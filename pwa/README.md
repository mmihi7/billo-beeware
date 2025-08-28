# Billo PWA

A Progressive Web Application for Billo Restaurant Management System.

## Getting Started

### Prerequisites
- Python 3.9+
- Poetry (for dependency management)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Start the development server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
4. Open http://localhost:8000 in your browser

## Development

### Project Structure
- `app/` - Main application code
  - `routers/` - API route handlers
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)

### Testing
Run tests with:
```bash
poetry run pytest
```
