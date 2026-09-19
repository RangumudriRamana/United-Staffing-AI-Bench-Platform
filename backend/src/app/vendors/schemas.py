from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field,computed_field

from app.vendors.enums import (VendorStatus,VendorTier,VendorType,ClientStatus,)


# ==========================================================
# Vendor Contact Schemas
# ==========================================================

class VendorContactBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    title: str | None = Field(default=None, max_length=100)
    email: str = Field(..., max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    linkedin: str | None = Field(default=None, max_length=255)
    timezone: str = Field(default="EST", max_length=50)
    preferred_contact: bool = False
    is_active: bool = True


class VendorContactCreateRequest(VendorContactBase):
    pass


class VendorContactUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    title: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    linkedin: str | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=50)
    preferred_contact: bool | None = None
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


class VendorContactResponse(VendorContactBase):
    public_id: UUID
    last_contacted: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Vendor Schemas
# ==========================================================

class VendorBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    vendor_type: VendorType = VendorType.PRIME_VENDOR
    tier: VendorTier = VendorTier.TIER_2
    status: VendorStatus = VendorStatus.ACTIVE
    website: str | None = Field(default=None, max_length=255)
    preferred: bool = False
    notes: str | None = Field(default=None, max_length=1000)


class VendorCreateRequest(VendorBase):
    contacts: list[VendorContactCreateRequest] = Field(default_factory=list)


class VendorUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    vendor_type: VendorType | None = None
    tier: VendorTier | None = None
    status: VendorStatus | None = None
    website: str | None = Field(default=None, max_length=255)
    preferred: bool | None = None
    notes: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class VendorResponse(VendorBase):
    public_id: UUID
    created_at: datetime
    updated_at: datetime

    contacts: list[VendorContactResponse] = Field(default_factory=list)
    clients: list[ClientResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Vendor Search / Filter DTO
# ==========================================================

class VendorFilters(BaseModel):
    vendor_type: VendorType | None = None
    tier: VendorTier | None = None
    status: VendorStatus | None = None
    preferred_only: bool = False
    search_text: str | None = None


# ==========================================================
# Client Schemas
# (Client currently lives inside Vendor aggregate)
# ==========================================================

class ClientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    display_name: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    primary_location: str | None = Field(default=None, max_length=150)
    timezone: str = "EST"
    notes: str | None = Field(default=None, max_length=1000)
    status: ClientStatus = ClientStatus.ACTIVE
    preferred: bool = False


class ClientCreateRequest(ClientBase):
    vendor_public_id: UUID


class ClientUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150,)
    display_name: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    primary_location: str | None = Field(default=None, max_length=150)
    timezone: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=1000)
    status: ClientStatus | None = None
    preferred: bool | None = None

    model_config = ConfigDict(extra="forbid")


class ClientResponse(ClientBase):
    public_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==========================================================
# Client Search Filters
# ==========================================================

class ClientFilters(BaseModel):
    vendor_public_id: UUID | None = None
    status: ClientStatus | None = None
    industry: str | None = None
    preferred_only: bool = False
    search_text: str | None = None
