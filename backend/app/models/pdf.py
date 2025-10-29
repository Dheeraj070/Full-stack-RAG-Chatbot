from datetime import datetime
from app import mongo
from bson import ObjectId

class PDFDocument:
    """PDF Document model for MongoDB"""
    
    collection = mongo.db.pdf_documents
    
    @staticmethod
    def create(user_id, filename, file_path, file_size, text_content, metadata=None):
        """Create a new PDF document entry"""
        pdf_data = {
            'user_id': ObjectId(user_id),
            'filename': filename,
            'file_path': file_path,
            'file_size': file_size,
            'text_content': text_content,
            'page_count': metadata.get('page_count', 0) if metadata else 0,
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
            'is_active': True,
            'processed': True
        }
        result = PDFDocument.collection.insert_one(pdf_data)
        pdf_data['_id'] = result.inserted_id
        return pdf_data
    
    @staticmethod
    def get_by_id(pdf_id):
        """Get PDF by ID"""
        return PDFDocument.collection.find_one({'_id': ObjectId(pdf_id)})
    
    @staticmethod
    def get_by_user(user_id, skip=0, limit=50):
        """Get PDFs by user ID"""
        pdfs = list(PDFDocument.collection.find(
            {'user_id': ObjectId(user_id), 'is_active': True}
        ).sort('created_at', -1).skip(skip).limit(limit))
        total = PDFDocument.collection.count_documents({'user_id': ObjectId(user_id), 'is_active': True})
        return pdfs, total
    
    @staticmethod
    def get_all_pdfs(skip=0, limit=50):
        """Get all PDFs (admin only)"""
        pdfs = list(PDFDocument.collection.find({'is_active': True}).sort('created_at', -1).skip(skip).limit(limit))
        total = PDFDocument.collection.count_documents({'is_active': True})
        return pdfs, total
    
    @staticmethod
    def delete_pdf(pdf_id):
        """Soft delete PDF"""
        return PDFDocument.collection.update_one(
            {'_id': ObjectId(pdf_id)},
            {'$set': {'is_active': False}}
        )
    
    @staticmethod
    def to_dict(pdf, include_content=False):
        """Convert PDF document to dictionary"""
        if not pdf:
            return None
        result = {
            'id': str(pdf['_id']),
            'user_id': str(pdf['user_id']),
            'filename': pdf['filename'],
            'file_size': pdf['file_size'],
            'page_count': pdf.get('page_count', 0),
            'processed': pdf.get('processed', False),
            'created_at': pdf['created_at'].isoformat()
        }
        if include_content:
            result['text_content'] = pdf.get('text_content', '')
        return result