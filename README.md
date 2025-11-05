# 🧠 MNEMO - Memory Arbitrage Platform

> **Transform idle VRAM and RAM into revenue. The Airbnb for memory.**

MNEMO is a VRAM/RAM-as-a-Service marketplace that captures idle memory from data centers, edge clusters, and consumer machines (Mist Nodes), then rents it to AI teams needing burst capacity.

## 🎯 Core Innovation

**Geographic clustering** creates local memory meshes that outperform AWS/GCP through proximity (<1ms latency vs 10-30ms to cloud), enabling community-owned infrastructure with network effects.

Unlike GPU marketplaces that rent whole machines, Mnemo arbitrages the **memory layer itself** - an unfilled market niche.

## 🚀 Features

### For Memory Providers (Earn Money)
- 💰 **Monetize Idle Resources** - Earn $50-150/month from unused RAM/VRAM
- 📊 **Real-Time Dashboard** - Monitor earnings, utilization, and performance
- 🔒 **Secure & Isolated** - Sandboxed memory allocation
- ⚡ **Automatic Discovery** - Set-and-forget node agent

### For Memory Renters (Save Money)
- 💵 **40-60% Cost Savings** vs AWS/GCP
- 🌍 **Geographic Proximity** - <1ms latency to local clusters
- 🎯 **Smart Matching** - AI-powered node selection
- 📈 **Elastic Scaling** - Pay only for what you use

## 📁 Project Structure

```
Nnemo/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # REST API endpoints
│   │   ├── auth/        # JWT authentication
│   │   ├── models/      # SQLAlchemy models
│   │   ├── services/    # Business logic (matching, etc.)
│   │   ├── config.py    # Configuration management
│   │   ├── database.py  # Database connection
│   │   └── main.py      # FastAPI application
│   ├── scripts/         # Database init, migrations
│   ├── Dockerfile       # Backend container
│   └── requirements.txt
│
├── frontend/            # React + TypeScript UI
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── App.tsx
│   └── package.json
│
├── node-agent/          # Python agent for providers
│   ├── node_agent.py    # Main agent script
│   ├── node_config.example.json
│   ├── requirements.txt
│   └── README.md
│
├── docs/                # Documentation
├── docker-compose.yml   # Docker orchestration
└── README.md           # This file
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + Python 3.11 |
| **Database** | PostgreSQL 15 |
| **Frontend** | React 18 + TypeScript |
| **Node Agent** | Python + psutil + pynvml |
| **Auth** | JWT + bcrypt |
| **Payments** | Stripe + Web3 |
| **Deployment** | Docker + Kubernetes |

## 🏃 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend development)
- PostgreSQL 15 (or use Docker)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Nnemo.git
cd Nnemo
```

### 2. Start with Docker Compose

```bash
# Copy environment file
cp backend/.env.example backend/.env

# Edit .env with your settings
nano backend/.env

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python scripts/init_db.py
```

### 3. Access Services

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **Database:** localhost:5432

### 4. Test Accounts (after seeding)

```
Admin:    admin@mnemo.io / admin123
Provider: provider@example.com / provider123
Client:   client@example.com / client123
```

## 📋 Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb mnemo_db
python scripts/init_db.py

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Node Agent Setup

```bash
cd node-agent

# Install dependencies
pip install -r requirements.txt

# Configure agent
cp node_config.example.json node_config.json
nano node_config.json

# Run agent
python node_agent.py
```

## 🔑 API Authentication

All API endpoints require authentication via:

1. **JWT Token** (for web/mobile apps)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "client@example.com", "password": "client123"}'
```

2. **API Key** (for node agents)
```bash
curl -X GET http://localhost:8000/api/nodes \
  -H "X-API-Key: your_api_key_here"
```

## 📖 API Documentation

### Core Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

#### Nodes
- `POST /api/nodes/register` - Register a new node
- `POST /api/nodes/{id}/heartbeat` - Send node metrics
- `GET /api/nodes` - List all nodes
- `GET /api/nodes/{id}` - Get node details
- `PUT /api/nodes/{id}` - Update node config
- `DELETE /api/nodes/{id}` - Deactivate node

#### Marketplace
- `GET /api/marketplace` - Browse available memory
- `POST /api/marketplace/request` - Request memory with matching

#### Contracts
- `POST /api/contracts/create` - Create memory contract
- `GET /api/contracts` - List contracts
- `GET /api/contracts/{id}` - Get contract details
- `POST /api/contracts/{id}/settle` - Complete contract
- `POST /api/contracts/{id}/extend` - Extend contract

**Full API docs:** http://localhost:8000/docs

## 🧮 Matching Algorithm

MNEMO uses a sophisticated scoring system (max ~300 points):

| Factor | Weight | Description |
|--------|--------|-------------|
| **Proximity** | 0-100 (3x if prefer_local) | Distance-based scoring |
| **Price** | 0-50 | Lower price = higher score |
| **Reliability** | 0-50 | Based on uptime score |
| **Capacity** | 0-30 | Overcapacity = better failover |
| **Node Type** | +20 | Bonus for mist nodes |

### Example Match Request

```bash
curl -X POST http://localhost:8000/api/marketplace/request \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ram_gb": 32,
    "vram_gb": 12,
    "duration_sec": 3600,
    "max_price_per_gb_sec": 0.000002,
    "prefer_local": true,
    "max_distance_km": 100
  }'
