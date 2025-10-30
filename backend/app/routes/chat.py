from flask import Blueprint, request, jsonify
from app.models.chat import Chat
from app.models.session import Session
from app.models.pdf import PDFDocument
from app.models.vectorstore import VectorStore
from app.utils.gemini_client import GeminiClient
from app.utils.embeddings import EmbeddingGenerator
from app.utils.validators import Validators
from app.utils.decorators import token_required
from app.utils.faiss_store import faiss_store
import logging
import numpy as np

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

def search_with_faiss_fallback(query_embedding, pdf_ids, top_k_per_pdf=3):
    """
    Search using FAISS with automatic fallback to MongoDB
    Supports multiple PDFs
    
    Args:
        query_embedding: Query vector
        pdf_ids: Single PDF ID (string) or list of PDF IDs
        top_k_per_pdf: Number of results per PDF
    
    Returns:
        List of similar chunks with source information
    """
    try:
        # Normalize pdf_ids to list
        if isinstance(pdf_ids, str):
            pdf_ids = [pdf_ids]
        
        # Try FAISS first (fast)
        logger.info(f"🔍 Searching with FAISS across {len(pdf_ids)} PDFs...")
        
        if len(pdf_ids) == 1:
            # Single PDF search
            faiss_results = faiss_store.search(
                query_embedding=query_embedding,
                pdf_id=pdf_ids[0],
                top_k=top_k_per_pdf * 2  # Get more results for single PDF
            )
        else:
            # Multiple PDF search
            faiss_results = faiss_store.search_multiple_pdfs(
                query_embedding=query_embedding,
                pdf_ids=pdf_ids,
                top_k_per_pdf=top_k_per_pdf
            )
        
        if faiss_results:
            logger.info(f"✅ FAISS found {len(faiss_results)} results")
            return [{
                'chunk': result['chunk_text'],
                'similarity': result['similarity'],
                'chunk_index': result['chunk_index'],
                'pdf_id': result.get('source_pdf_id', result.get('pdf_id'))
            } for result in faiss_results]
    
    except Exception as e:
        logger.warning(f"⚠️  FAISS search failed: {str(e)}, falling back to MongoDB")
    
    # Fallback to MongoDB (slower but reliable)
    logger.info("🔍 Falling back to MongoDB search...")
    try:
        if len(pdf_ids) == 1:
            similar_chunks = VectorStore.search_similar(query_embedding, pdf_id=pdf_ids[0], top_k=top_k_per_pdf * 2)
        else:
            similar_chunks = VectorStore.search_multiple_pdfs(query_embedding, pdf_ids, top_k_per_pdf)
        
        logger.info(f"✅ MongoDB found {len(similar_chunks)} results")
        return similar_chunks
    except Exception as e:
        logger.error(f"❌ MongoDB search also failed: {str(e)}")
        return []

