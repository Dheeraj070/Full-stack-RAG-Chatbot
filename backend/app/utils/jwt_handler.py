import jwt
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class JWTHandler:
    """JWT token handler"""
    
    @staticmethod
    def generate_token(user_data):
        """Generate JWT token"""
        try:
            payload = {
                'user_id': user_data['id'],
                'firebase_uid': user_data['firebase_uid'],
                'email': user_data['email'],
                'role': user_data['role'],
                'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(
                payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm=current_app.config['JWT_ALGORITHM']
            )
            
            return token
        except Exception as e:
            logger.error(f"Failed to generate token: {str(e)}")
            return None
    
    @staticmethod
    def decode_token(token):
        """Decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return None
    
    @staticmethod
    def refresh_token(token):
        """Refresh JWT token"""
        payload = JWTHandler.decode_token(token)
        if payload:
            # Remove exp and iat from payload
            payload.pop('exp', None)
            payload.pop('iat', None)
            return JWTHandler.generate_token(payload)
        return None