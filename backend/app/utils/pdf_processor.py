import PyPDF2
import os
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF processing utility"""
    
    @staticmethod
    def extract_text(file_path):
        """Extract text from PDF file"""
        try:
            text_content = []
            page_count = 0
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            full_text = '\n\n'.join(text_content)
            
            metadata = {
                'page_count': page_count,
                'character_count': len(full_text),
                'word_count': len(full_text.split())
            }
            
            logger.info(f"Successfully extracted text from PDF: {page_count} pages")
            return full_text, metadata
        
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise
    
    @staticmethod
    def chunk_text(text, chunk_size=1000, overlap=200):
        """Split text into chunks with overlap"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def save_file(file, upload_folder):
        """Save uploaded file"""
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            
            # Add timestamp if file exists
            if os.path.exists(file_path):
                name, ext = os.path.splitext(filename)
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{name}_{timestamp}{ext}"
                file_path = os.path.join(upload_folder, filename)
            
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            logger.info(f"Saved file: {filename} ({file_size} bytes)")
            return file_path, filename, file_size
        
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise
    
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions