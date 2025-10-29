from datetime import datetime
from app import mongo
from bson import ObjectId
import numpy as np

class VectorStore:
    """Vector Store model for MongoDB"""
    
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
    def get_by_pdf(pdf_id):
        """Get all vectors for a PDF"""
        return list(VectorStore.collection.find({'pdf_id': ObjectId(pdf_id)}))
    
    @staticmethod
    def search_similar(query_embedding, pdf_id=None, top_k=5):
        """Search for similar vectors using cosine similarity"""
        query = {'pdf_id': ObjectId(pdf_id)} if pdf_id else {}
        vectors = list(VectorStore.collection.find(query))
        
        if not vectors:
            return []
        
        # Convert query embedding to numpy array
        query_vec = np.array(query_embedding)
        
        # Calculate cosine similarity for each vector
        similarities = []
        for vec in vectors:
            stored_vec = np.array(vec['embedding'])
            similarity = np.dot(query_vec, stored_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(stored_vec))
            similarities.append((vec, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [{'chunk': sim[0]['chunk_text'], 'similarity': float(sim[1]), 'metadata': sim[0].get('metadata', {})} 
                for sim in similarities[:top_k]]
    
    @staticmethod
    def delete_by_pdf(pdf_id):
        """Delete all vectors for a PDF"""
        return VectorStore.collection.delete_many({'pdf_id': ObjectId(pdf_id)})
    
    @staticmethod
    def get_all_vectors(skip=0, limit=50):
        """Get all vectors (admin only)"""
        vectors = list(VectorStore.collection.find().skip(skip).limit(limit))
        total = VectorStore.collection.count_documents({})
        return vectors, total
    
    @staticmethod
    def get_stats():
        """Get vectorstore statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': '$pdf_id',
                    'chunk_count': {'$sum': 1}
                }
            }
        ]
        stats = list(VectorStore.collection.aggregate(pipeline))
        return {
            'total_chunks': VectorStore.collection.count_documents({}),
            'total_pdfs': len(stats),
            'pdf_stats': stats
        }
    
    @staticmethod
    def to_dict(vector):
        """Convert vector document to dictionary"""
        if not vector:
            return None
        return {
            'id': str(vector['_id']),
            'pdf_id': str(vector['pdf_id']),
            'chunk_text': vector['chunk_text'][:200] + '...' if len(vector['chunk_text']) > 200 else vector['chunk_text'],
            'chunk_index': vector['chunk_index'],
            'created_at': vector['created_at'].isoformat()
        }