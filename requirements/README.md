# MNEMO Requirements

This directory contains information about all project dependencies.

## 📦 Requirements Files Locations

### Backend Dependencies
**Location:** `../backend/requirements.txt`

Python packages for FastAPI backend:
- FastAPI & Uvicorn (web framework)
- PostgreSQL & SQLAlchemy (database)
- JWT & Bcrypt (authentication)
- Stripe & Web3 (payments)
- WebSockets (real-time)
- Pydantic (validation)
- Testing tools

**Install:**
```bash
cd backend
pip install -r requirements.txt
```

---

### Node Agent Dependencies
**Location:** `../node-agent/requirements.txt`

Python packages for system monitoring agent:
- psutil (system monitoring)
- requests (HTTP client)
- nvidia-ml-py (optional GPU monitoring)

**Install:**
```bash
cd node-agent
pip install -r requirements.txt
```

---

### Frontend Dependencies
**Location:** `../frontend/package.json`

Node.js packages for React frontend:
- React 18 & TypeScript
- Axios (API client)
- React Router (navigation)
- Recharts (charts)

**Install:**
```bash
cd frontend
npm install
```

---

## 🚀 Quick Installation

### Option 1: Interactive Install Script
```bash
./install.sh
```

### Option 2: Make Commands
```bash
# Install everything
make install-all

# Or install individually
make install-backend
make install-frontend
make install-agent
```

### Option 3: Docker (Recommended)
```bash
docker-compose up -d
```
No manual dependency installation needed!

---

## 📋 System Requirements

### Backend & Node Agent
- Python 3.11 or higher
- pip (Python package manager)
- PostgreSQL 15 (or use Docker)

### Frontend
- Node.js 18 or higher
- npm (comes with Node.js)

### Optional
- Docker & Docker Compose (for containerized deployment)
- NVIDIA GPU drivers (for GPU monitoring in node agent)

---

## 🔧 Development Setup

1. **Create Python virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install all dependencies:**
   ```bash
   make install-all
   ```

3. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   ```

4. **Initialize database:**
   ```bash
   cd backend
   python scripts/init_db.py
   ```

5. **Start services:**
   ```bash
   # Backend
   make backend

   # Frontend (in another terminal)
   make frontend

   # Node agent (in another terminal)
   make agent
   ```

---

## 📦 Dependency Updates

To update dependencies:

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update

# Node agent
cd node-agent
pip install --upgrade -r requirements.txt
```

---

## 🐛 Troubleshooting

### Python package conflicts
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node modules issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### PostgreSQL connection errors
- Check if PostgreSQL is running
- Verify DATABASE_URL in backend/.env
- Or use Docker: `docker-compose up postgres`

### GPU monitoring not working
```bash
# Install nvidia-ml-py
pip install nvidia-ml-py

# Verify NVIDIA drivers
nvidia-smi
```

---

## 📚 Additional Resources

- **Backend docs:** ../backend/README.md
- **Frontend docs:** ../frontend/README.md
- **Node agent docs:** ../node-agent/README.md
- **Main README:** ../README.md
