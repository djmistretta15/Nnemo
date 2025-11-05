#!/bin/bash

# MNEMO Platform Quick Start Script

echo "=================================="
echo "🧠 MNEMO Platform - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env (please edit with your settings)"
fi

# Start services
echo ""
echo "🚀 Starting MNEMO services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if backend is up
echo ""
echo "🔍 Checking backend health..."
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend is healthy!"
else
    echo "⚠️  Backend may still be starting. Please wait a moment."
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
docker-compose exec -T backend python scripts/init_db.py << EOF
y
EOF

echo ""
echo "=================================="
echo "✅ MNEMO Platform is running!"
echo "=================================="
echo ""
echo "Access points:"
echo "  • Backend API:  http://localhost:8000"
echo "  • API Docs:     http://localhost:8000/docs"
echo "  • Frontend:     http://localhost:3000"
echo ""
echo "Test accounts:"
echo "  • Admin:    admin@mnemo.io / admin123"
echo "  • Provider: provider@example.com / provider123"
echo "  • Client:   client@example.com / client123"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo ""
