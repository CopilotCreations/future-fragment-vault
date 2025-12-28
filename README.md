# Time Capsule Web 🕰️

A web application that allows users to create messages, drawings, or code snippets that are locked until a future date. Unlocked capsules are displayed in a surreal, collage-like presentation.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask Version](https://img.shields.io/badge/flask-3.0-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

## Features

- 🔒 **Time-Locked Content** - Create messages that remain hidden until a specified future date
- 📝 **Multiple Content Types** - Support for text, drawings, and code snippets
- 🎨 **Visual Collage** - Unlocked capsules displayed in a surreal, interactive collage
- 🏷️ **Tagging System** - Organize and filter capsules by tags
- ⏳ **Countdown Timers** - See when upcoming capsules will unlock
- 🎯 **Search & Filter** - Find capsules by content, type, or tags

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd future-fragment-vault

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Access the Application

Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
future-fragment-vault/
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment configuration
├── .gitignore               # Git ignore patterns
│
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline configuration
│
├── src/
│   ├── backend/
│   │   ├── __init__.py      # Backend package
│   │   ├── app.py           # Flask application factory
│   │   ├── database.py      # Database models
│   │   └── routes.py        # API endpoints
│   │
│   └── frontend/
│       ├── index.html       # Main HTML page
│       ├── style.css        # Styles and animations
│       └── main.js          # Frontend JavaScript
│
├── tests/
│   ├── __init__.py          # Test package
│   ├── conftest.py          # Pytest fixtures
│   ├── test_app.py          # Application tests
│   ├── test_database.py     # Database model tests
│   └── test_routes.py       # API route tests
│
└── docs/
    ├── ARCHITECTURE.md      # System architecture
    ├── USAGE.md             # User guide
    └── SUGGESTIONS.md       # Future improvements
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/capsules` | List all public capsules |
| GET | `/api/capsules/unlocked` | Get unlocked capsules only |
| GET | `/api/capsules/locked` | Get locked capsules with countdowns |
| GET | `/api/capsules/:id` | Get specific capsule |
| POST | `/api/capsules` | Create new capsule |
| DELETE | `/api/capsules/:id` | Delete a capsule |
| PATCH | `/api/capsules/:id/position` | Update collage position |
| GET | `/api/tags` | Get all unique tags |
| GET | `/api/stats` | Get capsule statistics |

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src/backend --cov-report=html

# Run specific test file
pytest tests/test_routes.py -v
```

## Configuration

Copy `.env.example` to `.env` and customize:

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///time_capsule.db
HOST=0.0.0.0
PORT=5000
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System design and technical details
- [User Guide](docs/USAGE.md) - How to use the application
- [Suggestions](docs/SUGGESTIONS.md) - Future improvements and roadmap

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python, Flask
- **Database**: SQLite (SQLAlchemy ORM)
- **Testing**: pytest, pytest-cov
- **CI/CD**: GitHub Actions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

---

*Lock your memories. Unlock the future.* 🚀
