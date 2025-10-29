"""
Initialize or rebuild FAISS index from existing MongoDB data
Run this script after setting up the database
"""

from app import create_app
from app.utils.faiss_store import faiss_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize FAISS from MongoDB"""
    app = create_app('development')
    
    with app.app_context():
        logger.info("Starting FAISS initialization...")
        
        # Check current state
        stats = faiss_store.get_stats()
        logger.info(f"Current FAISS stats: {stats}")
        
        # Rebuild from MongoDB
        logger.info("Rebuilding FAISS index from MongoDB...")
        success = faiss_store.rebuild_from_mongodb()
        
        if success:
            stats = faiss_store.get_stats()
            logger.info(f"FAISS index rebuilt successfully!")
            logger.info(f"New stats: {stats}")
        else:
            logger.error("Failed to rebuild FAISS index")

if __name__ == '__main__':
    main()