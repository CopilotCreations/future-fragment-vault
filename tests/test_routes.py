"""
Time Capsule Web - API Routes Tests

Tests for all API endpoints.
"""

import pytest
import json
from datetime import datetime, timezone, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.database import db, Capsule
from backend.routes import parse_datetime


class TestParseDatetime:
    """Tests for the parse_datetime utility function."""
    
    def test_parse_datetime_iso_with_milliseconds(self):
        """Test parsing ISO format with milliseconds.
        
        Verifies that parse_datetime correctly handles ISO 8601 format
        strings that include milliseconds and extracts year, month, day.
        """
        result = parse_datetime('2024-12-25T10:30:00.000Z')
        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 25
    
    def test_parse_datetime_iso_with_z(self):
        """Test parsing ISO format with Z suffix.
        
        Verifies that parse_datetime correctly handles ISO 8601 format
        strings with Z (Zulu/UTC) suffix and extracts time components.
        """
        result = parse_datetime('2024-06-15T14:30:00Z')
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_datetime_iso_without_z(self):
        """Test parsing ISO format without Z suffix.
        
        Verifies that parse_datetime handles ISO 8601 format strings
        that lack the trailing Z suffix.
        """
        result = parse_datetime('2024-06-15T14:30:00')
        assert result is not None
    
    def test_parse_datetime_date_only(self):
        """Test parsing date-only format.
        
        Verifies that parse_datetime handles date-only strings
        (without time component) and extracts year, month, day.
        """
        result = parse_datetime('2024-06-15')
        assert result is not None
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15
    
    def test_parse_datetime_invalid(self):
        """Test parsing invalid format returns None.
        
        Verifies that parse_datetime returns None when given
        a string that is not a valid date format.
        """
        result = parse_datetime('invalid-date')
        assert result is None
    
    def test_parse_datetime_none(self):
        """Test parsing None returns None.
        
        Verifies that parse_datetime gracefully handles None input
        by returning None without raising an exception.
        """
        result = parse_datetime(None)
        assert result is None
    
    def test_parse_datetime_empty_string(self):
        """Test parsing empty string returns None.
        
        Verifies that parse_datetime handles empty string input
        by returning None without raising an exception.
        """
        result = parse_datetime('')
        assert result is None


class TestGetCapsules:
    """Tests for GET /api/capsules endpoint."""
    
    def test_get_capsules_empty(self, client):
        """Test getting capsules when none exist.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/api/capsules')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'capsules' in data
        assert len(data['capsules']) == 0
    
    def test_get_capsules_with_data(self, client, create_test_capsules):
        """Test getting capsules with data.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        ids = create_test_capsules()
        
        response = client.get('/api/capsules')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return only public capsules
        assert len(data['capsules']) == 2
    
    def test_get_capsules_filter_by_type(self, client, create_test_capsules):
        """Test filtering capsules by content type.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules?content_type=text')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        for capsule in data['capsules']:
            assert capsule['content_type'] == 'text'
    
    def test_get_capsules_filter_by_tag(self, client, create_test_capsules):
        """Test filtering capsules by tag.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules?tag=unlocked')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['capsules']) >= 1
    
    def test_get_capsules_search(self, client, create_test_capsules):
        """Test searching capsules.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules?search=Unlocked')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['capsules']) >= 1
    
    def test_get_capsules_pagination(self, client, create_test_capsules):
        """Test capsule pagination.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules?limit=1&offset=0')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['capsules']) == 1
        assert data['limit'] == 1
        assert data['offset'] == 0


class TestGetUnlockedCapsules:
    """Tests for GET /api/capsules/unlocked endpoint."""
    
    def test_get_unlocked_capsules_empty(self, client):
        """Test getting unlocked capsules when none exist.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/api/capsules/unlocked')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'capsules' in data
        assert len(data['capsules']) == 0
    
    def test_get_unlocked_capsules_with_data(self, client, create_test_capsules):
        """Test getting only unlocked capsules.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules/unlocked')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return only unlocked public capsules
        for capsule in data['capsules']:
            assert capsule['is_unlocked'] == True
    
    def test_get_unlocked_capsules_includes_content(self, client, create_test_capsules):
        """Test that unlocked capsules include content.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules/unlocked')
        data = json.loads(response.data)
        
        for capsule in data['capsules']:
            if capsule['is_unlocked']:
                assert 'content' in capsule


class TestGetLockedCapsules:
    """Tests for GET /api/capsules/locked endpoint."""
    
    def test_get_locked_capsules_empty(self, client):
        """Test getting locked capsules when none exist.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/api/capsules/locked')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'capsules' in data
    
    def test_get_locked_capsules_with_data(self, client, create_test_capsules):
        """Test getting only locked capsules.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules/locked')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        for capsule in data['capsules']:
            assert capsule['is_unlocked'] == False
    
    def test_get_locked_capsules_excludes_content(self, client, create_test_capsules):
        """Test that locked capsules exclude content.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/capsules/locked')
        data = json.loads(response.data)
        
        for capsule in data['capsules']:
            assert 'content' not in capsule


