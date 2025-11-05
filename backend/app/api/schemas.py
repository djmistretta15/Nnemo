"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    role: str
    api_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================================
# Node Schemas
# ============================================================================

class NodeBase(BaseModel):
    node_type: str = Field(..., pattern="^(datacenter|edge_cluster|mist_node)$")
    name: str = Field(..., min_length=1, max_length=255)
    region: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    bandwidth_mbps: int = Field(..., gt=0)
    base_latency_ms: Decimal = Field(..., gt=0)
    price_per_gb_sec: Decimal = Field(..., gt=0)
    metadata: Optional[Dict[str, Any]] = None


class NodeRegister(NodeBase):
    total_ram_gb: int = Field(..., gt=0)
    total_vram_gb: int = Field(..., ge=0)


class NodeUpdate(BaseModel):
    name: Optional[str] = None
    price_per_gb_sec: Optional[Decimal] = None
    bandwidth_mbps: Optional[int] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NodeHeartbeat(BaseModel):
    available_ram_gb: int = Field(..., ge=0)
    available_vram_gb: int = Field(..., ge=0)
    cpu_usage_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    gpu_usage_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    temperature_c: Optional[int] = None
    bandwidth_mbps: Optional[int] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class NodeResponse(NodeBase):
    id: UUID
    owner_id: Optional[UUID]
    total_ram_gb: int
    available_ram_gb: int
    total_vram_gb: int
    available_vram_gb: int
    uptime_score: Decimal
    reputation_score: int
    status: str
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class NodeDetailResponse(NodeResponse):
    total_earnings: Optional[Decimal] = 0
    active_contracts: int = 0
    total_contracts: int = 0


# ============================================================================
# Marketplace Schemas
# ============================================================================

class MarketplaceFilter(BaseModel):
    node_type: Optional[str] = None
    region: Optional[str] = None
    min_ram_gb: Optional[int] = None
    min_vram_gb: Optional[int] = None
    max_price_per_gb_sec: Optional[Decimal] = None
    min_uptime_score: Optional[Decimal] = None
    client_lat: Optional[Decimal] = None
    client_lng: Optional[Decimal] = None
    max_distance_km: Optional[int] = None
    limit: int = Field(50, le=100)
    offset: int = 0


class OfferResponse(BaseModel):
    node_id: UUID
    node_name: str
    node_type: str
    region: str
    available_ram_gb: int
    available_vram_gb: int
    price_per_gb_sec: Decimal
    uptime_score: Decimal
    distance_km: Optional[Decimal] = None
    estimated_latency_ms: Decimal


class MarketplaceResponse(BaseModel):
    offers: List[OfferResponse]
    total_count: int


class MemoryRequest(BaseModel):
    ram_gb: int = Field(..., gt=0)
    vram_gb: int = Field(..., ge=0)
    duration_sec: int = Field(..., gt=0)
    max_price_per_gb_sec: Decimal = Field(..., gt=0)
    prefer_local: bool = True
    max_distance_km: Optional[int] = Field(None, gt=0)
    min_uptime_score: Optional[Decimal] = Field(None, ge=0, le=100)


class MatchResult(BaseModel):
    node_id: UUID
    node_name: str
    node_type: str
    match_score: Decimal
    estimated_cost: Decimal
    distance_km: Optional[Decimal] = None
    estimated_latency_ms: Decimal
    score_breakdown: Dict[str, Decimal]


class MatchResponse(BaseModel):
    request_id: UUID
    matches: List[MatchResult]


# ============================================================================
# Contract Schemas
# ============================================================================

class ContractCreate(BaseModel):
    node_id: UUID
    ram_gb: int = Field(..., gt=0)
    vram_gb: int = Field(..., ge=0)
    duration_sec: int = Field(..., gt=0)


class ContractSettle(BaseModel):
    actual_egress_gb: Optional[Decimal] = 0


class ContractExtend(BaseModel):
    additional_duration_sec: int = Field(..., gt=0)


class ContractResponse(BaseModel):
    id: UUID
    client_id: UUID
    node_id: UUID
    ram_gb: int
    vram_gb: int
    duration_sec: int
    start_time: datetime
    end_time: datetime
    price_per_gb_sec: Decimal
    total_cost_usd: Decimal
    actual_latency_ms: Optional[Decimal]
    egress_gb: Decimal
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Payment Schemas
# ============================================================================

class PaymentCreate(BaseModel):
    contract_id: UUID
    payment_method: str = Field(..., pattern="^(stripe|crypto_eth|crypto_sol)$")
    stripe_token: Optional[str] = None


class CryptoPayment(BaseModel):
    contract_id: UUID
    blockchain: str = Field(..., pattern="^(ethereum|solana)$")
    tx_hash: str
    wallet_address: str


class TransactionResponse(BaseModel):
    id: UUID
    contract_id: UUID
    amount_usd: Decimal
    payment_method: str
    status: str
    created_at: datetime
    settled_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Cluster Schemas
# ============================================================================

class ClusterResponse(BaseModel):
    region: str
    center: Dict[str, Decimal]
    total_nodes: int
    node_composition: Dict[str, int]
    total_ram_gb: int
    available_ram_gb: int
    total_vram_gb: int
    available_vram_gb: int
    avg_price_per_gb_sec: Optional[Decimal]


class ClustersListResponse(BaseModel):
    clusters: List[ClusterResponse]


# ============================================================================
# Analytics Schemas
# ============================================================================

class EarningsResponse(BaseModel):
    total_earnings: Decimal
    earnings_by_period: List[Dict[str, Any]]


class SpendingResponse(BaseModel):
    total_spending: Decimal
    spending_by_period: List[Dict[str, Any]]
    spending_by_node_type: Dict[str, Decimal]


class MarketSupplyResponse(BaseModel):
    total_nodes: int
    total_ram_gb: int
    available_ram_gb: int
    total_vram_gb: int
    available_vram_gb: int
    utilization_rate: Decimal


class PricingTrendResponse(BaseModel):
    avg_price_per_gb_sec: Decimal
    price_trends: List[Dict[str, Any]]


# ============================================================================
# Error Response
# ============================================================================

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
