from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.chat import Chat
from app.models.session import Session
from app.models.pdf import PDFDocument
from app.models.vectorstore import VectorStore
from app.utils.decorators import token_required, role_required
from app.utils.faiss_store import faiss_store
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def get_users():
    """Get all users"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        users, total = User.get_all_users(skip=skip, limit=limit)
        
        return jsonify({
            'users': [User.to_dict(user) for user in users],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': 'Failed to get users'}), 500

@admin_bp.route('/user/<user_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_user(user_id):
    """Update user information"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get user
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update user
        update_data = {}
        if 'display_name' in data:
            update_data['display_name'] = data['display_name']
        if 'role' in data:
            update_data['role'] = data['role']
        if 'is_active' in data:
            update_data['is_active'] = data['is_active']
        
        User.update_user(user_id, update_data)
        
        logger.info(f"User {user_id} updated by admin")
        
        return jsonify({
            'message': 'User updated successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return jsonify({'error': 'Failed to update user'}), 500

@admin_bp.route('/user/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        User.delete_user(user_id)
        
        logger.info(f"User {user_id} deleted by admin")
        
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({'error': 'Failed to delete user'}), 500

# ==================== SESSION MANAGEMENT ====================

@admin_bp.route('/sessions', methods=['GET'])
@token_required
@role_required('admin')
def get_sessions():
    """Get all sessions"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        sessions, total = Session.get_all_sessions(skip=skip, limit=limit)
        
        return jsonify({
            'sessions': [Session.to_dict(session) for session in sessions],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        return jsonify({'error': 'Failed to get sessions'}), 500

@admin_bp.route('/session/<session_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_session(session_id):
    """Delete session"""
    try:
        session = Session.get_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        Session.delete_session(session_id)
        Chat.delete_by_session(session_id)
        
        logger.info(f"Session {session_id} deleted by admin")
        
        return jsonify({
            'message': 'Session deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}")
        return jsonify({'error': 'Failed to delete session'}), 500

# ==================== CHAT MANAGEMENT ====================

@admin_bp.route('/chats', methods=['GET'])
@token_required
@role_required('admin')
def get_chats():
    """Get all chats"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        chats, total = Chat.get_all_chats(skip=skip, limit=limit)
        
        return jsonify({
            'chats': [Chat.to_dict(chat) for chat in chats],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get chats error: {str(e)}")
        return jsonify({'error': 'Failed to get chats'}), 500

@admin_bp.route('/chat/<chat_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_chat(chat_id):
    """Delete chat"""
    try:
        Chat.delete_chat(chat_id)
        
        logger.info(f"Chat {chat_id} deleted by admin")
        
        return jsonify({
            'message': 'Chat deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete chat error: {str(e)}")
        return jsonify({'error': 'Failed to delete chat'}), 500

# ==================== PDF MANAGEMENT ====================

@admin_bp.route('/pdfs', methods=['GET'])
@token_required
@role_required('admin')
def get_pdfs():
    """Get all PDFs"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        pdfs, total = PDFDocument.get_all_pdfs(skip=skip, limit=limit)
        
        return jsonify({
            'pdfs': [PDFDocument.to_dict(pdf) for pdf in pdfs],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get PDFs error: {str(e)}")
        return jsonify({'error': 'Failed to get PDFs'}), 500

@admin_bp.route('/pdf/<pdf_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_pdf(pdf_id):
    """Delete PDF and its vectors from FAISS"""
    try:
        pdf = PDFDocument.get_by_id(pdf_id)
        if not pdf:
            return jsonify({'error': 'PDF not found'}), 404
        
        # Delete from MongoDB
        PDFDocument.delete_pdf(pdf_id)
        VectorStore.delete_by_pdf(pdf_id)
        
        # Remove from FAISS
        logger.info(f"Removing vectors from FAISS for PDF {pdf_id}")
        faiss_store.remove_pdf_vectors(pdf_id)
        
        logger.info(f"PDF {pdf_id} deleted by admin")
        
        return jsonify({
            'message': 'PDF deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete PDF error: {str(e)}")
        return jsonify({'error': 'Failed to delete PDF'}), 500

# ==================== VECTOR STORE MANAGEMENT ====================

@admin_bp.route('/vectorstore', methods=['GET'])
@token_required
@role_required('admin')
def get_vectorstore():
    """Get vector store data"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        vectors, total = VectorStore.get_all_vectors(skip=skip, limit=limit)
        
        return jsonify({
            'vectors': [VectorStore.to_dict(vector) for vector in vectors],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get vectorstore error: {str(e)}")
        return jsonify({'error': 'Failed to get vectorstore data'}), 500

@admin_bp.route('/vectorstore/stats', methods=['GET'])
@token_required
@role_required('admin')
def get_vectorstore_stats():
    """Get detailed vector store statistics including FAISS"""
    try:
        from app import mongo
        
        # Get MongoDB stats
        mongo_vectors = mongo.db.vectorstore.count_documents({})
        
        # Get FAISS stats
        faiss_stats = faiss_store.get_stats()
        
        # Get per-PDF stats
        pipeline = [
            {
                '$group': {
                    '_id': '$pdf_id',
                    'chunk_count': {'$sum': 1}
                }
            }
        ]
        pdf_stats = list(mongo.db.vectorstore.aggregate(pipeline))
        
        return jsonify({
            'mongodb': {
                'total_vectors': mongo_vectors,
                'pdfs': len(pdf_stats)
            },
            'faiss': faiss_stats,
            'per_pdf': [
                {
                    'pdf_id': str(stat['_id']),
                    'chunks': stat['chunk_count']
                }
                for stat in pdf_stats
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Get vectorstore stats error: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@admin_bp.route('/vectorstore/rebuild', methods=['POST'])
@token_required
@role_required('admin')
def rebuild_faiss_index():
    """Rebuild FAISS index from MongoDB (admin only)"""
    try:
        logger.info("Starting FAISS index rebuild from MongoDB...")
        
        success = faiss_store.rebuild_from_mongodb()
        
        if success:
            stats = faiss_store.get_stats()
            return jsonify({
                'message': 'FAISS index rebuilt successfully',
                'stats': stats
            }), 200
        else:
            return jsonify({'error': 'Failed to rebuild FAISS index'}), 500
    
    except Exception as e:
        logger.error(f"Rebuild FAISS index error: {str(e)}")
        return jsonify({'error': 'Failed to rebuild FAISS index', 'details': str(e)}), 500

# ==================== SYSTEM STATISTICS ====================

@admin_bp.route('/stats', methods=['GET'])
@token_required
@role_required('admin')
def get_stats():
    """Get system statistics including FAISS"""
    try:
        from app import mongo
        
        total_users = mongo.db.users.count_documents({})
        total_sessions = mongo.db.sessions.count_documents({})
        total_chats = mongo.db.chats.count_documents({})
        total_pdfs = mongo.db.pdf_documents.count_documents({'is_active': True})
        total_vectors = mongo.db.vectorstore.count_documents({})
        
        # Get FAISS stats
        faiss_stats = faiss_store.get_stats()
        
        return jsonify({
            'total_users': total_users,
            'total_sessions': total_sessions,
            'total_chats': total_chats,
            'total_pdfs': total_pdfs,
            'total_vectors': total_vectors,
            'faiss': faiss_stats
        }), 200
    
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500