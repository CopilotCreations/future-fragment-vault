"""
Time Capsule Web - Database Model Tests

Tests for the Capsule model and database operations.
"""

import pytest
from datetime import datetime, timezone, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.database import db, Capsule, generate_uuid


class TestGenerateUUID:
    """Tests for UUID generation."""
    
    def test_generate_uuid_returns_string(self):
        """Test that generate_uuid returns a string.

        Validates that the generate_uuid function returns a value
        of type string.
        """
        uuid = generate_uuid()
        assert isinstance(uuid, str)
    
    def test_generate_uuid_unique(self):
        """Test that generate_uuid returns unique values.

        Generates 100 UUIDs and verifies that all values are unique
        by comparing list length to set length.
        """
        uuids = [generate_uuid() for _ in range(100)]
        assert len(uuids) == len(set(uuids))
    
    def test_generate_uuid_format(self):
        """Test that generate_uuid returns valid UUID format.

        Validates that the generated UUID follows the standard format
        of 8-4-4-4-12 hexadecimal characters separated by hyphens.
        """
        uuid = generate_uuid()
        parts = uuid.split('-')
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12


class TestCapsuleModel:
    """Tests for the Capsule model."""
    
    def test_create_capsule(self, app):
        """Test creating a new capsule.

        Args:
            app: Flask application fixture with test configuration.

        Validates that a capsule can be created and persisted to the
        database with all required fields properly stored.
        """
        with app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=30)
            capsule = Capsule(
                title='Test Capsule',
                content='Test content',
                content_type='text',
                creator_name='Test User',
                unlock_date=future_date
            )
            
            db.session.add(capsule)
            db.session.commit()
            
            assert capsule.id is not None
            assert capsule.title == 'Test Capsule'
            assert capsule.content == 'Test content'
            assert capsule.content_type == 'text'
            assert capsule.creator_name == 'Test User'
    
    def test_capsule_defaults(self, app):
        """Test that capsule has correct default values.

        Args:
            app: Flask application fixture with test configuration.

        Validates that capsules are created with appropriate default
        values for content_type, is_public, and fragment positioning.
        """
        with app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=1)
            capsule = Capsule(
                title='Test',
                content='Content',
                creator_name='User',
                unlock_date=future_date
            )
            
            db.session.add(capsule)
            db.session.commit()
            
            assert capsule.content_type == 'text'
            assert capsule.is_public == True
            assert capsule.fragment_x is not None
            assert capsule.fragment_y is not None
            assert capsule.fragment_rotation is not None
            assert capsule.fragment_scale is not None
    
    def test_capsule_fragment_position_ranges(self, app):
        """Test that fragment positions are within valid ranges.

        Args:
            app: Flask application fixture with test configuration.

        Validates that auto-generated fragment positions fall within
        expected ranges: x/y between 10-90, rotation between -15 and 15,
        and scale between 0.8 and 1.2.
        """
        with app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=1)
            capsule = Capsule(
                title='Test',
                content='Content',
                creator_name='User',
                unlock_date=future_date
            )
            
            assert 10 <= capsule.fragment_x <= 90
            assert 10 <= capsule.fragment_y <= 90
            assert -15 <= capsule.fragment_rotation <= 15
            assert 0.8 <= capsule.fragment_scale <= 1.2
    
    def test_capsule_is_unlocked_future(self, app):
        """Test is_unlocked returns False for future capsules.

        Args:
            app: Flask application fixture with test configuration.

        Validates that capsules with unlock dates in the future
        return False from the is_unlocked method.
        """
        with app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=30)
            capsule = Capsule(
                title='Future Capsule',
                content='Content',
                creator_name='User',
                unlock_date=future_date
            )
            
            assert capsule.is_unlocked() == False
    
    def test_capsule_is_unlocked_past(self, app):
        """Test is_unlocked returns True for past capsules.

        Args:
            app: Flask application fixture with test configuration.

        Validates that capsules with unlock dates in the past
        return True from the is_unlocked method.
        """
        with app.app_context():
            past_date = datetime.now(timezone.utc) - timedelta(days=1)
            capsule = Capsule(
                title='Past Capsule',
                content='Content',
                creator_name='User',
                unlock_date=past_date
            )
            
            assert capsule.is_unlocked() == True
    
    def test_time_until_unlock_future(self, app):
        """Test time_until_unlock returns timedelta for future capsules.

        Args:
            app: Flask application fixture with test configuration.

        Validates that capsules with future unlock dates return a
        timedelta object representing the time remaining until unlock.
        """
        with app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=30)
            capsule = Capsule(
                title='Future Capsule',
                content='Content',
                creator_name='User',
                unlock_date=future_date
            )
            
            time_remaining = capsule.time_until_unlock()
            assert time_remaining is not None
            assert time_remaining.days >= 29
    
    def test_time_until_unlock_past(self, app):
        """Test time_until_unlock returns None for past capsules.

        Args:
            app: Flask application fixture with test configuration.

        Validates that capsules with past unlock dates return None
        from the time_until_unlock method.
        """
        with app.app_context():
            past_date = datetime.now(timezone.utc) - timedelta(days=1)
            capsule = Capsule(
                title='Past Capsule',
                content='Content',
                creator_name='User',
                unlock_date=past_date
            )
            
            assert capsule.time_until_unlock() is None
    
    def test_to_dict_unlocked(self, app):
        """Test to_dict includes content for unlocked capsules.

        Args:
            app: Flask application fixture with test configuration.

        Validates that the to_dict method includes content, sets
        is_unlocked to True, and properly parses tags for unlocked capsules.
        """
        with app.app_context():
            past_date = datetime.now(timezone.utc) - timedelta(days=1)
            capsule = Capsule(
                title='Past Capsule',
                content='Secret content',
                creator_name='User',
                unlock_date=past_date,
                tags='tag1,tag2'
            )
            
            result = capsule.to_dict(include_content=True)
            
            assert result['content'] == 'Secret content'
            assert result['is_unlocked'] == True
            assert result['tags'] == ['tag1', 'tag2']
    
    def test_to_dict_locked(self, app):
        """Test to_dict excludes content for locked capsules.

        Args:
            app: Flask application fixture with test configuration.

        Validates that the to_dict method excludes content, sets
        is_unlocked to False, and includes time_remaining for locked capsules.
        """
        with app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=30)
            capsule = Capsule(
                title='Future Capsule',
                content='Secret content',
                creator_name='User',
                unlock_date=future_date
            )
            
            result = capsule.to_dict(include_content=True)
            
            assert 'content' not in result
            assert result['is_unlocked'] == False
            assert 'time_remaining' in result
            assert result['time_remaining']['days'] >= 29
    
    def test_to_dict_no_tags(self, app):
        """Test to_dict handles None tags correctly.

        Args:
            app: Flask application fixture with test configuration.

        Validates that capsules with None tags return an empty list
        in the dictionary representation.
        """
        with app.app_context():
            past_date = datetime.now(timezone.utc) - timedelta(days=1)
            capsule = Capsule(
                title='No Tags Capsule',
                content='Content',
                creator_name='User',
                unlock_date=past_date,
                tags=None
            )
            
            result = capsule.to_dict()
            assert result['tags'] == []
    
    def test_capsule_repr(self, app):
        """Test capsule string representation.

        Args:
            app: Flask application fixture with test configuration.

        Validates that the __repr__ method returns a string containing
        the capsule's id and title.
        """
        with app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=1)
            capsule = Capsule(
                id='test-id-123',
                title='Test Capsule',
                content='Content',
                creator_name='User',
                unlock_date=future_date
            )
            
            repr_str = repr(capsule)
            assert 'test-id-123' in repr_str
            assert 'Test Capsule' in repr_str


