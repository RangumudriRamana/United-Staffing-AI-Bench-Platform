export type SubmissionStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "INTERVIEW_SCHEDULED"
  | "INTERVIEW_COMPLETED"
  | "OFFER_RECEIVED"
  | "OFFER_ACCEPTED"
  | "PLACED"
  | "REJECTED"
  | "WITHDRAWN"
  | "CLOSED";

export type EmploymentType =
  | "C2C"
  | "W2"
  | "1099"
  | "FULL_TIME";

export type InterviewType =
  | "TECHNICAL"
  | "CULTURAL"
  | "CLIENT"
  | "MANAGEMENT";

export type InterviewStatus =
  | "SCHEDULED"
  | "COMPLETED"
  | "CANCELLED";

export type OfferStatus =
  | "PENDING"
  | "ACCEPTED"
  | "DECLINED"
  | "EXPIRED";

export type PlacementStatus =
  | "ACTIVE"
  | "COMPLETED"
  | "TERMINATED";


export interface Submission {
  public_id: string;

  consultant_id: number;
  submitted_by: number;

  vendor_id: number;
  vendor_contact_id: number | null;

  client_id: number;
  requirement_id: number | null;

  client_name_snapshot: string;
  vendor_name_snapshot: string;
  job_title_snapshot: string;

  job_id: string | null;

  job_title: string;
  job_location: string | null;

  employment_type: EmploymentType;

  rate: number;
  currency: string;

  submission_status: SubmissionStatus;

  submitted_at: string;
  expected_start_date: string | null;

  submission_notes: string | null;

  created_at: string;
  updated_at: string;
}


export interface SubmissionHistory {
  id: number;

  submission_id: number;
  changed_by: number;

  status: SubmissionStatus;

  effective_from: string;
  effective_until: string | null;

  reason: string | null;
  notes: string | null;

  created_at: string;
  updated_at: string;
}


export interface Interview {
  public_id: string;

  round_number: number;
  interview_type: InterviewType;
  status: InterviewStatus;

  scheduled_at: string;
  timezone: string;

  interviewer: string | null;
  feedback: string | null;

  created_at: string;
}


export interface ClientFeedback {
  id: number;

  submission_id: number;

  author: string;
  rating: number;
  feedback: string;
  received_at: string;

  created_at: string;
  updated_at: string;
}


export interface Offer {
  public_id: string;

  offered_rate: number;
  currency: string;

  start_date: string;
  expiration_date: string | null;

  offer_status: OfferStatus;

  notes: string | null;

  created_at: string;
}


export interface Placement {
  public_id: string;

  started_on: string;
  ended_on: string | null;

  billing_rate: number;
  pay_rate: number;

  placement_status: PlacementStatus;

  created_at: string;
}


export interface ConsultantSummary {
  public_id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface VendorSummary {
  public_id: string;
  name: string;
}

export interface VendorContactSummary {
  public_id: string;
  name: string;
  title: string | null;
  email: string;
  phone: string | null;
}

export interface ClientSummary {
  public_id: string;
  name: string;
  display_name: string | null;
}

export interface SubmissionDetail extends Submission {
  consultant: ConsultantSummary | null;
  vendor: VendorSummary | null;
  vendor_contact: VendorContactSummary | null;
  client: ClientSummary | null;

  history: SubmissionHistory[];
  interviews: Interview[];
  feedback: ClientFeedback[];
  offers: Offer[];
  placements: Placement[];
}


export interface SubmissionListResponse {
  items: Submission[];

  total: number;
  page: number;
  page_size: number;
}


export interface SubmissionSearchFilters {
  consultant_id?: number;
  vendor_id?: number;
  client_id?: number;
  requirement_id?: number;

  submission_status?: SubmissionStatus;
  employment_type?: EmploymentType;

  job_title?: string;

  page?: number;
  page_size?: number;
}

export interface CreateSubmissionRequest {
  consultant_public_id: string;
  vendor_public_id: string;
  vendor_contact_public_id?: string | null;
  client_public_id: string;
  requirement_public_id?: string | null;

  client_name_snapshot: string;
  vendor_name_snapshot: string;
  job_title_snapshot: string;
  job_id?: string | null;
  job_title: string;
  job_location?: string | null;
  employment_type?: EmploymentType;
  rate: number;
  currency?: string;
  expected_start_date?: string | null;
  submission_notes?: string | null;
}


export interface SubmissionTransitionRequest {
  target_status: SubmissionStatus;
  reason?: string | null;
  notes?: string | null;
}


export interface InterviewCreateRequest {
  round_number?: number;

  interview_type: InterviewType;

  scheduled_at: string;

  timezone?: string;

  interviewer?: string | null;
}


export interface OfferCreateRequest {
  offered_rate: number;
  currency?: string;

  start_date: string;
  expiration_date?: string | null;

  notes?: string | null;
}


export interface PlacementCreateRequest {
  started_on: string;
  ended_on?: string | null;

  billing_rate: number;
  pay_rate: number;
}