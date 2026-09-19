export type NotificationType =
  | "FOLLOW_UP_DUE"
  | "INTERVIEW_SCHEDULED"
  | "INTERVIEW_REMINDER"
  | "INTERVIEW_FEEDBACK_PENDING"
  | "OFFER_RECEIVED"
  | "OFFER_EXPIRING"
  | "PLACEMENT_CONFIRMED"
  | "CONSULTANT_AVAILABLE"
  | "REQUIREMENT_OPENED"
  | "REQUIREMENT_STALE"
  | "SYSTEM_ALERT";

export type NotificationPriority =
  | "LOW"
  | "NORMAL"
  | "HIGH"
  | "CRITICAL";

export type NotificationStatus =
  | "UNREAD"
  | "READ"
  | "DISMISSED";

export type DeliveryChannel =
  | "IN_APP"
  | "EMAIL"
  | "SMS"
  | "SLACK"
  | "TEAMS"
  | "WEBHOOK";

export interface Notification {
  public_id: string;
  recipient_id: number;
  notification_type: NotificationType;
  priority: NotificationPriority;
  status: NotificationStatus;
  delivery_channel: DeliveryChannel;
  title: string;
  body: string;
  created_at: string;
  read_at: string | null;
}