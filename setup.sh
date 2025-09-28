#!/bin/bash

# Weather Dashboard Setup Script
# This script sets up the modern weather dashboard with ShadCN components

echo "🌤️  Setting up Modern Weather Dashboard..."
echo "=================================================="

# Create project structure
echo "📁 Creating project structure..."
mkdir -p frontend
mkdir -p logs

# Move frontend files
echo "📄 Setting up frontend files..."
cp frontend_index.html frontend/index.html
cp frontend_app.js frontend/app.js

# Create a simple package.json for Node.js dependencies (optional)
cat > package.json << 'EOF'
{
  "name": "weather-dashboard",
  "version": "1.0.0",
  "description": "Modern weather dashboard with ShadCN components",
  "main": "backend_server.py",
  "scripts": {
    "start": "python backend_server.py",
    "dev": "uvicorn backend_server:app --reload --host 0.0.0.0 --port 8000"
  },
  "keywords": ["weather", "dashboard", "fastapi", "shadcn"],
  "author": "Weather Dashboard",
  "license": "MIT"
}
EOF

# Create requirements.txt for Python dependencies
cat > requirements.txt << 'EOF'
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
httpx>=0.25.2
pydantic>=2.5.0
mcp>=1.0.0
EOF

echo "✅ Project structure created!"
echo ""
echo "📋 Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Make sure your .env file has OPENROUTER_API_KEY set"
echo "3. Start the backend server: python backend_server.py"
echo "4. Open http://localhost:8000 in your browser"
echo ""
echo "🚀 Your modern weather dashboard is ready!"
echo "   Backend:  FastAPI server with your weather functions"
echo "   Frontend: Beautiful ShadCN-style components"
echo "   Features: Real-time weather data, caching, responsive design"