```

## 🔧 Configuration

### Backend Configuration (`.env`)

```bash
# Database
DATABASE_URL=postgresql://mnemo:password@localhost:5432/mnemo_db

# JWT
JWT_SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Payments
STRIPE_SECRET_KEY=sk_test_...
ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# Platform
PLATFORM_FEE_PERCENT=5.0
```

### Node Agent Configuration

```json
{
  "api_url": "http://localhost:8000",
  "api_key": "your_api_key_here",
  "node_type": "mist_node",
  "name": "MyNode_RTX4090",
  "region": "us-east-1",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "price_per_gb_sec": 0.0000008,
  "bandwidth_mbps": 1000,
  "base_latency_ms": 1.0,
  "heartbeat_interval": 60
}
```

## 📊 Database Schema

### Core Tables

- **users** - User accounts
- **nodes** - Memory providers
- **clients** - Memory renters
- **contracts** - Rental agreements
- **transactions** - Payment records
- **node_metrics** - Time-series metrics
- **clusters** - Geographic clusters

See `backend/app/models/models.py` for full schema.

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_test.py
```

## 🚢 Deployment

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to Kubernetes
kubectl apply -f k8s/

# Or deploy to cloud
# AWS ECS, GCP Cloud Run, Azure Container Apps, etc.
```

### Environment Variables

Set these in production:

- `DATABASE_URL` - Production PostgreSQL connection
- `JWT_SECRET_KEY` - Strong random secret
- `STRIPE_SECRET_KEY` - Production Stripe key
- `CORS_ORIGINS` - Production frontend URL

## 📈 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
pg_isready -h localhost -p 5432
```

### Metrics (Prometheus)

Metrics exposed at `/metrics`:
- Request count
- Response time
- Active contracts
- Node availability

## 🔒 Security

- JWT tokens expire after 24 hours
- API keys are hashed in database
- HTTPS enforced in production
- Rate limiting on all endpoints
- SQL injection prevention via SQLAlchemy
- CORS restricted to known origins

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🆘 Support

- **Documentation:** [docs.mnemo.io](https://docs.mnemo.io)
- **Discord:** [discord.gg/mnemo](https://discord.gg/mnemo)
- **GitHub Issues:** [github.com/mnemo/issues](https://github.com/mnemo/issues)
- **Email:** support@mnemo.io

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- [x] Core backend API
- [x] Node agent
- [x] Matching algorithm
- [x] Contract management

### Phase 2: MVP (Current)
- [ ] React frontend
- [ ] WebSocket real-time updates
- [ ] Payment integration
- [ ] Analytics dashboard

### Phase 3: Scale
- [ ] Mobile apps
- [ ] Advanced analytics
- [ ] Multi-region support
- [ ] Auto-failover

### Phase 4: Decentralization
- [ ] Blockchain settlement
- [ ] DAO governance
- [ ] Token economics
- [ ] Stake mechanism

## 💡 Use Cases

- **AI Training:** Burst memory for model training
- **Inference:** Low-latency inference serving
- **Gaming Studios:** Render farm memory pools
- **Research Labs:** Temporary compute clusters
- **Edge Computing:** Local data processing

## 🎓 Success Metrics

**For Renters:**
- Average latency: <1ms (vs 10-30ms cloud)
- Cost savings: 40-60% vs AWS/GCP
- Availability: 99.5%+ uptime

**For Providers:**
- Earnings: $50-150/month per node
- Utilization: 60%+ of idle capacity
- Payout time: <24 hours

## 🌟 Key Differentiators

1. **Memory-First:** Unlike GPU marketplaces, we focus on memory arbitrage
2. **Geographic Clustering:** Network effects through proximity
3. **Community-Owned:** Mist nodes create local infrastructure
4. **Smart Matching:** AI-powered node selection
5. **Transparent Pricing:** Real-time market rates

---

**Built with ❤️ by the MNEMO team**

*Making memory markets liquid and accessible to everyone.*
