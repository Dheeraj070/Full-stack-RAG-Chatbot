import re
import logging

logger = logging.getLogger(__name__)

class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        return True, "Password is valid"
    
    @staticmethod
    def validate_role(role):
        """Validate user role"""
        valid_roles = ['student', 'admin']
        return role in valid_roles
    
    @staticmethod
    def sanitize_input(text, max_length=10000):
        """Sanitize text input"""
        if not text:
            return ""
        
        # Remove any potential XSS or injection attempts
        text = text.strip()
        text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_file_size(file_size, max_size):
        """Validate file size"""
        return file_size <= max_size