#!/bin/bash

# MNEMO Platform - Master Installation Script

set -e  # Exit on error

echo "======================================"
echo "🧠 MNEMO Platform - Installation"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running in virtual environment for Python
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${RED}⚠️  Warning: Not running in a virtual environment${NC}"
        echo "It's recommended to use a virtual environment for Python packages"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Install backend dependencies
install_backend() {
    echo -e "${BLUE}📦 Installing Backend Dependencies...${NC}"
    cd backend

    if command -v python3 &> /dev/null; then
        python3 -m pip install -r requirements.txt
        echo -e "${GREEN}✅ Backend dependencies installed${NC}"
    else
        echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
        exit 1
    fi

    cd ..
    echo ""
}

# Install node agent dependencies
install_node_agent() {
    echo -e "${BLUE}📦 Installing Node Agent Dependencies...${NC}"
    cd node-agent

    if command -v python3 &> /dev/null; then
        python3 -m pip install -r requirements.txt
        echo -e "${GREEN}✅ Node agent dependencies installed${NC}"
    else
        echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
        exit 1
    fi

    cd ..
    echo ""
}

# Install frontend dependencies
install_frontend() {
    echo -e "${BLUE}📦 Installing Frontend Dependencies...${NC}"
    cd frontend

    if command -v npm &> /dev/null; then
        npm install
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${RED}❌ npm not found. Please install Node.js 18+${NC}"
        exit 1
    fi

    cd ..
    echo ""
}

# Main installation menu
main() {
    echo "Select installation option:"
    echo "1) Install ALL components (backend + frontend + node-agent)"
    echo "2) Install Backend only"
    echo "3) Install Frontend only"
    echo "4) Install Node Agent only"
    echo "5) Exit"
    echo ""
    read -p "Enter your choice (1-5): " choice

    case $choice in
        1)
            echo ""
            echo "Installing all components..."
            echo ""
            check_venv
            install_backend
            install_node_agent
            install_frontend
            ;;
        2)
            echo ""
            check_venv
            install_backend
            ;;
        3)
            echo ""
            install_frontend
            ;;
        4)
            echo ""
            check_venv
            install_node_agent
            ;;
        5)
            echo "Installation cancelled."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please run the script again.${NC}"
            exit 1
            ;;
    esac

    echo ""
    echo "======================================"
    echo -e "${GREEN}✅ Installation Complete!${NC}"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Copy backend/.env.example to backend/.env and configure"
    echo "2. Initialize database: cd backend && python scripts/init_db.py"
    echo "3. Start backend: cd backend && uvicorn app.main:app --reload"
    echo "4. Start frontend: cd frontend && npm start"
    echo "5. Configure and run node agent: cd node-agent && python node_agent.py"
    echo ""
    echo "Or use Docker Compose: docker-compose up -d"
    echo ""
}

# Run main function
main
