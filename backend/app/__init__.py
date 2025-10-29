from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from app.config import config
import logging

mongo = PyMongo()

def create_app(config_name='default'):
    """Application factory with FAISS initialization"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    mongo.init_app(app)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Initialize FAISS Vector Store
    logger.info("🚀 Initializing FAISS Vector Store...")
    try:
        from app.utils.faiss_store import faiss_store
        with app.app_context():
            stats = faiss_store.get_stats()
            logger.info(f"✅ FAISS initialized with {stats['total_vectors']} vectors from {stats['total_pdfs']} PDFs")
            
            # If FAISS is empty but MongoDB has data, offer to rebuild
            if stats['total_vectors'] == 0:
                mongo_count = mongo.db.vectorstore.count_documents({})
                if mongo_count > 0:
                    logger.warning(f"⚠️  FAISS is empty but MongoDB has {mongo_count} vectors")
                    logger.warning("💡 Run 'python init_faiss_safe.py' to rebuild FAISS index")
    except Exception as e:
        logger.error(f"❌ FAISS initialization failed: {str(e)}")
        logger.warning("⚠️  Application will continue without FAISS (fallback to MongoDB search)")
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.student import student_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        try:
            from app.utils.faiss_store import faiss_store
            faiss_stats = faiss_store.get_stats()
            faiss_status = 'operational' if faiss_stats['total_vectors'] >= 0 else 'unavailable'
        except Exception:
            faiss_status = 'unavailable'
        
        return {
            'status': 'healthy',
            'message': 'Engineering Chatbot API is running',
            'faiss': faiss_status,
            'timestamp': '2025-10-29 11:10:18'
        }, 200
    
    return app