"""
Time Capsule Web - API Routes

This module contains all the API endpoints for the Time Capsule Web application.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from .database import db, Capsule

api_bp = Blueprint('api', __name__)


def parse_datetime(date_string):
    """Parse a datetime string into a datetime object.

    Args:
        date_string (str): ISO format datetime string.

    Returns:
        datetime: Parsed datetime object with UTC timezone, or None if parsing fails.
    """
    if not date_string:
        return None
    
    # Try fromisoformat first (handles +00:00 timezone)
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass
    
    # Handle various ISO formats
    for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', 
                '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(date_string, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    return None


@api_bp.route('/capsules', methods=['GET'])
def get_capsules():
    """Get all unlocked public capsules.

    Query Parameters:
        tag (str): Filter by tag.
        search (str): Search in title and content.
        content_type (str): Filter by content type.
        limit (int): Maximum number of results (default: 50).
        offset (int): Number of results to skip (default: 0).

    Returns:
        flask.Response: JSON response containing capsules array, total count,
            limit, and offset.
    """
    tag = request.args.get('tag')
    search = request.args.get('search')
    content_type = request.args.get('content_type')
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    query = Capsule.query.filter(Capsule.is_public == True)
    
    if tag:
        query = query.filter(Capsule.tags.contains(tag))
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Capsule.title.ilike(search_pattern),
                Capsule.content.ilike(search_pattern)
            )
        )
    
    if content_type:
        query = query.filter(Capsule.content_type == content_type)
    
    capsules = query.order_by(Capsule.created_at.desc()).offset(offset).limit(limit).all()
    
    # Filter to only unlocked capsules for content display
    result = []
    for capsule in capsules:
        capsule_dict = capsule.to_dict(include_content=capsule.is_unlocked())
        result.append(capsule_dict)
    
    return jsonify({
        'capsules': result,
        'total': query.count(),
        'limit': limit,
        'offset': offset
    })


@api_bp.route('/capsules/unlocked', methods=['GET'])
def get_unlocked_capsules():
    """Get only unlocked capsules for the collage display.

    Query Parameters:
        limit (int): Maximum number of results (default: 30).

    Returns:
        flask.Response: JSON response containing array of unlocked capsules
            with full content.
    """
    limit = min(int(request.args.get('limit', 30)), 100)
    
    now = datetime.now(timezone.utc)
    capsules = Capsule.query.filter(
        Capsule.is_public == True,
        Capsule.unlock_date <= now
    ).order_by(Capsule.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'capsules': [capsule.to_dict(include_content=True) for capsule in capsules]
    })


@api_bp.route('/capsules/locked', methods=['GET'])
def get_locked_capsules():
    """Get locked capsules (without content) to show countdown.

    Query Parameters:
        limit (int): Maximum number of results (default: 10).

    Returns:
        flask.Response: JSON response containing array of locked capsules
            without content.
    """
    limit = min(int(request.args.get('limit', 10)), 50)
    
    now = datetime.now(timezone.utc)
    capsules = Capsule.query.filter(
        Capsule.is_public == True,
        Capsule.unlock_date > now
    ).order_by(Capsule.unlock_date.asc()).limit(limit).all()
    
    return jsonify({
        'capsules': [capsule.to_dict(include_content=False) for capsule in capsules]
    })


@api_bp.route('/capsules/<capsule_id>', methods=['GET'])
def get_capsule(capsule_id):
    """Get a specific capsule by ID.

    Args:
        capsule_id (str): The unique identifier of the capsule.

    Returns:
        flask.Response: JSON response containing the capsule object
            (content included only if unlocked), or error response.
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({'error': 'Capsule not found'}), 404
    
    if not capsule.is_public:
        return jsonify({'error': 'This capsule is private'}), 403
    
    return jsonify(capsule.to_dict(include_content=capsule.is_unlocked()))


