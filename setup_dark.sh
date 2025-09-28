#!/bin/bash

# Weather Dashboard Dark Mode Setup Script
# Sets up the modern weather dashboard with dark mode support

echo "🌙 Setting up Dark Mode Weather Dashboard..."
echo "=================================================="

# Create project structure
echo "📁 Creating project structure..."
mkdir -p frontend
mkdir -p logs
mkdir -p static

# Move frontend files to correct locations
echo "📄 Setting up dark mode frontend files..."
cp dark_mode_index.html frontend/index.html
cp dark_mode_app.js frontend/app.js

# Create enhanced package.json
cat > package.json << 'EOF'
{
  "name": "weather-dashboard-dark",
  "version": "2.0.0",
  "description": "Modern weather dashboard with dark mode and theme toggle",
  "main": "run_server.py",
  "scripts": {
    "start": "python run_server.py",
    "dev": "uvicorn run_server:app --reload --host 0.0.0.0 --port 8000",
    "serve": "python run_server.py"
  },
  "keywords": ["weather", "dashboard", "fastapi", "dark-mode", "theme-toggle"],
  "author": "Weather Dashboard Team",
  "license": "MIT",
  "features": {
    "dark_mode": true,
    "theme_toggle": true,
    "responsive_design": true,
    "glassmorphism": true,
    "enhanced_caching": true
  }
}
EOF

# Create enhanced requirements.txt
cat > requirements.txt << 'EOF'
# Core dependencies
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
httpx>=0.25.2
pydantic>=2.5.0

# MCP server (your weather functions)
# Note: Make sure your weather.py file is in the same directory

# Optional: Development dependencies
# black>=23.0.0
# pytest>=7.0.0
# pytest-asyncio>=0.21.0
EOF

# Create .env template
cat > .env.example << 'EOF'
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# Server Configuration (optional)
# HOST=0.0.0.0
# PORT=8000
# DEBUG=true

# Theme Configuration (optional)
# DEFAULT_THEME=dark
EOF

# Create a simple .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv/

# Environment variables
.env

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Cache
*.cache
.pytest_cache/
EOF

echo "✅ Dark mode project structure created!"
echo ""
echo "🌙 DARK MODE FEATURES:"
echo "   ✨ Beautiful dark theme (default)"
echo "   🎛️  Theme toggle button (top-right)"
echo "   🌓 Persistent theme preference"
echo "   📱 Enhanced responsive design"
echo "   🔄 Smooth theme transitions"
echo "   💨 Glassmorphism effects"
echo ""
echo "📋 Next steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Copy your .env file or create from .env.example"
echo "3. Make sure your weather.py is in the project root"
echo "4. Start the server: python run_server.py"
echo "5. Open http://localhost:8000 (starts in DARK MODE)"
echo ""
echo "🎨 THEME CONTROLS:"
echo "   • Click the 🌙/☀️ button in top-right to toggle themes"
echo "   • Dark mode is the default (easier on eyes)"
echo "   • Theme preference is saved in browser"
echo ""
echo "🚀 Your dark mode weather dashboard is ready!"
echo "   Backend:  Enhanced FastAPI with theme support"
echo "   Frontend: Beautiful dark mode + light mode toggle"
echo "   Default:  Dark mode active on startup"
