export interface PlannerSummary {
  planner_date: string;
  open_tasks: number;
  urgent_tasks: number;
  high_priority_tasks: number;
  marketing_follow_ups: number;
  submission_follow_ups: number;
  vendor_outreach: number;
}

export interface PlannerTaskItem {
  public_id: string;
  title: string;
  task_type: string;
  priority: string;
  status: string;
  due_at: string;
}

export interface PlannerResponse {
  summary: PlannerSummary;
  tasks: PlannerTaskItem[];
}