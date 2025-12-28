# Time Capsule Web Architecture

This document describes the architectural design and technical decisions behind the Time Capsule Web application.

## Overview

Time Capsule Web is a web application that allows users to create messages, drawings, or code snippets that are locked until a future date. The application presents unlocked capsules in a surreal, collage-like visual display.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │  index.html │  │  style.css  │  │   main.js   │                  │
│  │   (Views)   │  │  (Styling)  │  │   (Logic)   │                  │
│  └──────┬──────┘  └─────────────┘  └──────┬──────┘                  │
│         │                                  │                         │
│         └──────────────┬───────────────────┘                         │
│                        │ REST API Calls                              │
└────────────────────────┼─────────────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────────────┐
│                        ▼                                             │
│                   Backend Layer                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      Flask Application                          ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            ││
│  │  │   app.py    │  │  routes.py  │  │ database.py │            ││
│  │  │  (Factory)  │  │ (API Layer) │  │  (Models)   │            ││
│  │  └─────────────┘  └─────────────┘  └──────┬──────┘            ││
│  └──────────────────────────────────────────┼───────────────────────┘│
│                                              │                       │
└──────────────────────────────────────────────┼───────────────────────┘
                                               │
┌──────────────────────────────────────────────┼───────────────────────┐
│                                              ▼                       │
│                        Database Layer                                │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    SQLite / PostgreSQL                          ││
│  │                                                                 ││
│  │  ┌─────────────────────────────────────┐                       ││
│  │  │            Capsules Table            │                       ││
│  │  │  - id (UUID)                         │                       ││
│  │  │  - title, content, content_type      │                       ││
│  │  │  - creator_name, creator_email       │                       ││
│  │  │  - unlock_date, created_at           │                       ││
│  │  │  - fragment positions (x, y, etc.)   │                       ││
│  │  └─────────────────────────────────────┘                       ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

The frontend is built with vanilla HTML, CSS, and JavaScript for simplicity and performance.

#### index.html
- **Purpose**: Main HTML structure and views
- **Views**:
  - Collage View: Displays unlocked capsules in a visual collage
  - Create View: Form for creating new time capsules
  - Upcoming View: Shows locked capsules with countdowns
- **Features**:
  - Responsive design
  - Modal for viewing capsule details
  - Real-time statistics display

#### style.css
- **Purpose**: Visual styling and animations
- **Design Philosophy**: Surreal, collage-like aesthetic
- **Features**:
  - CSS custom properties for theming
  - Glassmorphism effects with backdrop blur
  - Smooth animations and transitions
  - Gradient color schemes
  - Responsive breakpoints

#### main.js
- **Purpose**: Application logic and API interaction
- **Key Responsibilities**:
  - State management
  - API communication
  - DOM manipulation
  - Event handling
  - Drawing canvas management
- **Design Patterns**:
  - Module pattern for organization
  - Event-driven architecture
  - Debouncing for search inputs

### Backend Layer

The backend uses Flask, a lightweight Python web framework.

#### app.py (Application Factory)
- **Purpose**: Create and configure Flask application
- **Features**:
  - Factory pattern for flexible configuration
  - CORS setup for API access
  - Static file serving
  - Blueprint registration
- **Configuration**:
  - Supports environment variables
  - Testing configuration override

#### routes.py (API Routes)
- **Purpose**: Define and implement API endpoints
- **Endpoints**:
  | Method | Endpoint | Description |
  |--------|----------|-------------|
  | GET | /api/capsules | List all public capsules |
  | GET | /api/capsules/unlocked | Get unlocked capsules |
  | GET | /api/capsules/locked | Get locked capsules |
  | GET | /api/capsules/:id | Get specific capsule |
  | POST | /api/capsules | Create new capsule |
  | DELETE | /api/capsules/:id | Delete capsule |
  | PATCH | /api/capsules/:id/position | Update fragment position |
  | GET | /api/tags | Get all unique tags |
  | GET | /api/stats | Get capsule statistics |

#### database.py (Database Models)
- **Purpose**: Define database schema and operations
- **ORM**: SQLAlchemy
- **Model**: Capsule
  - Core fields: id, title, content, content_type
  - Metadata: creator_name, tags, dates
  - Display: fragment positioning for collage

### Database Layer

Uses SQLite for development and can be configured for PostgreSQL in production.

#### Capsule Model Schema
```sql
CREATE TABLE capsules (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    creator_name VARCHAR(100) NOT NULL,
    creator_email VARCHAR(255),
    tags VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    unlock_date DATETIME NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    fragment_x FLOAT DEFAULT 50.0,
    fragment_y FLOAT DEFAULT 50.0,
    fragment_rotation FLOAT DEFAULT 0.0,
    fragment_scale FLOAT DEFAULT 1.0
);
```

## Data Flow

### Creating a Capsule

```
User Input → Form Validation → API POST → Database Insert → Response
    │                                                           │
    └──────────────────────────────────────────────────────────┘
                        UI Update
```

1. User fills out the capsule creation form
2. JavaScript validates input and formats data
3. POST request sent to `/api/capsules`
4. Server validates data and sets unlock date
5. Capsule saved to database with random fragment position
6. Success response returned
7. UI updates to show new capsule

### Viewing Capsules

```
Page Load → API GET → Filter by Date → Response → Render Collage
                          │
                          ├── Unlocked → Include Content
                          └── Locked → Include Countdown
```

1. Frontend requests capsules from API
2. Server queries database
3. Each capsule checked against current time
4. Unlocked capsules include content
5. Locked capsules include time remaining
6. Frontend renders capsules as collage fragments

## Security Considerations

### Privacy Protection
- **Locked Content**: Capsule content is never sent to the client until the unlock date
- **Server-Side Validation**: Unlock status determined on server, not client
- **Public/Private Flag**: Users can mark capsules as private

### Input Validation
- Required field validation
- Date format validation
- Future date enforcement
- Content type validation

### Potential Improvements
- Authentication system for users
- Rate limiting on API endpoints
- CSRF protection
- Content sanitization

## Scalability Considerations

### Current Design
- SQLite suitable for development and small deployments
- Single-server architecture
- In-memory filtering for search

### Scaling Paths
1. **Database**: Migrate to PostgreSQL for concurrent access
2. **Caching**: Add Redis for frequently accessed capsules
3. **Search**: Implement Elasticsearch for full-text search
4. **CDN**: Serve static assets from CDN
5. **Load Balancing**: Add horizontal scaling with load balancer

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | HTML5 | Structure |
| Frontend | CSS3 | Styling |
| Frontend | Vanilla JS | Interactivity |
| Backend | Python 3.10+ | Runtime |
| Backend | Flask 3.0 | Web Framework |
| Backend | SQLAlchemy | ORM |
| Database | SQLite | Data Storage |
| Testing | pytest | Unit Tests |
| CI/CD | GitHub Actions | Automation |

## Design Decisions

### Why Vanilla JavaScript?
- No build step required
- Smaller bundle size
- Direct DOM manipulation for performance
- Simpler deployment

### Why Flask?
- Lightweight and flexible
- Excellent for APIs
- Easy to understand and extend
- Great documentation

### Why SQLite?
- Zero configuration
- Self-contained
- Perfect for single-server deployments
- Easy migration to PostgreSQL if needed

### Why Collage Layout?
- Creates visual interest
- Each capsule feels unique
- Encourages exploration
- Memorable user experience
