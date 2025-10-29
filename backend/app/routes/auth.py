from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.firebase_auth import FirebaseAuth
from app.utils.jwt_handler import JWTHandler
from app.utils.validators import Validators
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        display_name = data.get('display_name')
        role = data.get('role', 'student')
        
        # Validate email
        if not Validators.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, message = Validators.validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate role
        if not Validators.validate_role(role):
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create Firebase user
        firebase_user = FirebaseAuth.create_user(email, password, display_name)
        if not firebase_user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Create user in MongoDB
        user = User.create(
            firebase_uid=firebase_user.uid,
            email=email,
            display_name=display_name or firebase_user.display_name,
            role=role
        )
        
        # Generate JWT token
        user_dict = User.to_dict(user)
        token = JWTHandler.generate_token(user_dict)
        
        logger.info(f"User registered successfully: {email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user_dict
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with Firebase token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('firebase_token'):
            return jsonify({'error': 'Firebase token is required'}), 400
        
        firebase_token = data['firebase_token']
        
        # Verify Firebase token
        decoded_token = FirebaseAuth.verify_token(firebase_token)
        if not decoded_token:
            return jsonify({'error': 'Invalid Firebase token'}), 401
        
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        
        # Find or create user in MongoDB
        user = User.find_by_firebase_uid(firebase_uid)
        
        if not user:
            # Create new user
            display_name = decoded_token.get('name') or email.split('@')[0]
            user = User.create(
                firebase_uid=firebase_uid,
                email=email,
                display_name=display_name,
                role='student'  # Default role
            )
        else:
            # Update last login
            User.update_last_login(firebase_uid)
        
        # Generate JWT token
        user_dict = User.to_dict(user)
        token = JWTHandler.generate_token(user_dict)
        
        logger.info(f"User logged in successfully: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_dict
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verify JWT token"""
    try:
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = JWTHandler.decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        user = User.find_by_id(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'valid': True,
            'user': User.to_dict(user)
        }), 200
    
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': 'Token verification failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT token"""
    try:
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        new_token = JWTHandler.refresh_token(token)
        if not new_token:
            return jsonify({'error': 'Failed to refresh token'}), 401
        
        return jsonify({
            'token': new_token
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500