"""
Test placement logic and node selection algorithm.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.core.deps import get_db

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_token():
    """Fixture to get an auth token."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "TestOrg",
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]


def test_placement_chooses_best_node(auth_token):
    """Test that placement algorithm chooses the node with best fit score."""
    # Create two nodes with different characteristics
    # Node 1: More VRAM headroom but lower bandwidth
    client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Node1-LowBandwidth",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0,
            "memory_bandwidth_gbps": 1000.0,
            "network_latency_ms_estimate": 5.0
        }
    )
    
    # Node 2: Less VRAM headroom but higher bandwidth and lower latency
    client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Node2-HighBandwidth",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "H100",
            "vram_gb_total": 80.0,
            "memory_bandwidth_gbps": 3000.0,
            "network_latency_ms_estimate": 1.0
        }
    )
    
    # Create model profile
    client.post(
        "/api/v1/model-profiles",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Llama-2-13B",
            "suggested_min_vram_gb": 24.0,
            "suggested_batch_size": 4,
            "category": "llm"
        }
    )
    
    # Make placement request
    response = client.post(
        "/api/v1/placement/requests",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "model_name": "Llama-2-13B",
            "priority": "normal"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Should choose Node2 due to higher bandwidth and lower latency
    # (even though both have same VRAM headroom)
    assert data["decision"]["node"]["name"] == "Node2-HighBandwidth"
    assert data["decision"]["estimated_fit_score"] > 0
    assert "Node2-HighBandwidth" in data["decision"]["reason"]


def test_placement_respects_region_filter(auth_token):
    """Test that placement respects preferred region."""
    # Node in us-east-1
    client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Node-USEast",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0
        }
    )
    
    # Node in us-west-2
    client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Node-USWest",
            "provider_name": "AWS",
            "region": "us-west-2",
            "gpu_model": "A100",
            "vram_gb_total": 80.0
        }
    )
    
    # Request with preferred region us-west-2
    response = client.post(
        "/api/v1/placement/requests",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "model_name": "TestModel",
            "required_vram_gb": 24.0,
            "preferred_region": "us-west-2"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["decision"]["node"]["name"] == "Node-USWest"
    assert data["decision"]["node"]["region"] == "us-west-2"


def test_placement_fails_when_no_suitable_node(auth_token):
    """Test that placement returns 422 when no suitable node exists."""
    # Create node with insufficient VRAM
    client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "SmallNode",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "T4",
            "vram_gb_total": 16.0
        }
    )
    
    # Request more VRAM than available
    response = client.post(
        "/api/v1/placement/requests",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "model_name": "LargeModel",
            "required_vram_gb": 100.0
        }
    )
    
    assert response.status_code == 422
    assert "No suitable node found" in response.json()["detail"]


def test_placement_with_telemetry_update(auth_token):
    """Test placement considers updated VRAM from telemetry."""
    # Create node
    create_response = client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "DynamicNode",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0
        }
    )
    node_id = create_response.json()["id"]
    
    # Update telemetry to show less free VRAM
    client.post(
        f"/api/v1/nodes/{node_id}/telemetry",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "vram_gb_free": 20.0,
            "utilization_percent": 75.0,
            "temperature_c": 70.0
        }
    )
    
    # Try to place a model requiring 30GB (should fail)
    response = client.post(
        "/api/v1/placement/requests",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "model_name": "MediumModel",
            "required_vram_gb": 30.0
        }
    )
    
    assert response.status_code == 422
    assert "No suitable node found" in response.json()["detail"]


def test_public_placement_quote(auth_token):
    """Test public placement quote API."""
    # Create node
    client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "PublicNode",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0
        }
    )
    
    # Get quote without authentication (using API key)
    response = client.post(
        "/api/v1/public/placement/quote",
        headers={"X-API-Key": "test-api-key"},
        json={
            "model_name": "TestModel",
            "required_vram_gb": 24.0
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["chosen_node"]["name"] == "PublicNode"
    assert data["estimated_fit_score"] > 0
    assert "reason" in data