@api_bp.route('/capsules', methods=['POST'])
def create_capsule():
    """Create a new time capsule.

    Request Body:
        title (str): Title of the capsule (required).
        content (str): The message, drawing, or code (required).
        content_type (str): Type of content - 'text', 'drawing', 'code'
            (default: 'text').
        creator_name (str): Name of the creator (required).
        creator_email (str): Email of the creator (optional).
        unlock_date (str): ISO format date when capsule unlocks (required).
        tags (list[str]): Array of tags (optional).
        is_public (bool): Whether capsule is public (default: true).

    Returns:
        flask.Response: JSON response containing success message and created
            capsule object, or error response.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['title', 'content', 'creator_name', 'unlock_date']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Parse unlock date
    unlock_date = parse_datetime(data['unlock_date'])
    if not unlock_date:
        return jsonify({'error': 'Invalid unlock_date format. Use ISO 8601 format.'}), 400
    
    # Validate unlock date is in the future
    now = datetime.now(timezone.utc)
    if unlock_date <= now:
        return jsonify({'error': 'Unlock date must be in the future'}), 400
    
    # Process tags
    tags = data.get('tags', [])
    if isinstance(tags, list):
        tags = ','.join(tags)
    
    # Create capsule
    capsule = Capsule(
        title=data['title'],
        content=data['content'],
        content_type=data.get('content_type', 'text'),
        creator_name=data['creator_name'],
        creator_email=data.get('creator_email'),
        unlock_date=unlock_date,
        tags=tags,
        is_public=data.get('is_public', True)
    )
    
    db.session.add(capsule)
    db.session.commit()
    
    return jsonify({
        'message': 'Capsule created successfully',
        'capsule': capsule.to_dict(include_content=False)
    }), 201


@api_bp.route('/capsules/<capsule_id>', methods=['DELETE'])
def delete_capsule(capsule_id):
    """Delete a capsule by ID.

    Args:
        capsule_id (str): The unique identifier of the capsule.

    Returns:
        flask.Response: JSON response containing success message,
            or error response if capsule not found.
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({'error': 'Capsule not found'}), 404
    
    db.session.delete(capsule)
    db.session.commit()
    
    return jsonify({'message': 'Capsule deleted successfully'})


@api_bp.route('/capsules/<capsule_id>/position', methods=['PATCH'])
def update_capsule_position(capsule_id):
    """Update the fragment position of a capsule for the collage display.

    Args:
        capsule_id (str): The unique identifier of the capsule.

    Request Body:
        fragment_x (float): X position (0-100).
        fragment_y (float): Y position (0-100).
        fragment_rotation (float): Rotation angle (-30 to 30).
        fragment_scale (float): Scale factor (0.5 to 1.5).

    Returns:
        flask.Response: JSON response containing updated capsule data,
            or error response if capsule not found.
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({'error': 'Capsule not found'}), 404
    
    data = request.get_json()
    
    if 'fragment_x' in data:
        capsule.fragment_x = max(0, min(100, float(data['fragment_x'])))
    if 'fragment_y' in data:
        capsule.fragment_y = max(0, min(100, float(data['fragment_y'])))
    if 'fragment_rotation' in data:
        capsule.fragment_rotation = max(-30, min(30, float(data['fragment_rotation'])))
    if 'fragment_scale' in data:
        capsule.fragment_scale = max(0.5, min(1.5, float(data['fragment_scale'])))
    
    db.session.commit()
    
    return jsonify(capsule.to_dict(include_content=capsule.is_unlocked()))


@api_bp.route('/tags', methods=['GET'])
def get_tags():
    """Get all unique tags from capsules.

    Returns:
        flask.Response: JSON response containing sorted array of unique tags.
    """
    capsules = Capsule.query.filter(
        Capsule.is_public == True,
        Capsule.tags.isnot(None),
        Capsule.tags != ''
    ).all()
    
    all_tags = set()
    for capsule in capsules:
        if capsule.tags:
            for tag in capsule.tags.split(','):
                tag = tag.strip()
                if tag:
                    all_tags.add(tag)
    
    return jsonify({'tags': sorted(list(all_tags))})


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about the capsules.

    Returns:
        flask.Response: JSON response containing total, unlocked, and locked
            capsule counts.
    """
    now = datetime.now(timezone.utc)
    
    total = Capsule.query.filter(Capsule.is_public == True).count()
    unlocked = Capsule.query.filter(
        Capsule.is_public == True,
        Capsule.unlock_date <= now
    ).count()
    locked = Capsule.query.filter(
        Capsule.is_public == True,
        Capsule.unlock_date > now
    ).count()
    
    return jsonify({
        'total': total,
        'unlocked': unlocked,
        'locked': locked
    })
