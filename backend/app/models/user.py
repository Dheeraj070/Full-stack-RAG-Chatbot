from datetime import datetime
from app import mongo
from bson import ObjectId

class User:
    """User model for MongoDB"""
    
    collection = mongo.db.users
    
    @staticmethod
    def create(firebase_uid, email, display_name=None, role='student'):
        """Create a new user"""
        user_data = {
            'firebase_uid': firebase_uid,
            'email': email,
            'display_name': display_name or email.split('@')[0],
            'role': role,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'last_login': datetime.utcnow()
        }
        result = User.collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return user_data
    
    @staticmethod
    def find_by_firebase_uid(firebase_uid):
        """Find user by Firebase UID"""
        return User.collection.find_one({'firebase_uid': firebase_uid})
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.collection.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by MongoDB ID"""
        return User.collection.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def update_last_login(firebase_uid):
        """Update user's last login timestamp"""
        return User.collection.update_one(
            {'firebase_uid': firebase_uid},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    
    @staticmethod
    def get_all_users(skip=0, limit=50):
        """Get all users with pagination"""
        users = list(User.collection.find().skip(skip).limit(limit))
        total = User.collection.count_documents({})
        return users, total
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user information"""
        update_data['updated_at'] = datetime.utcnow()
        return User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def delete_user(user_id):
        """Soft delete user"""
        return User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def to_dict(user):
        """Convert user document to dictionary"""
        if not user:
            return None
        return {
            'id': str(user['_id']),
            'firebase_uid': user['firebase_uid'],
            'email': user['email'],
            'display_name': user['display_name'],
            'role': user['role'],
            'is_active': user.get('is_active', True),
            'created_at': user['created_at'].isoformat() + 'Z',
            'last_login': user.get('last_login', user['created_at']).isoformat() + 'Z'
        }