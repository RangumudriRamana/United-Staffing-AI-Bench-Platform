export type VisaStatus =
  | "H1B"
  | "H4 EAD"
  | "GC"
  | "USC"
  | "OPT"
  | "STEM OPT"
  | "CPT"
  | "L2 EAD"
  | "TN"
  | "E3"
  | "Other";

export type MarketingStatus =
  | "NEW"
  | "READY_FOR_MARKETING"
  | "MARKETING_ACTIVE"
  | "INTERVIEWING"
  | "OFFER_PENDING"
  | "PLACED"
  | "ON_PROJECT"
  | "UNAVAILABLE"
  | "INACTIVE";

export type RateType =
  | "Hourly"
  | "Daily"
  | "Monthly"
  | "Annual";

export type AvailabilityStatus =
  | "AVAILABLE_NOW"
  | "AVAILABLE_ON_DATE"
  | "NOT_AVAILABLE";

export interface Consultant {
  public_id: string;

  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;

  current_title: string | null;
  total_experience_years: number;

  current_location: string | null;
  preferred_location: string | null;
  relocation_available: boolean;
  remote_preference: string;

  visa_status: VisaStatus;
  visa_expiration: string | null;
  work_authorized: boolean;

  marketing_status: MarketingStatus;

  availability_status: AvailabilityStatus;
  availability_date: string | null;

  rate_type: RateType;
  expected_rate: number | string | null;

  recruiter_id?: number;
  created_by?: number | null;
  updated_by?: number | null;

  created_at: string;
  updated_at: string;
}

export interface CreateConsultantRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;

  current_title?: string | null;
  total_experience_years?: number;

  current_location?: string | null;
  preferred_location?: string | null;
  relocation_available?: boolean;
  remote_preference?: string;

  visa_status: VisaStatus;
  visa_expiration?: string | null;
  work_authorized?: boolean;

  availability_date?: string | null;

  rate_type?: RateType;
  expected_rate?: number | null;
}

export interface UpdateConsultantRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string | null;

  current_title?: string | null;
  total_experience_years?: number;

  current_location?: string | null;
  preferred_location?: string | null;
  relocation_available?: boolean;
  remote_preference?: string;

  visa_status?: VisaStatus;
  visa_expiration?: string | null;
  work_authorized?: boolean;

  availability_date?: string | null;

  rate_type?: RateType;
  expected_rate?: number | null;
}

export interface ConsultantsResponse {
  data: Consultant[];

  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}