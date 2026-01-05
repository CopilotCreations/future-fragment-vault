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
    """Create application for testing.

    Creates a Flask application configured for testing with an in-memory
    SQLite database. The database tables are created before yielding
    and cleaned up after the test completes.

    Yields:
        Flask: The configured Flask application instance for testing.
    """
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
    """Create a test client for the app.

    Args:
        app: The Flask application fixture.

    Returns:
        FlaskClient: A test client for making HTTP requests to the app.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app.

    Args:
        app: The Flask application fixture.

    Returns:
        FlaskCliRunner: A CLI runner for testing Flask CLI commands.
    """
    return app.test_cli_runner()


@pytest.fixture
def sample_capsule_data():
    """Provide sample capsule data for testing.

    Creates a dictionary with sample capsule data that has an unlock date
    30 days in the future.

    Returns:
        dict: A dictionary containing sample capsule attributes including
            title, content, content_type, creator_name, unlock_date, tags,
            and is_public flag.
    """
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
    """Provide capsule data with past unlock date (already unlocked).

    Creates a dictionary with capsule data that has an unlock date
    1 day in the past, simulating an already unlocked capsule.

    Returns:
        dict: A dictionary containing capsule attributes with a past
            unlock_date, making the capsule already viewable.
    """
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
    """Create multiple test capsules in the database.

    Provides a factory function that creates three test capsules with
    different states: unlocked (past date), locked (future date), and
    private (not publicly visible).

    Args:
        app: The Flask application fixture.

    Returns:
        callable: A function that when called creates the test capsules
            and returns a dictionary mapping capsule states ('unlocked',
            'locked', 'private') to their respective database IDs.
    """
    def _create_capsules():
        """Create and persist test capsules to the database.

        Returns:
            dict: A dictionary with keys 'unlocked', 'locked', and 'private'
                mapping to the corresponding capsule IDs.
        """
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
