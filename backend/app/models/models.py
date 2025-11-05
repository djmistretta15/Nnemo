"""
SQLAlchemy models for Mnemo platform
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON, BigInteger, Numeric, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    """User accounts (shared with GP4U)"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='user')  # user, provider, admin

    # Profile
    full_name = Column(String(255))
    organization = Column(String(255))

    # Auth
    api_key = Column(String(128), unique=True, index=True)
    jwt_secret = Column(String(255))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    nodes = relationship("Node", back_populates="owner")
    clients = relationship("Client", back_populates="user")


class Node(Base):
    """Node providers (data centers, edge clusters, mist nodes)"""
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_type = Column(String(50), nullable=False, index=True)  # datacenter, edge_cluster, mist_node
    name = Column(String(255), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    region = Column(String(50), nullable=False, index=True)

    # Location
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

    # Capacity metrics
    total_ram_gb = Column(Integer, nullable=False)
    available_ram_gb = Column(Integer, nullable=False)
    total_vram_gb = Column(Integer, nullable=False)
    available_vram_gb = Column(Integer, nullable=False)

    # Performance
    bandwidth_mbps = Column(Integer, nullable=False)
    base_latency_ms = Column(Numeric(8, 3), nullable=False)

    # Reliability
    uptime_score = Column(Numeric(5, 2), default=99.0)
    reputation_score = Column(Integer, default=100)

    # Pricing
    price_per_gb_sec = Column(Numeric(12, 9), nullable=False)

    # Metadata
    metadata = Column(JSON)  # {idle_schedule, gpu_model, cooling_type, etc}
    status = Column(String(20), default='active', index=True)  # active, maintenance, offline
    last_heartbeat = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="nodes")
    offers = relationship("Offer", back_populates="node", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="node")
    metrics = relationship("NodeMetric", back_populates="node", cascade="all, delete-orphan")


class Offer(Base):
    """Memory offers/listings"""
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey('nodes.id', ondelete='CASCADE'), index=True)

    # Capacity
    ram_gb = Column(Integer, nullable=False)
    vram_gb = Column(Integer, nullable=False)

    # Performance guarantees
    min_bandwidth_mbps = Column(Integer)
    max_latency_ms = Column(Numeric(8, 3))

    # Pricing
    price_per_gb_sec = Column(Numeric(12, 9), nullable=False)
    egress_price_per_gb = Column(Numeric(8, 5))

    # Terms
    min_duration_sec = Column(Integer, default=60)
    max_duration_sec = Column(Integer, default=86400)
    replication_eligible = Column(Boolean, default=True)

    # Status
    status = Column(String(20), default='available', index=True)  # available, reserved, fulfilled
    expires_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    node = relationship("Node", back_populates="offers")


class Client(Base):
    """Clients/renters"""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    org_name = Column(String(255), nullable=False)

    # Location for proximity matching
    default_region = Column(String(50))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

    # Billing
    budget_monthly_usd = Column(Numeric(10, 2))
    current_spend_usd = Column(Numeric(10, 2), default=0)

    # Preferences
    prefer_local = Column(Boolean, default=True)
    max_latency_ms = Column(Numeric(8, 3))
    min_reliability = Column(Numeric(5, 2))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="clients")
    contracts = relationship("Contract", back_populates="client")


class Contract(Base):
    """Memory contracts (rental agreements)"""
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'), index=True)
    node_id = Column(UUID(as_uuid=True), ForeignKey('nodes.id'), index=True)

    # Allocation
    ram_gb = Column(Integer, nullable=False)
    vram_gb = Column(Integer, nullable=False)

    # Timing
    duration_sec = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Pricing
    price_per_gb_sec = Column(Numeric(12, 9), nullable=False)
    total_cost_usd = Column(Numeric(10, 4), nullable=False)

    # Performance
    actual_latency_ms = Column(Numeric(8, 3))
    egress_gb = Column(Numeric(10, 3), default=0)

    # Status
    status = Column(String(20), default='pending', index=True)  # pending, active, completed, failed
    settlement_hash = Column(String(128))  # for payment verification

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    client = relationship("Client", back_populates="contracts")
    node = relationship("Node", back_populates="contracts")
    transactions = relationship("Transaction", back_populates="contract")


class Transaction(Base):
    """Payment transactions"""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), index=True)

    amount_usd = Column(Numeric(10, 4), nullable=False)
    payment_method = Column(String(50))  # stripe, crypto_eth, crypto_sol

    # Stripe
    stripe_payment_id = Column(String(255))

    # Crypto
    blockchain = Column(String(20))
    tx_hash = Column(String(128))
    wallet_address = Column(String(128))

    status = Column(String(20), default='pending', index=True)  # pending, completed, failed, refunded

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settled_at = Column(DateTime(timezone=True))

    # Relationships
    contract = relationship("Contract", back_populates="transactions")


class NodeMetric(Base):
    """Node heartbeat/metrics (time-series data)"""
    __tablename__ = "node_metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    node_id = Column(UUID(as_uuid=True), ForeignKey('nodes.id', ondelete='CASCADE'), index=True)

    # Metrics at time of report
    available_ram_gb = Column(Integer, nullable=False)
    available_vram_gb = Column(Integer, nullable=False)
    cpu_usage_pct = Column(Numeric(5, 2))
    gpu_usage_pct = Column(Numeric(5, 2))
    temperature_c = Column(Integer)
    bandwidth_mbps = Column(Integer)

    # Geolocation (can change for mobile nodes)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    node = relationship("Node", back_populates="metrics")


class Cluster(Base):
    """Geographic clusters (computed view)"""
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region = Column(String(50), nullable=False, unique=True)

    # Aggregated capacity
    total_nodes = Column(Integer, default=0)
    datacenter_nodes = Column(Integer, default=0)
    edge_nodes = Column(Integer, default=0)
    mist_nodes = Column(Integer, default=0)

    total_ram_gb = Column(Integer, default=0)
    available_ram_gb = Column(Integer, default=0)
    total_vram_gb = Column(Integer, default=0)
    available_vram_gb = Column(Integer, default=0)

    # Pricing
    avg_price_per_gb_sec = Column(Numeric(12, 9))

    # Location
    center_latitude = Column(Numeric(9, 6))
    center_longitude = Column(Numeric(9, 6))

    # Timestamp
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
