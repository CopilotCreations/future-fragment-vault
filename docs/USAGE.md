# Time Capsule Web - User Guide

Welcome to Time Capsule Web! This guide will help you understand how to use the application to create and discover time-locked messages.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Creating a Time Capsule](#creating-a-time-capsule)
4. [Viewing the Collage](#viewing-the-collage)
5. [Upcoming Capsules](#upcoming-capsules)
6. [Search and Filtering](#search-and-filtering)
7. [Content Types](#content-types)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

Time Capsule Web allows you to create messages, drawings, or code snippets that remain locked until a future date you specify. Once the unlock date arrives, your capsule becomes visible in the community collage, creating a visual tapestry of memories from the past.

### Key Features

- **🔒 Time-Locked Content**: Messages remain hidden until the unlock date
- **🎨 Multiple Content Types**: Text, drawings, and code snippets
- **🖼️ Visual Collage**: Unlocked capsules displayed in a surreal, interactive collage
- **🏷️ Tagging System**: Organize and filter capsules by tags
- **⏳ Countdown Timers**: See when upcoming capsules will unlock

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd future-fragment-vault
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**:
   ```bash
   python run.py
   ```

6. **Open your browser**:
   Navigate to `http://localhost:5000`

---

## Creating a Time Capsule

### Step-by-Step Guide

1. **Navigate to Create View**
   - Click the "Create Capsule" button in the navigation bar

2. **Fill in the Details**

   | Field | Description | Required |
   |-------|-------------|----------|
   | Title | A name for your capsule | Yes |
   | Content Type | Text, Drawing, or Code | Yes |
   | Your Message | The content to be locked | Yes |
   | Your Name | How you want to be credited | Yes |
   | Unlock Date | When the capsule opens | Yes |
   | Tags | Categories for filtering | No |
   | Public | Whether others can see it | No |

3. **Choose Your Content Type**
   - **Text**: Write a message or story
   - **Drawing**: Use the canvas to draw
   - **Code**: Share a code snippet with syntax highlighting

4. **Set the Unlock Date**
   - Must be in the future (at least 5 minutes)
   - Consider meaningful dates: birthdays, anniversaries, future milestones

5. **Launch Your Capsule**
   - Click "🚀 Launch Capsule"
   - Your capsule is now locked until the unlock date!

### Tips for Great Capsules

- **Be personal**: Write to your future self or loved ones
- **Use meaningful dates**: Anniversaries, graduations, life milestones
- **Add context**: Include details that will make sense later
- **Use tags**: Help others discover related capsules

---

## Viewing the Collage

The Collage view is the heart of Time Capsule Web, displaying all unlocked capsules in a visually dynamic layout.

### Features

- **Interactive Fragments**: Click on any capsule to view its full content
- **Random Positioning**: Each capsule has a unique position and rotation
- **Hover Effects**: Capsules highlight when you hover over them
- **Color Coding**: Different content types have different accent colors

### Reading a Capsule

1. Click on any fragment in the collage
2. A modal opens showing:
   - Full title
   - Creator name
   - Unlock date
   - Complete content
   - Associated tags

---

## Upcoming Capsules

The Upcoming view shows capsules that are still locked, building anticipation for future reveals.

### Information Displayed

- **Title**: The capsule's name
- **Creator**: Who created it
- **Countdown**: Days, hours, and minutes remaining
- **Unlock Date**: Exact date and time of reveal

### Why View Upcoming?

- See what's coming next
- Anticipate community reveals
- Plan for meaningful dates

---

## Search and Filtering

Find specific capsules using the powerful search and filter system.

### Search

- Type in the search box to find capsules by title or content
- Search is case-insensitive
- Results update as you type

### Filters

| Filter | Options | Description |
|--------|---------|-------------|
| Content Type | All, Text, Drawing, Code | Filter by content type |
| Tags | Dynamic list | Filter by assigned tags |

### Combining Filters

Filters work together:
- Search for "birthday" + filter by "Text" = all text capsules containing "birthday"

---

## Content Types

### Text Capsules 📝

Perfect for:
- Letters to your future self
- Predictions
- Memories and stories
- Wishes and hopes

### Drawing Capsules 🎨

Features:
- Color picker for brush color
- Adjustable brush size
- Clear canvas button
- Touch support for tablets

Perfect for:
- Sketches and doodles
- Visual memories
- Art pieces
- Diagrams

### Code Capsules 💻

Features:
- Language selector (JavaScript, Python, HTML, CSS)
- Monospace font for readability
- Syntax preserved

Perfect for:
- Code experiments
- Programming predictions
- Algorithm snapshots
- Learning milestones

---

## API Reference

For developers who want to integrate with Time Capsule Web.

### Base URL

```
http://localhost:5000/api
```

### Endpoints

#### Get All Capsules
```http
GET /api/capsules
```

Query Parameters:
- `tag`: Filter by tag
- `search`: Search in title/content
- `content_type`: Filter by type
- `limit`: Max results (default: 50)
- `offset`: Skip results (default: 0)

#### Get Unlocked Capsules
```http
GET /api/capsules/unlocked
```

#### Get Locked Capsules
```http
GET /api/capsules/locked
```

#### Get Specific Capsule
```http
GET /api/capsules/{id}
```

#### Create Capsule
```http
POST /api/capsules
Content-Type: application/json

{
    "title": "My Capsule",
    "content": "Hello, future!",
    "content_type": "text",
    "creator_name": "John Doe",
    "unlock_date": "2025-12-25T00:00:00Z",
    "tags": ["holiday", "personal"],
    "is_public": true
}
```

#### Delete Capsule
```http
DELETE /api/capsules/{id}
```

#### Get Statistics
```http
GET /api/stats
```

Response:
```json
{
    "total": 42,
    "unlocked": 30,
    "locked": 12
}
```

#### Get All Tags
```http
GET /api/tags
```

---

## Troubleshooting

### Common Issues

#### "Unlock date must be in the future"
- The unlock date must be at least 5 minutes from now
- Check your timezone settings
- Make sure the date picker shows the correct date

#### Capsule Not Appearing
- Refresh the page
- Check if the capsule is public
- Verify the unlock date has passed

#### Drawing Not Saving
- Make sure you've actually drawn something
- Try a different browser if issues persist
- Check console for JavaScript errors

#### Server Won't Start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is available
- Verify Python version is 3.10+

### Getting Help

If you encounter issues not covered here:
1. Check the [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
2. Review the [SUGGESTIONS.md](SUGGESTIONS.md) for known limitations
3. Open an issue on GitHub

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Escape` | Close modal |
| `Tab` | Navigate form fields |
| `Enter` | Submit form (when in form) |

---

## Browser Support

| Browser | Minimum Version |
|---------|-----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

---

## Privacy & Data

- **Local Storage**: The application uses SQLite, storing all data locally
- **No Tracking**: No analytics or tracking scripts
- **Content Privacy**: Locked capsules are never exposed until unlock date
- **Public/Private**: You control who can see your capsules

---

*Thank you for using Time Capsule Web! We hope your messages bring joy when they're unlocked in the future.* 🕰️
