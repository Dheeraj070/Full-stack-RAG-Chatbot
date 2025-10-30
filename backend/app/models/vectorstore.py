from app import mongo
from bson import ObjectId
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store model for embeddings"""
    collection = mongo.db.vectorstore

    @staticmethod
    def create(pdf_id, chunk_text, embedding, chunk_index, metadata=None):
        """Create a new vector entry"""
        vector_data = {
            'pdf_id': ObjectId(pdf_id),
            'chunk_text': chunk_text,
            'embedding': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
            'chunk_index': chunk_index,
            'metadata': metadata or {},
            'created_at': datetime.utcnow()
        }

        result = VectorStore.collection.insert_one(vector_data)
        vector_data['_id'] = result.inserted_id
        return vector_data

    @staticmethod
    def search_similar(query_embedding, pdf_id=None, top_k=5):
        """Search for similar vectors with optional PDF filtering"""
        query_vec = np.array(query_embedding)

        # Build query - if pdf_id is None, search all PDFs
        if pdf_id:
            query = {'pdf_id': ObjectId(pdf_id)} if isinstance(pdf_id, str) else {'pdf_id': pdf_id}
        else:
            query = {}

        vectors = list(VectorStore.collection.find(query))

        if not vectors:
            return []

        similarities = []
        for vec in vectors:
            stored_vec = np.array(vec['embedding'])
            similarity = np.dot(query_vec, stored_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(stored_vec)
            )
            similarities.append({
                'chunk': vec.get('chunk_text', ''),
                'similarity': float(similarity),
                'pdf_id': str(vec['pdf_id']),
                'chunk_index': vec.get('chunk_index')
            })

        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]

    @staticmethod
    def search_multiple_pdfs(query_embedding, pdf_ids, top_k_per_pdf=3):
        """
        Search across multiple PDFs and return top results from each

        Args:
            query_embedding: Query vector
            pdf_ids: List of PDF IDs to search
            top_k_per_pdf: Number of results per PDF

        Returns:
            List of results with PDF source information
        """
        all_results = []

        for pdf_id in pdf_ids:
            results = VectorStore.search_similar(query_embedding, pdf_id, top_k_per_pdf)
            for result in results:
                result['source_pdf_id'] = pdf_id
                all_results.append(result)

        # Sort all results by similarity
        all_results.sort(key=lambda x: x['similarity'], reverse=True)

        return all_results

    @staticmethod
    def get_by_pdf(pdf_id, skip=0, limit=50):
        """Get vectors by PDF ID"""
        vectors = list(VectorStore.collection.find(
            {'pdf_id': ObjectId(pdf_id)}
        ).skip(skip).limit(limit))

        return vectors

    @staticmethod
    def delete_by_pdf(pdf_id):
        """Delete all vectors for a PDF"""
        result = VectorStore.collection.delete_many({'pdf_id': ObjectId(pdf_id)})
        return result.deleted_count

    @staticmethod
    def get_all_vectors(skip=0, limit=50):
        """Get all vectors with pagination"""
        vectors = list(VectorStore.collection.find().skip(skip).limit(limit))
        total = VectorStore.collection.count_documents({})
        return vectors, total

    @staticmethod
    def to_dict(vector):
        """Convert vector document to dictionary"""
        return {
            'id': str(vector['_id']),
            'pdf_id': str(vector['pdf_id']),
            'chunk_text': vector.get('chunk_text', ''),
            'chunk_index': vector.get('chunk_index'),
            'metadata': vector.get('metadata', {}),
            'created_at': vector['created_at'].isoformat() + 'Z'
        }