class TestCapsuleWithNaiveDatetime:
    """Tests for capsule handling of naive datetime objects."""
    
    def test_is_unlocked_with_naive_datetime(self, app):
        """Test is_unlocked handles naive datetime correctly.

        Args:
            app: Flask application fixture with test configuration.

        Validates that the is_unlocked method works correctly when
        the capsule was created with a naive datetime (no timezone info).
        """
        with app.app_context():
            # Create with naive datetime (no timezone)
            past_date = datetime.now() - timedelta(days=1)
            capsule = Capsule(
                title='Naive Date Capsule',
                content='Content',
                creator_name='User',
                unlock_date=past_date
            )
            
            # Should not raise an error
            result = capsule.is_unlocked()
            assert result == True
    
    def test_time_until_unlock_with_naive_datetime(self, app):
        """Test time_until_unlock handles naive datetime correctly.

        Args:
            app: Flask application fixture with test configuration.

        Validates that the time_until_unlock method works correctly
        when the capsule was created with a naive datetime (no timezone info).
        """
        with app.app_context():
            future_date = datetime.now() + timedelta(days=30)
            capsule = Capsule(
                title='Naive Date Capsule',
                content='Content',
                creator_name='User',
                unlock_date=future_date
            )
            
            result = capsule.time_until_unlock()
            assert result is not None
            assert result.days >= 29
