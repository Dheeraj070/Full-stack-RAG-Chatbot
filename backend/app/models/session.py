from datetime import datetime
from app import mongo
from bson import ObjectId

class Session:
    """Session model for MongoDB"""
    
    collection = mongo.db.sessions
    
    @staticmethod
    def create(user_id, session_name=None):
        """Create a new session"""
        session_data = {
            'user_id': ObjectId(user_id),
            'session_name': session_name or f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'message_count': 0
        }
        result = Session.collection.insert_one(session_data)
        session_data['_id'] = result.inserted_id
        return session_data
    
    @staticmethod
    def get_by_id(session_id):
        """Get session by ID"""
        return Session.collection.find_one({'_id': ObjectId(session_id)})
    
    @staticmethod
    def get_by_user(user_id, skip=0, limit=50):
        """Get sessions by user ID"""
        sessions = list(Session.collection.find(
            {'user_id': ObjectId(user_id), 'is_active': True}
        ).sort('updated_at', -1).skip(skip).limit(limit))
        total = Session.collection.count_documents({'user_id': ObjectId(user_id), 'is_active': True})
        return sessions, total
    
    @staticmethod
    def get_all_sessions(skip=0, limit=50):
        """Get all sessions (admin only)"""
        sessions = list(Session.collection.find().sort('updated_at', -1).skip(skip).limit(limit))
        total = Session.collection.count_documents({})
        return sessions, total
    
    @staticmethod
    def update_session(session_id, update_data):
        """Update session"""
        update_data['updated_at'] = datetime.utcnow()
        return Session.collection.update_one(
            {'_id': ObjectId(session_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def increment_message_count(session_id):
        """Increment message count"""
        return Session.collection.update_one(
            {'_id': ObjectId(session_id)},
            {
                '$inc': {'message_count': 1},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    @staticmethod
    def delete_session(session_id):
        """Soft delete session"""
        return Session.collection.update_one(
            {'_id': ObjectId(session_id)},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def to_dict(session):
        """Convert session document to dictionary"""
        if not session:
            return None
        return {
            'id': str(session['_id']),
            'user_id': str(session['user_id']),
            'session_name': session['session_name'],
            'message_count': session.get('message_count', 0),
            'is_active': session.get('is_active', True),
            'created_at': session['created_at'].isoformat(),
            'updated_at': session['updated_at'].isoformat()
        }