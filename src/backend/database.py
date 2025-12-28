"""
Time Capsule Web - Database Configuration and Models

This module contains the SQLAlchemy database configuration and model definitions.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask application.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()


def generate_uuid():
    """Generate a unique identifier for capsules."""
    return str(uuid.uuid4())


class Capsule(db.Model):
    """
    Time Capsule model representing a message locked until a future date.
    
    Attributes:
        id: Unique identifier for the capsule
        title: Title of the capsule
        content: The message, drawing data, or code snippet
        content_type: Type of content ('text', 'drawing', 'code')
        creator_name: Name of the capsule creator
        creator_email: Optional email of the creator
        tags: Comma-separated tags for categorization
        created_at: Timestamp when the capsule was created
        unlock_date: Date when the capsule becomes visible
        is_public: Whether the capsule is publicly visible when unlocked
        fragment_x: X position for collage display (0-100)
        fragment_y: Y position for collage display (0-100)
        fragment_rotation: Rotation angle for collage display (-30 to 30)
        fragment_scale: Scale factor for collage display (0.5 to 1.5)
    """
    __tablename__ = 'capsules'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), nullable=False, default='text')
    creator_name = db.Column(db.String(100), nullable=False)
    creator_email = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    unlock_date = db.Column(db.DateTime, nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    fragment_x = db.Column(db.Float, default=50.0)
    fragment_y = db.Column(db.Float, default=50.0)
    fragment_rotation = db.Column(db.Float, default=0.0)
    fragment_scale = db.Column(db.Float, default=1.0)
    
    def __init__(self, **kwargs):
        """Initialize a new capsule with random fragment positioning."""
        super().__init__(**kwargs)
        if 'id' not in kwargs:
            self.id = generate_uuid()
        if 'fragment_x' not in kwargs:
            import random
            self.fragment_x = random.uniform(10, 90)
        if 'fragment_y' not in kwargs:
            import random
            self.fragment_y = random.uniform(10, 90)
        if 'fragment_rotation' not in kwargs:
            import random
            self.fragment_rotation = random.uniform(-15, 15)
        if 'fragment_scale' not in kwargs:
            import random
            self.fragment_scale = random.uniform(0.8, 1.2)
    
    def is_unlocked(self):
        """
        Check if the capsule has been unlocked based on current time.
        
        Returns:
            bool: True if the unlock date has passed, False otherwise
        """
        now = datetime.now(timezone.utc)
        unlock_utc = self.unlock_date
        if unlock_utc.tzinfo is None:
            unlock_utc = unlock_utc.replace(tzinfo=timezone.utc)
        return now >= unlock_utc
    
    def time_until_unlock(self):
        """
        Calculate the time remaining until the capsule unlocks.
        
        Returns:
            timedelta: Time remaining until unlock, or None if already unlocked
        """
        if self.is_unlocked():
            return None
        now = datetime.now(timezone.utc)
        unlock_utc = self.unlock_date
        if unlock_utc.tzinfo is None:
            unlock_utc = unlock_utc.replace(tzinfo=timezone.utc)
        return unlock_utc - now
    
    def to_dict(self, include_content=True):
        """
        Convert the capsule to a dictionary representation.
        
        Args:
            include_content: Whether to include the content (only for unlocked capsules)
            
        Returns:
            dict: Dictionary representation of the capsule
        """
        result = {
            'id': self.id,
            'title': self.title,
            'content_type': self.content_type,
            'creator_name': self.creator_name,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'unlock_date': self.unlock_date.isoformat() if self.unlock_date else None,
            'is_public': self.is_public,
            'is_unlocked': self.is_unlocked(),
            'fragment_x': self.fragment_x,
            'fragment_y': self.fragment_y,
            'fragment_rotation': self.fragment_rotation,
            'fragment_scale': self.fragment_scale
        }
        
        if include_content and self.is_unlocked():
            result['content'] = self.content
        elif not self.is_unlocked():
            time_remaining = self.time_until_unlock()
            if time_remaining:
                result['time_remaining'] = {
                    'days': time_remaining.days,
                    'hours': time_remaining.seconds // 3600,
                    'minutes': (time_remaining.seconds % 3600) // 60
                }
        
        return result
    
    def __repr__(self):
        return f'<Capsule {self.id}: {self.title}>'
