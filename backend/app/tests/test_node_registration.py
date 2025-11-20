"""
Test node registration and telemetry updates.
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


def test_create_node(auth_token):
    """Test node registration."""
    response = client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "TestNode-GPU1",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0,
            "memory_bandwidth_gbps": 1935.0,
            "network_latency_ms_estimate": 2.5
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TestNode-GPU1"
    assert data["gpu_model"] == "A100"
    assert data["vram_gb_total"] == 80.0
    assert data["vram_gb_free_estimate"] == 80.0  # Initially all free
    assert data["is_active"] is True


def test_list_nodes(auth_token):
    """Test listing nodes."""
    # Create a node first
    client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "TestNode-GPU1",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0
        }
    )
    
    # List nodes
    response = client.get(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "TestNode-GPU1"


def test_push_telemetry_updates_vram(auth_token):
    """Test that pushing telemetry updates node VRAM estimate."""
    # Create node
    create_response = client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "TestNode-GPU1",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0
        }
    )
    node_id = create_response.json()["id"]
    
    # Push telemetry
    telemetry_response = client.post(
        f"/api/v1/nodes/{node_id}/telemetry",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "vram_gb_free": 60.0,
            "utilization_percent": 25.0,
            "temperature_c": 65.0
        }
    )
    assert telemetry_response.status_code == 201
    
    # Verify node VRAM was updated
    node_response = client.get(
        f"/api/v1/nodes/{node_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert node_response.status_code == 200
    assert node_response.json()["vram_gb_free_estimate"] == 60.0


def test_get_node_telemetry(auth_token):
    """Test retrieving node telemetry history."""
    # Create node
    create_response = client.post(
        "/api/v1/nodes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "TestNode-GPU1",
            "provider_name": "AWS",
            "region": "us-east-1",
            "gpu_model": "A100",
            "vram_gb_total": 80.0
        }
    )
    node_id = create_response.json()["id"]
    
    # Push multiple telemetry records
    for vram in [70.0, 60.0, 50.0]:
        client.post(
            f"/api/v1/nodes/{node_id}/telemetry",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "vram_gb_free": vram,
                "utilization_percent": 25.0,
                "temperature_c": 65.0
            }
        )
    
    # Get telemetry
    response = client.get(
        f"/api/v1/nodes/{node_id}/telemetry",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Should be newest first
    assert data[0]["vram_gb_free"] == 50.0
    assert data[1]["vram_gb_free"] == 60.0
    assert data[2]["vram_gb_free"] == 70.0
