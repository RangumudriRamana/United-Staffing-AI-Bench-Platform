import { UserRole } from "@/store/authStore";

export interface WidgetMeta {
  id: string;
  title: string;
  component: React.ComponentType;
  allowedRoles: UserRole[];
  grid: {
    xs: number;
    sm?: number;
    md?: number;
  };
}