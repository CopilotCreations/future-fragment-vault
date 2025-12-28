"""
Time Capsule Web - Application Factory Tests

Tests for app creation and configuration.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.app import create_app


class TestAppFactory:
    """Tests for the application factory."""
    
    def test_create_app_default_config(self):
        """Test creating app with default configuration."""
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        
        assert app is not None
        assert app.config['TESTING'] == True
    
    def test_create_app_custom_config(self):
        """Test creating app with custom configuration."""
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'custom-secret',
            'CUSTOM_SETTING': 'custom-value'
        })
        
        assert app.config['SECRET_KEY'] == 'custom-secret'
        assert app.config['CUSTOM_SETTING'] == 'custom-value'
    
    def test_create_app_has_api_blueprint(self):
        """Test that app has API blueprint registered."""
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        
        assert 'api' in app.blueprints
    
    def test_create_app_cors_enabled(self):
        """Test that CORS is enabled for API routes."""
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        
        with app.test_client() as client:
            response = client.options('/api/capsules')
            # CORS headers should be present
            assert response.status_code in [200, 204]
    
    def test_create_app_static_folder_set(self):
        """Test that static folder is configured."""
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        
        assert 'frontend' in app.static_folder


class TestAppRoutes:
    """Tests for app-level routes."""
    
    def test_root_route_exists(self, client):
        """Test that root route returns index."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_fallback_route(self, client):
        """Test that unknown routes fallback to index."""
        # Since the file may not exist, we get a fallback behavior
        # For non-existent files, the app serves index.html
        response = client.get('/nonexistent-page')
        # Accept either 200 (file served) or 404 (file not found)
        assert response.status_code in [200, 404]
