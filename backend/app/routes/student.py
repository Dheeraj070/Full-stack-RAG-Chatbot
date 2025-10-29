from flask import Blueprint, request, jsonify, current_app
from app.models.pdf import PDFDocument
from app.models.vectorstore import VectorStore
from app.utils.pdf_processor import PDFProcessor
from app.utils.embeddings import EmbeddingGenerator
from app.utils.decorators import token_required
from app.utils.faiss_store import faiss_store
import logging
import numpy as np

logger = logging.getLogger(__name__)

student_bp = Blueprint('student', __name__)

@student_bp.route('/upload-pdf', methods=['POST'])
@token_required
def upload_pdf():
    """Upload and process a PDF document with FAISS integration"""
    try:
        user_id = request.current_user['user_id']
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not PDFProcessor.allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
        
        # Save file
        file_path, filename, file_size = PDFProcessor.save_file(file, current_app.config['UPLOAD_FOLDER'])
        
        # Extract text from PDF
        text_content, metadata = PDFProcessor.extract_text(file_path)
        
        # Create PDF document in database
        pdf = PDFDocument.create(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            text_content=text_content,
            metadata=metadata
        )
        
        pdf_id = str(pdf['_id'])
        
        # Process text into chunks
        chunks = PDFProcessor.chunk_text(text_content)
        
        # Generate embeddings for chunks
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = EmbeddingGenerator.generate_embeddings_batch(chunks)
        embeddings_array = np.array(embeddings)
        
        # Store embeddings in MongoDB (for backup and persistence)
        chunk_indices = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            VectorStore.create(
                pdf_id=pdf_id,
                chunk_text=chunk,
                embedding=embedding,
                chunk_index=idx,
                metadata={'page_range': f"Chunk {idx + 1}"}
            )
            chunk_indices.append(idx)
        
        # Add to FAISS for fast similarity search
        logger.info(f"Adding {len(chunks)} vectors to FAISS index...")
        success = faiss_store.add_vectors(
            pdf_id=pdf_id,
            embeddings=embeddings_array,
            chunks=chunks,
            chunk_indices=chunk_indices
        )
        
        if not success:
            logger.warning("Failed to add vectors to FAISS, but data is in MongoDB")
        
        logger.info(f"PDF uploaded and processed: {filename} ({len(chunks)} chunks)")
        
        # Get FAISS stats
        faiss_stats = faiss_store.get_stats()
        
        return jsonify({
            'message': 'PDF uploaded and processed successfully',
            'pdf': PDFDocument.to_dict(pdf),
            'chunks_created': len(chunks),
            'faiss_stats': faiss_stats
        }), 201
    
    except Exception as e:
        logger.error(f"Upload PDF error: {str(e)}")
        return jsonify({'error': 'Failed to upload PDF', 'details': str(e)}), 500

@student_bp.route('/pdfs', methods=['GET'])
@token_required
def get_pdfs():
    """Get user's uploaded PDFs"""
    try:
        user_id = request.current_user['user_id']
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        # Get PDFs
        pdfs, total = PDFDocument.get_by_user(user_id, skip=skip, limit=limit)
        
        return jsonify({
            'pdfs': [PDFDocument.to_dict(pdf) for pdf in pdfs],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Get PDFs error: {str(e)}")
        return jsonify({'error': 'Failed to get PDFs'}), 500

@student_bp.route('/pdf/<pdf_id>', methods=['DELETE'])
@token_required
def delete_pdf(pdf_id):
    """Delete a PDF document and its vectors from FAISS"""
    try:
        user_id = request.current_user['user_id']
        
        # Get PDF
        pdf = PDFDocument.get_by_id(pdf_id)
        if not pdf:
            return jsonify({'error': 'PDF not found'}), 404
        
        # Verify PDF belongs to user
        if str(pdf['user_id']) != user_id:
            return jsonify({'error': 'Unauthorized access to PDF'}), 403
        
        # Delete from MongoDB
        PDFDocument.delete_pdf(pdf_id)
        VectorStore.delete_by_pdf(pdf_id)
        
        # Remove from FAISS
        logger.info(f"Removing vectors from FAISS for PDF {pdf_id}")
        faiss_store.remove_pdf_vectors(pdf_id)
        
        logger.info(f"PDF {pdf_id} deleted")
        
        return jsonify({
            'message': 'PDF deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete PDF error: {str(e)}")
        return jsonify({'error': 'Failed to delete PDF'}), 500