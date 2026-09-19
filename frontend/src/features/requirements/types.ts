export type RequirementStatus =
  | "DRAFT"
  | "OPEN"
  | "SOURCING"
  | "SUBMITTING"
  | "INTERVIEWING"
  | "ON_HOLD"
  | "FILLED"
  | "CANCELLED"
  | "CLOSED";

export type WorkModel =
  | "REMOTE"
  | "HYBRID"
  | "ONSITE";

export type RequirementPriority =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "URGENT";

export type EmploymentType =
  | "C2C"
  | "W2"
  | "1099"
  | "FULL_TIME";

export type DocumentType =
  | "Resume"
  | "Work Authorization"
  | "Passport"
  | "Driver License"
  | "Visa"
  | "I-94"
  | "SSN"
  | "Vendor RTR"
  | "Rate Confirmation"
  | "Miscellaneous";

export interface RequirementTechnology {
  technology_id: number;
  minimum_years: number;
  mandatory: boolean;
  notes: string | null;
}

export interface Requirement {
  public_id: string;
  vendor_id: number;
  client_id: number;
  owner_recruiter_id: number;

  job_title: string;
  job_code: string | null;

  employment_type: EmploymentType;
  work_model: WorkModel;

  location: string | null;

  rate_min: number | null;
  rate_max: number | null;
  currency: string;

  priority: RequirementPriority;
  status: RequirementStatus;

  positions: number;

  received_date: string;
  target_start_date: string | null;

  description: string | null;
  notes: string | null;

  technologies: RequirementTechnology[];
  history: unknown[];
}

export interface CreateRequirementRequest {
  vendor_id: number;
  client_id: number;
  job_title: string;
  job_code?: string | null;

  employment_type?: EmploymentType;
  work_model?: WorkModel;

  location?: string | null;
  description?: string | null;
  notes?: string | null;

  rate_min?: number | null;
  rate_max?: number | null;
  currency?: string;

  priority?: RequirementPriority;

  experience_min?: number;
  experience_max?: number | null;

  positions?: number;

  target_start_date?: string | null;
}

export interface RequirementTransitionRequest {
  target_status: RequirementStatus;
  reason?: string | null;
  notes?: string | null;
}

export interface RequirementTechnologyRequest {
  technology_id: number;
  minimum_years?: number;
  mandatory?: boolean;
  notes?: string | null;
}

export interface RequirementDocumentRequest {
  document_type: DocumentType;
  mandatory?: boolean;
  notes?: string | null;
}

export interface OwnerReassignmentRequest {
  new_owner_id: number;
}

export interface RequirementSearchCriteria {
  search?: string;
  status?: RequirementStatus;
  employment_type?: EmploymentType;
  work_model?: WorkModel;
  priority?: RequirementPriority;
  owner_recruiter_id?: number;
  vendor_id?: number;
  client_id?: number;
}