class TestGetCapsuleById:
    """Tests for GET /api/capsules/<id> endpoint."""
    
    def test_get_capsule_not_found(self, client):
        """Test getting a non-existent capsule.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/api/capsules/non-existent-id')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_capsule_unlocked(self, client, create_test_capsules):
        """Test getting an unlocked capsule by ID.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        ids = create_test_capsules()
        
        response = client.get(f'/api/capsules/{ids["unlocked"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == ids['unlocked']
        assert 'content' in data
    
    def test_get_capsule_locked(self, client, create_test_capsules):
        """Test getting a locked capsule by ID.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        ids = create_test_capsules()
        
        response = client.get(f'/api/capsules/{ids["locked"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == ids['locked']
        assert 'content' not in data
    
    def test_get_private_capsule(self, client, create_test_capsules):
        """Test getting a private capsule returns 403.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        ids = create_test_capsules()
        
        response = client.get(f'/api/capsules/{ids["private"]}')
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data


class TestCreateCapsule:
    """Tests for POST /api/capsules endpoint."""
    
    def test_create_capsule_success(self, client, sample_capsule_data):
        """Test creating a capsule successfully.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'capsule' in data
        assert data['capsule']['title'] == sample_capsule_data['title']
    
    def test_create_capsule_no_data(self, client):
        """Test creating a capsule without data.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.post(
            '/api/capsules',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_capsule_missing_title(self, client, sample_capsule_data):
        """Test creating a capsule without title.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        del sample_capsule_data['title']
        
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'title' in data['error']
    
    def test_create_capsule_missing_content(self, client, sample_capsule_data):
        """Test creating a capsule without content.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        del sample_capsule_data['content']
        
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_capsule_missing_creator(self, client, sample_capsule_data):
        """Test creating a capsule without creator name.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        del sample_capsule_data['creator_name']
        
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_capsule_missing_unlock_date(self, client, sample_capsule_data):
        """Test creating a capsule without unlock date.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        del sample_capsule_data['unlock_date']
        
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_capsule_invalid_unlock_date(self, client, sample_capsule_data):
        """Test creating a capsule with invalid unlock date.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        sample_capsule_data['unlock_date'] = 'not-a-date'
        
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid unlock_date' in data['error']
    
    def test_create_capsule_past_unlock_date(self, client, sample_capsule_data):
        """Test creating a capsule with past unlock date.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        sample_capsule_data['unlock_date'] = past_date.isoformat()
        
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'future' in data['error'].lower()
    
    def test_create_capsule_with_string_tags(self, client, sample_capsule_data):
        """Test creating a capsule with string tags.
        
        Args:
            client: Flask test client fixture.
            sample_capsule_data: Fixture providing valid capsule data.
        """
        sample_capsule_data['tags'] = 'tag1,tag2,tag3'
        
        response = client.post(
            '/api/capsules',
            data=json.dumps(sample_capsule_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201


class TestDeleteCapsule:
    """Tests for DELETE /api/capsules/<id> endpoint."""
    
    def test_delete_capsule_success(self, client, create_test_capsules):
        """Test deleting a capsule successfully.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        ids = create_test_capsules()
        
        response = client.delete(f'/api/capsules/{ids["unlocked"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        
        # Verify capsule is deleted
        get_response = client.get(f'/api/capsules/{ids["unlocked"]}')
        assert get_response.status_code == 404
    
    def test_delete_capsule_not_found(self, client):
        """Test deleting a non-existent capsule.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.delete('/api/capsules/non-existent-id')
        assert response.status_code == 404


class TestUpdateCapsulePosition:
    """Tests for PATCH /api/capsules/<id>/position endpoint."""
    
    def test_update_position_success(self, client, create_test_capsules):
        """Test updating capsule position successfully.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        ids = create_test_capsules()
        
        response = client.patch(
            f'/api/capsules/{ids["unlocked"]}/position',
            data=json.dumps({
                'fragment_x': 25.5,
                'fragment_y': 75.0,
                'fragment_rotation': 10.0,
                'fragment_scale': 1.1
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['fragment_x'] == 25.5
        assert data['fragment_y'] == 75.0
    
    def test_update_position_clamps_values(self, client, create_test_capsules):
        """Test that position values are clamped to valid ranges.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        ids = create_test_capsules()
        
        response = client.patch(
            f'/api/capsules/{ids["unlocked"]}/position',
            data=json.dumps({
                'fragment_x': 150.0,  # Should be clamped to 100
                'fragment_y': -50.0,  # Should be clamped to 0
                'fragment_rotation': 45.0,  # Should be clamped to 30
                'fragment_scale': 0.1  # Should be clamped to 0.5
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['fragment_x'] == 100.0
        assert data['fragment_y'] == 0.0
        assert data['fragment_rotation'] == 30.0
        assert data['fragment_scale'] == 0.5
    
    def test_update_position_not_found(self, client):
        """Test updating position of non-existent capsule.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.patch(
            '/api/capsules/non-existent-id/position',
            data=json.dumps({'fragment_x': 50.0}),
            content_type='application/json'
        )
        
        assert response.status_code == 404


class TestGetTags:
    """Tests for GET /api/tags endpoint."""
    
    def test_get_tags_empty(self, client):
        """Test getting tags when none exist.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/api/tags')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tags' in data
        assert len(data['tags']) == 0
    
    def test_get_tags_with_data(self, client, create_test_capsules):
        """Test getting all unique tags.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/tags')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'tags' in data
        assert 'test' in data['tags']
    
    def test_get_tags_sorted(self, client, create_test_capsules):
        """Test that tags are sorted alphabetically.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/tags')
        data = json.loads(response.data)
        
        tags = data['tags']
        assert tags == sorted(tags)


class TestGetStats:
    """Tests for GET /api/stats endpoint."""
    
    def test_get_stats_empty(self, client):
        """Test getting stats when no capsules exist.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['total'] == 0
        assert data['unlocked'] == 0
        assert data['locked'] == 0
    
    def test_get_stats_with_data(self, client, create_test_capsules):
        """Test getting stats with capsules.
        
        Args:
            client: Flask test client fixture.
            create_test_capsules: Fixture that creates test capsule data.
        """
        create_test_capsules()
        
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['total'] == 2  # Only public capsules
        assert data['unlocked'] == 1
        assert data['locked'] == 1


class TestServeStatic:
    """Tests for static file serving."""
    
    def test_serve_index(self, client):
        """Test serving the index page.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/')
        assert response.status_code == 200
    
    def test_serve_css(self, client):
        """Test serving CSS file.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/style.css')
        assert response.status_code == 200
    
    def test_serve_js(self, client):
        """Test serving JavaScript file.
        
        Args:
            client: Flask test client fixture.
        """
        response = client.get('/main.js')
        assert response.status_code == 200
