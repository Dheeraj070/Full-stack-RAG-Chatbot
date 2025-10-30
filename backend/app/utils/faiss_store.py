import faiss
import numpy as np
import pickle
import os
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """
    FAISS-based vector store for efficient similarity search
    Singleton pattern to ensure single instance across application
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize FAISS index and load existing data"""
        if self._initialized:
            return
        
        self.dimension = 384  # all-MiniLM-L6-v2 embedding dimension
        self.index = None
        self.id_map = {}  # Maps FAISS index position to metadata
        self.pdf_vector_map = {}  # Maps pdf_id to list of FAISS indices
        self.index_path = 'faiss_data'
        
        # Create directory if it doesn't exist
        Path(self.index_path).mkdir(exist_ok=True)
        
        # Initialize or load index
        self.initialize_index()
        self._initialized = True
        
        logger.info(f"FAISS Vector Store initialized with {self.index.ntotal} vectors")
    
    def initialize_index(self):
        """Initialize FAISS index or load from disk"""
        index_file = os.path.join(self.index_path, 'index.faiss')
        id_map_file = os.path.join(self.index_path, 'id_map.pkl')
        pdf_map_file = os.path.join(self.index_path, 'pdf_vector_map.pkl')
        
        if os.path.exists(index_file) and os.path.exists(id_map_file):
            try:
                # Load existing index
                self.index = faiss.read_index(index_file)
                
                with open(id_map_file, 'rb') as f:
                    self.id_map = pickle.load(f)
                
                if os.path.exists(pdf_map_file):
                    with open(pdf_map_file, 'rb') as f:
                        self.pdf_vector_map = pickle.load(f)
                
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Error loading FAISS index: {str(e)}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        # Using IndexFlatIP for Inner Product (cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {}
        self.pdf_vector_map = {}
        logger.info("Created new FAISS index")
    
    def add_vectors(
        self, 
        pdf_id: str, 
        embeddings: np.ndarray, 
        chunks: List[str], 
        chunk_indices: List[int]
    ) -> bool:
        """
        Add vectors to FAISS index
        
        Args:
            pdf_id: PDF document ID
            embeddings: Numpy array of embeddings (shape: [n, 384])
            chunks: List of text chunks
            chunk_indices: List of chunk indices
        
        Returns:
            bool: Success status
        """
        try:
            if not isinstance(embeddings, np.ndarray):
                embeddings = np.array(embeddings)
            
            embeddings = embeddings.astype('float32')
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Get starting index
            start_idx = self.index.ntotal
            
            # Add vectors to index
            self.index.add(embeddings)
            
            # Track vector indices for this PDF
            if pdf_id not in self.pdf_vector_map:
                self.pdf_vector_map[pdf_id] = []
            
            # Update metadata maps
            for i, (chunk, chunk_idx) in enumerate(zip(chunks, chunk_indices)):
                faiss_idx = start_idx + i
                
                self.id_map[faiss_idx] = {
                    'pdf_id': pdf_id,
                    'chunk_text': chunk,
                    'chunk_index': chunk_idx
                }
                
                self.pdf_vector_map[pdf_id].append(faiss_idx)
            
            # Save to disk
            self.save_index()
            
            logger.info(f"Added {len(embeddings)} vectors for PDF {pdf_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding vectors to FAISS: {str(e)}")
            return False
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        pdf_id: Optional[str] = None, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector (384-dim)
            pdf_id: Optional PDF ID to filter results
            top_k: Number of results to return
        
        Returns:
            List of dictionaries with similarity results
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("FAISS index is empty")
                return []
            
            # Prepare query
            if not isinstance(query_embedding, np.ndarray):
                query_embedding = np.array(query_embedding)
            
            query = query_embedding.reshape(1, -1).astype('float32')
            faiss.normalize_L2(query)
            
            # If filtering by PDF, search more and filter later
            search_k = top_k * 10 if pdf_id else top_k
            search_k = min(search_k, self.index.ntotal)
            
            # Perform search
            similarities, indices = self.index.search(query, search_k)
            
            # Collect results
            results = []
            for score, idx in zip(similarities[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                if idx in self.id_map:
                    metadata = self.id_map[idx]
                    
                    # Filter by PDF if specified
                    if pdf_id and metadata['pdf_id'] != pdf_id:
                        continue
                    
                    results.append({
                        'faiss_id': int(idx),
                        'similarity': float(score),
                        'pdf_id': metadata['pdf_id'],
                        'chunk_text': metadata['chunk_text'],
                        'chunk_index': metadata['chunk_index']
                    })
                    
                    # Stop if we have enough results
                    if len(results) >= top_k:
                        break
            
            logger.info(f"Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAISS index: {str(e)}")
            return []
    
    def remove_pdf_vectors(self, pdf_id: str) -> bool:
        """
        Remove all vectors for a specific PDF
        Note: FAISS doesn't support deletion, so we rebuild the index
        
        Args:
            pdf_id: PDF document ID
        
        Returns:
            bool: Success status
        """
        try:
            if pdf_id not in self.pdf_vector_map:
                logger.warning(f"PDF {pdf_id} not found in vector store")
                return True
            
            # Get indices to remove
            indices_to_remove = set(self.pdf_vector_map[pdf_id])
            
            if not indices_to_remove:
                return True
            
            # Rebuild index without deleted vectors
            vectors_to_keep = []
            new_id_map = {}
            new_pdf_vector_map = {}
            
            for idx in range(self.index.ntotal):
                if idx not in indices_to_remove and idx in self.id_map:
                    # Get vector from index
                    vector = self.index.reconstruct(int(idx))
                    vectors_to_keep.append(vector)
                    
                    # Update maps with new index
                    new_idx = len(vectors_to_keep) - 1
                    metadata = self.id_map[idx]
                    new_id_map[new_idx] = metadata
                    
                    # Update PDF vector map
                    current_pdf_id = metadata['pdf_id']
                    if current_pdf_id not in new_pdf_vector_map:
                        new_pdf_vector_map[current_pdf_id] = []
                    new_pdf_vector_map[current_pdf_id].append(new_idx)
            
            # Create new index
            self._create_new_index()
            
            if vectors_to_keep:
                vectors_array = np.array(vectors_to_keep).astype('float32')
                self.index.add(vectors_array)
            
            self.id_map = new_id_map
            self.pdf_vector_map = new_pdf_vector_map
            
            # Save updated index
            self.save_index()
            
            logger.info(f"Removed {len(indices_to_remove)} vectors for PDF {pdf_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing PDF vectors: {str(e)}")
            return False
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            index_file = os.path.join(self.index_path, 'index.faiss')
            id_map_file = os.path.join(self.index_path, 'id_map.pkl')
            pdf_map_file = os.path.join(self.index_path, 'pdf_vector_map.pkl')
            
            # Save FAISS index
            faiss.write_index(self.index, index_file)
            
            # Save metadata
            with open(id_map_file, 'wb') as f:
                pickle.dump(self.id_map, f)
            
            with open(pdf_map_file, 'wb') as f:
                pickle.dump(self.pdf_vector_map, f)
            
            logger.info("FAISS index and metadata saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'total_pdfs': len(self.pdf_vector_map),
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else None
        }
    
    def rebuild_from_mongodb(self):
        """
        Rebuild FAISS index from MongoDB data
        Useful for recovery or migration
        """
        try:
            from app import mongo
            from app.models.vectorstore import VectorStore
            
            logger.info("Rebuilding FAISS index from MongoDB...")
            
            # Clear current index
            self._create_new_index()
            
            # Group vectors by PDF
            pipeline = [
                {
                    '$group': {
                        '_id': '$pdf_id',
                        'vectors': {'$push': '$$ROOT'}
                    }
                }
            ]
            
            pdf_groups = list(VectorStore.collection.aggregate(pipeline))
            
            for group in pdf_groups:
                pdf_id = str(group['_id'])
                vectors_data = group['vectors']
                
                embeddings = []
                chunks = []
                chunk_indices = []
                
                for vec in vectors_data:
                    embeddings.append(vec['embedding'])
                    chunks.append(vec['chunk_text'])
                    chunk_indices.append(vec['chunk_index'])
                
                embeddings_array = np.array(embeddings)
                self.add_vectors(pdf_id, embeddings_array, chunks, chunk_indices)
            
            logger.info(f"Rebuilt FAISS index with {self.index.ntotal} vectors from {len(pdf_groups)} PDFs")
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding FAISS index: {str(e)}")
            return False

    def search_multiple_pdfs(
        self, 
        query_embedding: np.ndarray, 
        pdf_ids: List[str], 
        top_k_per_pdf: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search across multiple PDFs
        
        Args:
            query_embedding: Query vector
            pdf_ids: List of PDF IDs to search
            top_k_per_pdf: Results per PDF
        
        Returns:
            Combined and ranked results from all PDFs
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("⚠️  FAISS index is empty")
                return []
            all_results = []
            # Search each PDF individually
            for pdf_id in pdf_ids:
                results = self.search(query_embedding, pdf_id, top_k_per_pdf)
                for result in results:
                    result['source_pdf_id'] = pdf_id
                    all_results.append(result)
            
            # Sort by similarity across all PDFs
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"✅ Found {len(all_results)} results across {len(pdf_ids)} PDFs")
            return all_results
            
        except Exception as e:
            logger.error(f"❌ Error searching multiple PDFs: {str(e)}")
            return []

# Singleton instance
faiss_store = FAISSVectorStore()