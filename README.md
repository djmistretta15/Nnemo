# 🚀 MAR - Memory Arbitrage Router

> **VRAM-aware GPU placement engine for intelligent workload distribution**

MAR (Memory Arbitrage Router) is a production-ready system that functions as the intelligence layer for GPU workload placement, deciding which GPU nodes receive workloads based on memory efficiency, locality, and real-time telemetry.

## 🎯 Core Features

### Smart Placement Algorithm
- **VRAM-aware scoring** - Evaluates nodes based on available VRAM headroom
- **Bandwidth optimization** - Considers memory bandwidth in placement decisions
- **Latency awareness** - Factors in network latency for optimal performance
- **Regional filtering** - Supports preferred region placement

### Real-time Telemetry
- Track GPU utilization, VRAM usage, and temperature
- Automatic VRAM estimate updates
- Historical telemetry data retention

### Production-Ready Architecture
- Full REST API with OpenAPI documentation
- JWT authentication with refresh tokens
- PostgreSQL database with Alembic migrations
- Comprehensive test suite

## 📁 Project Structure

```
MAR/
├── backend/              # FastAPI backend
│   ├── alembic/         # Database migrations
│   ├── app/
│   │   ├── api/v1/      # REST API endpoints
│   │   ├── core/        # Config, security, dependencies
│   │   ├── db/          # Database session and base
│   │   ├── models/      # SQLAlchemy 2.x ORM models
│   │   ├── schemas/     # Pydantic v2 schemas
│   │   ├── services/    # Business logic (placement algorithm)
│   │   ├── tests/       # Pytest test suite
│   │   └── main.py      # FastAPI application
│   ├── pyproject.toml   # Python dependencies
│   └── alembic.ini      # Alembic configuration
│
├── frontend/            # Next.js 14+ App Router frontend
│   ├── app/            # Next.js app directory
│   │   ├── auth/       # Login & registration pages
│   │   ├── dashboard/  # Dashboard pages
│   │   ├── layout.tsx  # Root layout with navigation
│   │   └── page.tsx    # Landing page
│   ├── components/     # React components
│   ├── lib/            # API client & auth utilities
│   └── package.json    # Node dependencies
│
├── infra/              # Infrastructure configuration
│   ├── env.example.backend
│   └── env.example.frontend
│
├── docker-compose.yml  # Docker orchestration
└── README.md          # This file
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      MAR System Architecture                 │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Next.js    │  ← React Query + Tailwind CSS
    │   Frontend   │  ← JWT Auth + API Client
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │   FastAPI    │  ← REST API + OpenAPI Docs
    │   Backend    │  ← JWT Authentication
    └──────┬───────┘
           │
    ┌──────▼───────────────────────────────┐
    │         Service Layer                │
    │  ┌────────────────────────────────┐  │
    │  │   Placement Service            │  │
    │  │   • VRAM scoring algorithm     │  │
    │  │   • Node selection logic       │  │
    │  │   • Region filtering           │  │
    │  └────────────────────────────────┘  │
    │  ┌────────────────────────────────┐  │
    │  │   Node & Telemetry Services    │  │
    │  └────────────────────────────────┘  │
    └──────────────┬───────────────────────┘
                   │
    ┌──────────────▼───────────────┐
    │      PostgreSQL 15           │
    │  • Organizations & Users     │
    │  • Nodes & Telemetry        │
    │  • Placement Requests       │
    │  • Placement Decisions      │
    └──────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + Python 3.11 + SQLAlchemy 2.x |
| **Database** | PostgreSQL 15 + Alembic migrations |
| **Frontend** | Next.js 14 + TypeScript + Tailwind CSS |
| **API Client** | React Query + Axios |
| **Auth** | JWT + Refresh Tokens |
| **Deployment** | Docker + Docker Compose |

## 🏃 Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.11+ for local backend dev
- (Optional) Node.js 18+ for local frontend dev

### 1. Clone Repository

```bash
git clone https://github.com/djmistretta15/Nnemo.git
cd Nnemo
```

### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up --build

# The system will:
# 1. Start PostgreSQL database
# 2. Run Alembic migrations
# 3. Start FastAPI backend on port 8000
# 4. Start Next.js frontend on port 3000
```

