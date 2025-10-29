import firebase_admin
from firebase_admin import credentials, auth
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class FirebaseAuth:
    """Firebase Authentication handler"""
    
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if not cls._initialized:
            try:
                cred_path = current_app.config['FIREBASE_CREDENTIALS_PATH']
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                logger.info("Firebase Admin SDK initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
                raise
    
    @staticmethod
    def verify_token(id_token):
        """Verify Firebase ID token"""
        try:
            FirebaseAuth.initialize()
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None
    
    @staticmethod
    def get_user(uid):
        """Get user from Firebase"""
        try:
            FirebaseAuth.initialize()
            user = auth.get_user(uid)
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            return None
    
    @staticmethod
    def create_user(email, password, display_name=None):
        """Create a new Firebase user"""
        try:
            FirebaseAuth.initialize()
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return None
    
    @staticmethod
    def delete_user(uid):
        """Delete Firebase user"""
        try:
            FirebaseAuth.initialize()
            auth.delete_user(uid)
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            return False