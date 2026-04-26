# Contributing to ARCS

Thank you for your interest in contributing to the AI-Driven Ransomware Detection & Containment System (ARCS)!

## How to Contribute

### Reporting Bugs
1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your environment (OS, Python version, Node version)

### Suggesting Features
1. Open an issue with the `enhancement` label
2. Describe the feature and its benefits
3. Provide examples or mockups if possible

### Pull Requests
1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- MongoDB Atlas account
- Supabase account

### Setup Steps
1. Clone the repository
2. Copy `.env.example` files and configure
3. Install dependencies:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```
4. Start services:
   ```bash
   docker-compose up -d  # Kafka & Zookeeper
   cd backend && python main.py
   cd frontend && npm run dev
   ```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions focused and small

### JavaScript/React
- Use ES6+ features
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable

### Commits
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Reference issues when applicable

## Testing
- Write tests for new features
- Ensure existing tests pass
- Test on multiple browsers (for frontend)

## Questions?
Open an issue or reach out to the maintainers.

Thank you for contributing! 🚀