### 3. Access Services

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Database:** localhost:5432

### 4. Create Your First Account

1. Navigate to http://localhost:3000
2. Click "Sign Up"
3. Fill in organization name, email, and password
4. You'll be automatically logged in and redirected to the dashboard

## 📖 API Documentation

### Core Endpoints

#### Authentication
```bash
# Register new organization + admin user
POST /api/v1/auth/register
{
  "organization_name": "Acme Corp",
  "email": "admin@acme.com",
  "password": "securepass123",
  "full_name": "John Doe"
}

# Login
POST /api/v1/auth/login
{
  "email": "admin@acme.com",
  "password": "securepass123"
}

# Get current user info
GET /api/v1/auth/me
Authorization: Bearer <token>
```

#### Nodes
```bash
# Create a GPU node
POST /api/v1/nodes
Authorization: Bearer <token>
{
  "name": "Node-GPU-A100-01",
  "provider_name": "AWS",
  "region": "us-east-1",
  "gpu_model": "A100",
  "vram_gb_total": 80.0,
  "memory_bandwidth_gbps": 1935.0,
  "network_latency_ms_estimate": 2.5
}

# List nodes
GET /api/v1/nodes?region=us-east-1&active=true
Authorization: Bearer <token>

# Get node details
GET /api/v1/nodes/{id}
Authorization: Bearer <token>

# Update node
PATCH /api/v1/nodes/{id}
Authorization: Bearer <token>
{
  "is_active": false
}
```

#### Telemetry
```bash
# Push telemetry data (updates node VRAM estimate)
POST /api/v1/nodes/{node_id}/telemetry
Authorization: Bearer <token>
{
  "vram_gb_free": 60.0,
  "utilization_percent": 25.0,
  "temperature_c": 65.0
}

# Get node telemetry history
GET /api/v1/nodes/{node_id}/telemetry?limit=100
Authorization: Bearer <token>
```

#### Model Profiles
```bash
# Create model profile
POST /api/v1/model-profiles
Authorization: Bearer <token>
{
  "name": "Llama-2-13B",
  "suggested_min_vram_gb": 24.0,
  "suggested_batch_size": 4,
  "category": "llm"
}

# List model profiles
GET /api/v1/model-profiles
Authorization: Bearer <token>
```

#### Placement Requests
```bash
# Create placement request (returns best node)
POST /api/v1/placement/requests
Authorization: Bearer <token>
{
  "model_name": "Llama-2-13B",
  "required_vram_gb": 24.0,
  "preferred_region": "us-east-1",
  "priority": "normal"
}

# Response includes chosen node and reasoning:
{
  "request": { ... },
  "decision": {
    "id": 1,
    "chosen_node_id": 5,
    "reason": "Node 'Node-GPU-A100-01' selected with 56.0GB VRAM headroom...",
    "estimated_fit_score": 87.5,
    "node": {
      "id": 5,
      "name": "Node-GPU-A100-01",
      "gpu_model": "A100",
      "vram_gb_total": 80.0,
      "vram_gb_free_estimate": 80.0,
      ...
    }
  }
}

# List placement requests
GET /api/v1/placement/requests
Authorization: Bearer <token>
```

#### Public API (Stateless Quote)
```bash
# Get placement quote without persisting
POST /api/v1/public/placement/quote
X-API-Key: your-api-key-here
{
  "model_name": "Llama-2-13B",
  "required_vram_gb": 24.0,
  "preferred_region": "us-east-1"
}
```

**Full API Documentation:** http://localhost:8000/docs

## 🧮 Placement Algorithm

The VRAM-aware placement algorithm scores nodes using weighted criteria:

```
score = (vram_gb_free_estimate - required_vram_gb) * 0.5
        + memory_bandwidth_gbps * 0.3
        - network_latency_ms_estimate * 0.2
```

Normalized to 0-100 range.

### Scoring Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| **VRAM Headroom** | 0.5 | Extra VRAM beyond requirements |
| **Memory Bandwidth** | 0.3 | GB/s throughput |
| **Network Latency** | -0.2 | ms (penalty for high latency) |

### Example Match Process

