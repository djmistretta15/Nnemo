#!/usr/bin/env python3
"""
Initialize MNEMO database
Creates all tables and optionally seeds test data
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base, SessionLocal
from app.models import User, Node, Client, Cluster
from app.auth import hash_password
import secrets


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


def seed_test_data():
    """Seed database with test data"""
    print("\nSeeding test data...")

    db = SessionLocal()

    try:
        # Create admin user
        admin = User(
            email="admin@mnemo.io",
            password_hash=hash_password("admin123"),
            full_name="Admin User",
            role="admin",
            api_key=secrets.token_urlsafe(32)
        )
        db.add(admin)

        # Create test provider user
        provider = User(
            email="provider@example.com",
            password_hash=hash_password("provider123"),
            full_name="Test Provider",
            organization="Test Datacenter",
            role="provider",
            api_key=secrets.token_urlsafe(32)
        )
        db.add(provider)

        # Create test client user
        client_user = User(
            email="client@example.com",
            password_hash=hash_password("client123"),
            full_name="Test Client",
            organization="AI Startup Inc",
            role="user",
            api_key=secrets.token_urlsafe(32)
        )
        db.add(client_user)

        db.commit()
        db.refresh(provider)
        db.refresh(client_user)

        # Create test nodes
        test_nodes = [
            Node(
                node_type="datacenter",
                name="DataCenter_Node_1",
                owner_id=provider.id,
                region="us-east-1",
                latitude=40.7128,
                longitude=-74.0060,
                total_ram_gb=256,
                available_ram_gb=256,
                total_vram_gb=80,
                available_vram_gb=80,
                bandwidth_mbps=10000,
                base_latency_ms=0.5,
                price_per_gb_sec=0.0000005,
                metadata={"gpu_model": "A100", "cooling": "liquid"}
            ),
            Node(
                node_type="edge_cluster",
                name="Edge_SF_Cluster",
                owner_id=provider.id,
                region="us-west-1",
                latitude=37.7749,
                longitude=-122.4194,
                total_ram_gb=128,
                available_ram_gb=128,
                total_vram_gb=48,
                available_vram_gb=48,
                bandwidth_mbps=5000,
                base_latency_ms=1.2,
                price_per_gb_sec=0.0000007,
                metadata={"gpu_model": "RTX 4090", "cooling": "air"}
            ),
            Node(
                node_type="mist_node",
                name="Alice_Gaming_PC",
                owner_id=provider.id,
                region="us-east-2",
                latitude=40.7282,
                longitude=-73.7949,
                total_ram_gb=64,
                available_ram_gb=64,
                total_vram_gb=24,
                available_vram_gb=24,
                bandwidth_mbps=980,
                base_latency_ms=0.8,
                price_per_gb_sec=0.0000008,
                metadata={"gpu_model": "RTX 4090", "idle_schedule": "9am-5pm"}
            )
        ]

        for node in test_nodes:
            db.add(node)

        # Create test client profile
        test_client = Client(
            user_id=client_user.id,
            org_name="AI Startup Inc",
            default_region="us-east-1",
            latitude=40.7128,
            longitude=-74.0060,
            budget_monthly_usd=5000,
            prefer_local=True,
            max_latency_ms=5.0,
            min_reliability=95.0
        )
        db.add(test_client)

        # Create test clusters
        clusters = [
            Cluster(
                region="us-east-1",
                total_nodes=1,
                datacenter_nodes=1,
                edge_nodes=0,
                mist_nodes=0,
                total_ram_gb=256,
                available_ram_gb=256,
                total_vram_gb=80,
                available_vram_gb=80,
                avg_price_per_gb_sec=0.0000005,
                center_latitude=40.7128,
                center_longitude=-74.0060
            ),
            Cluster(
                region="us-west-1",
                total_nodes=1,
                datacenter_nodes=0,
                edge_nodes=1,
                mist_nodes=0,
                total_ram_gb=128,
                available_ram_gb=128,
                total_vram_gb=48,
                available_vram_gb=48,
                avg_price_per_gb_sec=0.0000007,
                center_latitude=37.7749,
                center_longitude=-122.4194
            ),
            Cluster(
                region="us-east-2",
                total_nodes=1,
                datacenter_nodes=0,
                edge_nodes=0,
                mist_nodes=1,
                total_ram_gb=64,
                available_ram_gb=64,
                total_vram_gb=24,
                available_vram_gb=24,
                avg_price_per_gb_sec=0.0000008,
                center_latitude=40.7282,
                center_longitude=-73.7949
            )
        ]

        for cluster in clusters:
            db.add(cluster)

        db.commit()

        print("✅ Test data seeded successfully")
        print("\n📝 Test Accounts:")
        print(f"   Admin:    admin@mnemo.io / admin123 (API Key: {admin.api_key})")
        print(f"   Provider: provider@example.com / provider123 (API Key: {provider.api_key})")
        print(f"   Client:   client@example.com / client123 (API Key: {client_user.api_key})")
        print(f"\n📊 Created 3 test nodes and 1 test client")

    except Exception as e:
        print(f"❌ Error seeding data: {str(e)}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function"""
    print("="*60)
    print("MNEMO Database Initialization")
    print("="*60)

    # Create tables
    create_tables()

    # Ask if user wants to seed test data
    response = input("\nSeed test data? (y/n): ").lower().strip()
    if response == 'y':
        seed_test_data()

    print("\n✅ Database initialization complete!")


if __name__ == "__main__":
    main()
