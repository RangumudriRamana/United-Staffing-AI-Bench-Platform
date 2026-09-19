export type VendorStatus =
  | "ACTIVE"
  | "INACTIVE";

export type VendorTier =
  | "TIER_1"
  | "TIER_2"
  | "TIER_3";

export type VendorType =
  | "PRIME_VENDOR"
  | "IMPLEMENTATION_PARTNER"
  | "DIRECT_CLIENT"
  | "STAFFING_FIRM";

export type ClientStatus =
  | "ACTIVE"
  | "INACTIVE";

export interface VendorContact {
  public_id: string;
  name: string;
  title: string | null;
  email: string;
  phone: string | null;
  linkedin: string | null;
  timezone: string;
  preferred_contact: boolean;
  is_active: boolean;
  last_contacted: string | null;
  created_at: string;
  updated_at: string;
}

export interface Client {
  public_id: string;
  name: string;
  display_name: string | null;
  industry: string | null;
  website: string | null;
  primary_location: string | null;
  timezone: string;
  notes: string | null;
  status: ClientStatus;
  preferred: boolean;
  created_at: string;
  updated_at: string;
}

export interface Vendor {
  public_id: string;
  name: string;
  vendor_type: VendorType;
  tier: VendorTier;
  status: VendorStatus;
  website: string | null;
  preferred: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
  contacts: VendorContact[];
  clients: Client[];
}

export interface VendorPagination {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface VendorsResponse {
  data: Vendor[];
  pagination: VendorPagination;
}