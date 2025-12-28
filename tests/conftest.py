"""
Time Capsule Web - Test Configuration

This module provides pytest fixtures for testing.
"""

import os
import sys
import pytest
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.app import create_app
from backend.database import db, Capsule


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        # Close engine connections
        db.engine.dispose()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def sample_capsule_data():
    """Provide sample capsule data for testing."""
    future_date = datetime.now(timezone.utc) + timedelta(days=30)
    return {
        'title': 'Test Capsule',
        'content': 'This is a test message for the future.',
        'content_type': 'text',
        'creator_name': 'Test User',
        'unlock_date': future_date.isoformat(),
        'tags': ['test', 'sample'],
        'is_public': True
    }


@pytest.fixture
def past_capsule_data():
    """Provide capsule data with past unlock date (already unlocked)."""
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    return {
        'title': 'Past Capsule',
        'content': 'This capsule is already unlocked.',
        'content_type': 'text',
        'creator_name': 'Past User',
        'unlock_date': past_date,
        'tags': 'past,unlocked',
        'is_public': True
    }


@pytest.fixture
def create_test_capsules(app):
    """Create multiple test capsules in the database."""
    def _create_capsules():
        with app.app_context():
            # Create unlocked capsule
            past_date = datetime.now(timezone.utc) - timedelta(days=1)
            unlocked = Capsule(
                title='Unlocked Capsule',
                content='This is visible content.',
                content_type='text',
                creator_name='Test User',
                unlock_date=past_date,
                tags='test,unlocked',
                is_public=True
            )
            
            # Create locked capsule
            future_date = datetime.now(timezone.utc) + timedelta(days=30)
            locked = Capsule(
                title='Locked Capsule',
                content='This is hidden content.',
                content_type='code',
                creator_name='Another User',
                unlock_date=future_date,
                tags='test,locked',
                is_public=True
            )
            
            # Create private capsule
            private = Capsule(
                title='Private Capsule',
                content='This is private.',
                content_type='drawing',
                creator_name='Private User',
                unlock_date=past_date,
                is_public=False
            )
            
            db.session.add_all([unlocked, locked, private])
            db.session.commit()
            
            return {
                'unlocked': unlocked.id,
                'locked': locked.id,
                'private': private.id
            }
    
    return _create_capsules
