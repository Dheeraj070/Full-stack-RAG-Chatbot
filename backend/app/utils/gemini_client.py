import google.generativeai as genai
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """Google Gemini API client"""
    
    _model = None
    
    @classmethod
    def initialize(cls):
        """Initialize Gemini API"""
        if not cls._model:
            try:
                genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
                cls._model = genai.GenerativeModel(current_app.config['GEMINI_MODEL'])
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {str(e)}")
                raise
    
    @staticmethod
    def generate_response(prompt, context=None):
        """Generate response using Gemini API"""
        try:
            GeminiClient.initialize()
            
            # Build the full prompt with context
            full_prompt = ""
            
            if context:
                full_prompt += "Context from PDF document:\n"
                full_prompt += f"{context}\n\n"
            
            full_prompt += "You are an expert engineering assistant. "
            full_prompt += "Provide detailed, accurate, and helpful responses to engineering-related questions. "
            full_prompt += "If the question is based on a PDF context, use that information to provide specific answers.\n\n"
            full_prompt += f"Question: {prompt}\n\n"
            full_prompt += "Answer:"
            
            response = GeminiClient._model.generate_content(full_prompt)
            
            logger.info("Successfully generated response from Gemini API")
            return response.text
        
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response at the moment. Please try again."
    
    @staticmethod
    def generate_with_context(question, context_chunks):
        """Generate response with PDF context"""
        try:
            # Combine context chunks
            context = "\n\n".join([chunk['chunk'] for chunk in context_chunks[:3]])  # Top 3 chunks
            
            return GeminiClient.generate_response(question, context)
        
        except Exception as e:
            logger.error(f"Failed to generate response with context: {str(e)}")
            return "I apologize, but I'm having trouble processing the PDF context. Please try again."