@chat_bp.route('/send', methods=['POST'])
@token_required
def send_message():
    """Send a chat message with support for multiple PDFs"""
    try:
        data = request.get_json()
        user_id = request.current_user['user_id']
        
        # Validate required fields
        if not data or not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        message = Validators.sanitize_input(data['message'])
        session_id = data.get('session_id')
        
        # Support both single pdf_id and multiple pdf_ids
        pdf_id = data.get('pdf_id')  # Single PDF (backward compatible)
        pdf_ids = data.get('pdf_ids', [])  # Multiple PDFs (new)
        
        # Normalize to list
        if pdf_id and not pdf_ids:
            pdf_ids = [pdf_id]
        elif not pdf_ids:
            pdf_ids = []
        
        # Create or get session
        if not session_id:
            session = Session.create(user_id)
            session_id = str(session['_id'])
        else:
            session = Session.get_by_id(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404
            
            # Verify session belongs to user (unless admin)
            if str(session['user_id']) != user_id and request.current_user['role'] != 'admin':
                return jsonify({'error': 'Unauthorized access to session'}), 403
        
        # Generate response
        context_type = 'direct'
        response_text = None
        similar_chunks = []
        search_method = 'none'
        pdf_sources = []
        
        if pdf_ids:
            # PDF-assisted chat with multiple PDFs
            context_type = 'pdf_multiple' if len(pdf_ids) > 1 else 'pdf'
            
            # Verify all PDFs belong to user (unless admin)
            for pid in pdf_ids:
                pdf = PDFDocument.get_by_id(pid)
                if not pdf:
                    return jsonify({'error': f'PDF {pid} not found'}), 404
                
                if str(pdf['user_id']) != user_id and request.current_user['role'] != 'admin':
                    return jsonify({'error': f'Unauthorized access to PDF {pid}'}), 403
                
                pdf_sources.append({
                    'id': pid,
                    'filename': pdf['filename']
                })
            
            # Generate query embedding
            logger.info("Generating query embedding...")
            query_embedding = EmbeddingGenerator.generate_embedding(message)
            
            # Search with FAISS and automatic fallback to MongoDB
            logger.info(f"🔍 Searching across {len(pdf_ids)} PDF(s)...")
            similar_chunks = search_with_faiss_fallback(query_embedding, pdf_ids, top_k_per_pdf=3)
            search_method = 'faiss' if similar_chunks else 'mongodb'
            
            logger.info(f"Found {len(similar_chunks)} similar chunks using {search_method}")
            
            # Generate response with context
            if similar_chunks:
                # Group chunks by PDF for better context
                chunks_by_pdf = {}
                for chunk in similar_chunks[:9]:  # Top 9 chunks across all PDFs
                    pdf_id_source = chunk.get('pdf_id', chunk.get('source_pdf_id'))
                    if pdf_id_source not in chunks_by_pdf:
                        chunks_by_pdf[pdf_id_source] = []
                    chunks_by_pdf[pdf_id_source].append(chunk)
                
                # Format context with PDF sources
                context_parts = []
                for pdf_id_source, chunks in chunks_by_pdf.items():
                    pdf_info = next((p for p in pdf_sources if p['id'] == pdf_id_source), None)
                    pdf_name = pdf_info['filename'] if pdf_info else 'Unknown PDF'
                    
                    context_parts.append(f"\n--- From {pdf_name} ---")
                    for chunk in chunks:
                        context_parts.append(chunk['chunk'])
                
                response_text = GeminiClient.generate_with_context(
                    message, 
                    similar_chunks[:9],
                    pdf_sources=pdf_sources
                )
            else:
                response_text = "I couldn't find relevant information in the selected PDF(s). Please try rephrasing your question."
        else:
            # Direct chat
            response_text = GeminiClient.generate_response(message)
        
        # Save chat to database
        chat = Chat.create(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response_text,
            context_type=context_type,
            pdf_id=pdf_ids[0] if len(pdf_ids) == 1 else None,  # Store first PDF for backward compatibility
            metadata={
                'similar_chunks_count': len(similar_chunks),
                'search_method': search_method,
                'pdf_ids': pdf_ids,
                'pdf_sources': pdf_sources
            }
        )
        
        # Update session
        Session.increment_message_count(session_id)
        
        logger.info(f"Chat message processed for user {user_id} (method: {search_method}, PDFs: {len(pdf_ids)})")
        
        return jsonify({
            'message': 'Message sent successfully',
            'chat': Chat.to_dict(chat),
            'session_id': session_id,
            'similar_chunks_count': len(similar_chunks),
            'search_method': search_method,
            'pdf_sources': pdf_sources
        }), 200
    
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500

@chat_bp.route('/history/<session_id>', methods=['GET'])
@token_required
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        user_id = request.current_user['user_id']
        
        # Get session
        session = Session.get_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Verify session belongs to user (unless admin)
        if str(session['user_id']) != user_id and request.current_user['role'] != 'admin':
            return jsonify({'error': 'Unauthorized access to session'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        # Get chats
        chats = Chat.get_by_session(session_id, skip=skip, limit=limit)
        
        return jsonify({
            'session': Session.to_dict(session),
            'chats': [Chat.to_dict(chat) for chat in chats],
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get chat history error: {str(e)}")
        return jsonify({'error': 'Failed to get chat history'}), 500

@chat_bp.route('/sessions', methods=['GET'])
@token_required
def get_sessions():
    """Get user's chat sessions"""
    try:
        user_id = request.current_user['user_id']
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        # Get sessions
        sessions, total = Session.get_by_user(user_id, skip=skip, limit=limit)
        
        return jsonify({
            'sessions': [Session.to_dict(session) for session in sessions],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        return jsonify({'error': 'Failed to get sessions'}), 500

@chat_bp.route('/session', methods=['POST'])
@token_required
def create_session():
    """Create a new chat session"""
    try:
        data = request.get_json()
        user_id = request.current_user['user_id']
        
        session_name = data.get('session_name') if data else None
        
        # Create session
        session = Session.create(user_id, session_name)
        
        logger.info(f"Session created for user {user_id}")
        
        return jsonify({
            'message': 'Session created successfully',
            'session': Session.to_dict(session)
        }), 201
    
    except Exception as e:
        logger.error(f"Create session error: {str(e)}")
        return jsonify({'error': 'Failed to create session'}), 500

@chat_bp.route('/session/<session_id>', methods=['DELETE'])
@token_required
def delete_session(session_id):
    """Delete a chat session"""
    try:
        user_id = request.current_user['user_id']
        
        # Get session
        session = Session.get_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Verify session belongs to user (unless admin)
        if str(session['user_id']) != user_id and request.current_user['role'] != 'admin':
            return jsonify({'error': 'Unauthorized access to session'}), 403
        
        # Delete session and associated chats
        Session.delete_session(session_id)
        Chat.delete_by_session(session_id)
        
        logger.info(f"Session {session_id} deleted")
        
        return jsonify({
            'message': 'Session deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}")
        return jsonify({'error': 'Failed to delete session'}), 500