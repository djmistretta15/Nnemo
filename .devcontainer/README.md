# GitHub Codespaces Configuration for MAR

This directory contains the configuration for GitHub Codespaces, enabling one-click development environment setup.

## What's Configured

### Development Environment
- **Python 3.11** with FastAPI, SQLAlchemy, and testing tools
- **Node.js 18** for Next.js frontend development
- **Docker-in-Docker** for running docker-compose within Codespaces
- **PostgreSQL 15** database

### VS Code Extensions
- Python (Pylance, Black formatter, testing)
- TypeScript/JavaScript (ESLint, Prettier)
- Tailwind CSS IntelliSense
- PostgreSQL database tools
- REST client for API testing
- Docker tools
- GitLens

### Port Forwarding
- **3000**: Frontend (Next.js) - Auto-forwarded with notification
- **8000**: Backend API (FastAPI) - Auto-forwarded with notification
- **5432**: PostgreSQL Database - Auto-forwarded silently

## Quick Start in Codespaces

1. **Open in Codespaces**
   - Click the green "Code" button on GitHub
   - Select "Codespaces" tab
   - Click "Create codespace on [branch]"

2. **Wait for Setup**
   - Codespace will automatically build the container
   - All dependencies will be installed
   - Services will be configured

3. **Start the Application**
   ```bash
   docker-compose up --build
   ```

4. **Access the Services**
   - Frontend: Click the "Ports" tab and open port 3000
   - Backend API: Open port 8000 to access FastAPI docs at `/docs`
   - Database: Available on port 5432

## Development Workflow

### Backend Development
```bash
# Navigate to backend directory
cd backend

# Run migrations
alembic upgrade head

# Run tests
pytest app/tests/

# Start backend only (if not using docker-compose)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if needed)
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it mar-postgres psql -U mar_user -d mar_db

# Or use the SQLTools extension in VS Code
```

## Environment Variables

The following environment variables are pre-configured in `devcontainer.json`:

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: JWT secret for authentication
- `CORS_ORIGINS`: Allowed CORS origins

To customize, edit `.devcontainer/devcontainer.json` or create a `.env` file.

## Troubleshooting

### Services not starting
```bash
# Rebuild containers
docker-compose down -v
docker-compose up --build
```

### Port already in use
```bash
# Stop all services
docker-compose down

# Check running containers
docker ps
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres
```

### Frontend build issues
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

## VS Code Tasks

The following tasks are available in the Command Palette (Cmd/Ctrl+Shift+P):

- **Tasks: Run Task**
  - Start All Services (docker-compose up)
  - Run Backend Tests
  - Run Frontend Dev Server

## API Testing

Use the REST Client extension to test API endpoints:

1. Create a `.http` file in your workspace
2. Add requests:
   ```http
   ### Register User
   POST http://localhost:8000/api/v1/auth/register
   Content-Type: application/json

   {
     "organization_name": "Test Org",
     "email": "test@example.com",
     "password": "testpass123",
     "full_name": "Test User"
   }

   ### Get Nodes
   GET http://localhost:8000/api/v1/nodes
   Authorization: Bearer {{access_token}}
   ```

## Next Steps

1. Review the main README.md for complete documentation
2. Explore the API documentation at http://localhost:8000/docs
3. Access the frontend at http://localhost:3000
4. Start developing!

## Customization

To customize this Codespace:

1. Edit `.devcontainer/devcontainer.json`
2. Add VS Code extensions to the `extensions` array
3. Modify `postCreateCommand` for additional setup steps
4. Update `features` to add development tools

For more information, see [GitHub Codespaces documentation](https://docs.github.com/en/codespaces).
