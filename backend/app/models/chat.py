from datetime import datetime
from app import mongo
from bson import ObjectId

class Chat:
    """Chat model for MongoDB"""
    
    collection = mongo.db.chats
    
    @staticmethod
    def create(user_id, session_id, message, response, context_type='direct', pdf_id=None, metadata=None):
        """Create a new chat entry"""
        chat_data = {
            'user_id': ObjectId(user_id),
            'session_id': ObjectId(session_id),
            'message': message,
            'response': response,
            'context_type': context_type,  # 'direct' or 'pdf'
            'pdf_id': ObjectId(pdf_id) if pdf_id else None,
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = Chat.collection.insert_one(chat_data)
        chat_data['_id'] = result.inserted_id
        return chat_data
    
    @staticmethod
    def get_by_session(session_id, skip=0, limit=50):
        """Get chats by session ID"""
        chats = list(Chat.collection.find(
            {'session_id': ObjectId(session_id)}
        ).sort('created_at', 1).skip(skip).limit(limit))
        return chats
    
    @staticmethod
    def get_by_user(user_id, skip=0, limit=50):
        """Get chats by user ID"""
        chats = list(Chat.collection.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).skip(skip).limit(limit))
        total = Chat.collection.count_documents({'user_id': ObjectId(user_id)})
        return chats, total
    
    @staticmethod
    def get_all_chats(skip=0, limit=50):
        """Get all chats (admin only)"""
        chats = list(Chat.collection.find().sort('created_at', -1).skip(skip).limit(limit))
        total = Chat.collection.count_documents({})
        return chats, total
    
    @staticmethod
    def delete_chat(chat_id):
        """Delete a chat"""
        return Chat.collection.delete_one({'_id': ObjectId(chat_id)})
    
    @staticmethod
    def delete_by_session(session_id):
        """Delete all chats in a session"""
        return Chat.collection.delete_many({'session_id': ObjectId(session_id)})
    
    @staticmethod
    def to_dict(chat):
        """Convert chat document to dictionary"""
        if not chat:
            return None
        return {
            'id': str(chat['_id']),
            'user_id': str(chat['user_id']),
            'session_id': str(chat['session_id']),
            'message': chat['message'],
            'response': chat['response'],
            'context_type': chat['context_type'],
            'pdf_id': str(chat['pdf_id']) if chat.get('pdf_id') else None,
            'metadata': chat.get('metadata', {}),
            'created_at': chat['created_at'].isoformat()
        }