import google.generativeai as genai
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """Google Gemini API client"""
    
    _model = None
    
    @classmethod
    def get_model(cls):
        """Get or create Gemini model"""
        if cls._model is None:
            try:
                genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
                cls._model = genai.GenerativeModel(current_app.config.get('GEMINI_MODEL', 'gemini-pro'))
                logger.info("✅ Gemini model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
                raise
        return cls._model
    
    @staticmethod
    def generate_response(prompt):
        """Generate response for direct chat"""
        try:
            model = GeminiClient.get_model()
            
            system_prompt = """You are an expert engineering assistant. Provide clear, accurate, 
            and detailed explanations for engineering concepts, problems, and questions. 
            Use examples and step-by-step explanations when appropriate."""
            
            full_prompt = f"{system_prompt}\n\nQuestion: {prompt}\n\nAnswer:"
            
            response = model.generate_content(full_prompt)
            
            if not response or not response.text:
                return "I apologize, but I couldn't generate a response. Please try again."
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Gemini API error: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
    
    @staticmethod
    def generate_with_context(question, similar_chunks, pdf_sources=None):
        """
        Generate response with context from multiple PDFs
        
        Args:
            question: User's question
            similar_chunks: List of similar text chunks with PDF sources
            pdf_sources: List of PDF metadata (id, filename)
        """
        try:
            model = GeminiClient.get_model()
            
            # Build context with PDF source information
            context_parts = []
            
            if pdf_sources and len(pdf_sources) > 1:
                context_parts.append("I found relevant information from multiple documents:")
                context_parts.append("")
            
            # Group chunks by PDF
            chunks_by_pdf = {}
            for chunk in similar_chunks:
                pdf_id = chunk.get('pdf_id', chunk.get('source_pdf_id', 'unknown'))
                if pdf_id not in chunks_by_pdf:
                    chunks_by_pdf[pdf_id] = []
                chunks_by_pdf[pdf_id].append(chunk['chunk'])
            
            # Format context with clear PDF attribution
            for pdf_id, chunks in chunks_by_pdf.items():
                if pdf_sources:
                    pdf_info = next((p for p in pdf_sources if p['id'] == pdf_id), None)
                    if pdf_info:
                        context_parts.append(f"📄 From '{pdf_info['filename']}':")
                
                for i, chunk in enumerate(chunks, 1):
                    context_parts.append(f"{chunk}")
                    if i < len(chunks):
                        context_parts.append("")
                
                context_parts.append("")
            
            context = "\n".join(context_parts)
            
            # Create prompt
            if pdf_sources and len(pdf_sources) > 1:
                system_prompt = f"""You are an expert engineering assistant analyzing multiple documents.

Context from {len(pdf_sources)} documents:
{context}

Instructions:
1. Answer the question based on the provided context from multiple documents
2. When referencing information, mention which document it came from
3. If information conflicts between documents, acknowledge both perspectives
4. If the context doesn't contain enough information, say so clearly
5. Provide clear, detailed explanations with examples when appropriate
6. Synthesize information across documents when relevant

Question: {question}

Provide a comprehensive answer:"""
            else:
                system_prompt = f"""You are an expert engineering assistant analyzing a technical document.

Context from the document:
{context}

Instructions:
1. Answer the question based ONLY on the provided context
2. Provide clear, detailed explanations
3. If the context doesn't contain the answer, say so clearly
4. Use examples from the context when available

Question: {question}

Answer:"""
            
            response = model.generate_content(system_prompt)
            
            if not response or not response.text:
                return "I apologize, but I couldn't generate a response based on the provided context. Please try rephrasing your question."
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Gemini API error with context: {str(e)}")
            return "I apologize, but I'm having trouble analyzing the document(s) right now. Please try again later."