1. **Gather Candidates**
   - Filter: `is_active == True`
   - Filter: `vram_gb_free_estimate >= required_vram_gb`
   - Filter: `region == preferred_region` (if specified)

2. **Score Each Node**
   - Calculate weighted score
   - Track best fit

3. **Select Winner**
   - Return highest scoring node
   - Persist PlacementRequest + PlacementDecision
   - Return full details with reasoning

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest app/tests/

# Run specific test file
pytest app/tests/test_placement_logic.py -v

# Run with coverage
pytest --cov=app app/tests/
```

### Test Suite Includes

- ✅ **Authentication Flow** - Register, login, JWT validation
- ✅ **Node Management** - Create, list, update nodes
- ✅ **Telemetry Updates** - Push telemetry, verify VRAM updates
- ✅ **Placement Logic** - Algorithm correctness, region filtering, edge cases

## 🔧 Configuration

### Backend Environment Variables

Copy `infra/env.example.backend` to `backend/.env`:

```bash
DATABASE_URL=postgresql://mar_user:mar_password@localhost:5432/mar_db
JWT_SECRET_KEY=your-secret-key-change-in-production-minimum-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend Environment Variables

Copy `infra/env.example.frontend` to `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_V1_PREFIX=/api/v1
```

## 📋 Database Schema

### Core Tables

```sql
-- Users & Organizations
users (id, email, hashed_password, full_name, role, organization_id)
organizations (id, name, description)

-- GPU Nodes & Telemetry
nodes (id, organization_id, name, provider_name, region, gpu_model, 
       vram_gb_total, vram_gb_free_estimate, memory_bandwidth_gbps,
       network_latency_ms_estimate, is_active)
node_telemetry (id, node_id, vram_gb_free, utilization_percent, 
                temperature_c, collected_at)

-- Model Profiles
model_profiles (id, name, suggested_min_vram_gb, suggested_batch_size, category)

-- Placement System
placement_requests (id, user_id, organization_id, model_name, 
                    required_vram_gb, preferred_region, priority)
placement_decisions (id, placement_request_id, chosen_node_id, 
                     reason, estimated_fit_score)
```

## 🚢 Deployment

### Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup

Set these in production:

- `DATABASE_URL` - Production PostgreSQL connection
- `JWT_SECRET_KEY` - Strong random secret (min 32 chars)
- `CORS_ORIGINS` - Production frontend URL

## 🔒 Security Features

- ✅ JWT authentication with refresh tokens
- ✅ Password hashing with bcrypt
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ CORS configuration
- ✅ Input validation with Pydantic
- ✅ Proper error handling

## 📊 Demo Workflow

### 1. Register Organization & User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Demo Corp",
    "email": "demo@example.com",
    "password": "demopass123",
    "full_name": "Demo User"
  }'
```

### 2. Create GPU Nodes
```bash
curl -X POST http://localhost:8000/api/v1/nodes \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPU-Node-A100-01",
    "provider_name": "AWS",
    "region": "us-east-1",
    "gpu_model": "A100",
    "vram_gb_total": 80.0,
    "memory_bandwidth_gbps": 1935.0,
    "network_latency_ms_estimate": 2.5
  }'
```

### 3. Push Telemetry
```bash
curl -X POST http://localhost:8000/api/v1/nodes/1/telemetry \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "vram_gb_free": 60.0,
    "utilization_percent": 25.0,
    "temperature_c": 65.0
  }'
```

### 4. Create Model Profile
```bash
curl -X POST http://localhost:8000/api/v1/model-profiles \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Llama-2-13B",
    "suggested_min_vram_gb": 24.0,
    "suggested_batch_size": 4,
    "category": "llm"
  }'
```

### 5. Make Placement Request
```bash
curl -X POST http://localhost:8000/api/v1/placement/requests \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "Llama-2-13B",
    "priority": "normal"
  }'
```

### 6. View Results in Dashboard

Visit http://localhost:3000/dashboard to see:
- Active nodes
- Average free VRAM
- Recent placements
- Placement decision details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

**Built as a complete production-shaped MVP demonstrating VRAM-aware GPU placement intelligence.**

*MAR - Put Jobs Where VRAM Fits Best.*
