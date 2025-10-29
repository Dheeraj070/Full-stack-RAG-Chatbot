from app import create_app
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create app
logger.info("🚀 Starting Engineering Chatbot Backend...")
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"📍 Server starting on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"👤 Current user: Dheeraj070")
    logger.info(f"📅 Date: 2025-10-29 11:10:18 UTC")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )