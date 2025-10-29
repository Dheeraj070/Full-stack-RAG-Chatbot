from sentence_transformers import SentenceTransformer
from flask import current_app
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Embedding generation utility"""
    
    _model = None
    
    @classmethod
    def initialize(cls):
        """Initialize embedding model"""
        if not cls._model:
            try:
                model_name = current_app.config['EMBEDDING_MODEL']
                cls._model = SentenceTransformer(model_name)
                logger.info(f"Embedding model initialized: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize embedding model: {str(e)}")
                raise
    
    @staticmethod
    def generate_embedding(text):
        """Generate embedding for text"""
        try:
            EmbeddingGenerator.initialize()
            embedding = EmbeddingGenerator._model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise
    
    @staticmethod
    def generate_embeddings_batch(texts):
        """Generate embeddings for multiple texts"""
        try:
            EmbeddingGenerator.initialize()
            embeddings = EmbeddingGenerator._model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise