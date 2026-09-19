export interface ExecutiveSummaryDTO {
  total_consultants: number;
  available_consultants: number;
  active_requirements: number;
  active_submissions: number;
  placements_this_month: number;
}

export interface BenchHealthDTO {
  available: number;
  marketing_active: number;
  placed: number;
  idle_greater_30_days: number;
}

export interface RecruiterPerformanceSummaryDTO {
  recruiter_name: string;
  submissions_count: number;
  placements_count: number;
  conversion_rate: number;
}

export interface ForecastIndicatorsDTO {
  expected_placements_this_month: number;
  pipeline_growth_velocity: string;
}

export interface ExecutiveDashboardResponse {
  summary: ExecutiveSummaryDTO;
  bench_health: BenchHealthDTO;
  recruiter_performance: RecruiterPerformanceSummaryDTO[];
  forecast: ForecastIndicatorsDTO;
}

export interface RecruiterKPIMetrics {
  recruiter_id: number;
  active_consultants: number;
  total_submissions: number;
  interviews_scheduled: number;
  placements_secured: number;
  placement_conversion_rate: number;
}

export interface FollowUpItem {
  task_type: string;
  description: string;
  severity: string;
  target_public_id: string | null;
}

export interface DashboardTimelineEvent {
  event_type: string;
  summary: string;
  occurred_at: string;
  actor_id: number | null;
}

export interface RecruiterDashboardResponse {
  summary: RecruiterKPIMetrics;
  followups: FollowUpItem[];
  timeline: DashboardTimelineEvent[];
}

export interface AccountFunnelStage {
  stage_name: string;
  count: number;
  conversion_rate: number;
}

export interface RelationshipHealthDTO {
  health_score: number;
  status_label: string;
  contributing_factors: string[];
}

export interface AccountResponseTimeMetrics {
  avg_days_req_to_submission: number;
  avg_days_submission_to_interview: number;
  avg_days_interview_to_feedback: number;
}

export interface VendorAnalyticsSummaryResponse {
  vendor_public_id: string;
  vendor_name: string;
  funnel: AccountFunnelStage[];
  health: RelationshipHealthDTO;
  velocity: AccountResponseTimeMetrics;
}