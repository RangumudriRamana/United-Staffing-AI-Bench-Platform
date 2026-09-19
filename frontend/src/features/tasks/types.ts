export type TaskType =
  | "FOLLOW_UP_VENDOR"
  | "FOLLOW_UP_CLIENT"
  | "FOLLOW_UP_CONSULTANT"
  | "SUBMIT_PROFILE"
  | "REQUEST_FEEDBACK"
  | "INTERVIEW_PREPARATION"
  | "INTERVIEW_FOLLOW_UP"
  | "OFFER_REVIEW"
  | "PLACEMENT_CONFIRMATION"
  | "RESUME_REFRESH"
  | "MARKETING_REFRESH"
  | "GENERAL";

export type TaskStatus =
  | "OPEN"
  | "IN_PROGRESS"
  | "LIMIT_BREACHED"
  | "COMPLETED"
  | "CANCELLED"
  | "EXPIRED";

export type TaskPriority =
  | "LOW"
  | "NORMAL"
  | "HIGH"
  | "URGENT";

export interface Task {
  public_id: string;
  owner_id: number;
  task_type: TaskType;
  priority: TaskPriority;
  status: TaskStatus;
  title: string;
  description: string | null;
  related_entity_type: string | null;
  related_entity_id: number | null;
  due_at: string;
  completed_at: string | null;
  created_at: string;
}