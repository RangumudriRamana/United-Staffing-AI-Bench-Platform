import React from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { useAuthStore } from "@/store/authStore";

// Widgets
import { SummaryCards } from "../widgets/SummaryCards";
import { ActivityWidget } from "../widgets/ActivityWidget";
import { WidgetMeta } from "../types/widget.types";

// A basic placeholder widget for remaining checklist modules
const PlaceholderWidget = (title: string) => () => (
  <Box sx={{ p: 4, border: "1px dashed variant", borderRadius: 2, textAlign: "center", bgcolor: "action.hover" }}>
    <Typography variant="body2" color="text.secondary">{title} Context Data Pipeline Frame</Typography>
  </Box>
);

// Metadata Blueprint Configuration Engine
const WIDGET_REGISTRY: WidgetMeta[] = [
  { id: "activity", title: "Activity Watch", component: ActivityWidget, allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], grid: { xs: 12, md: 6 } },
  { id: "bench", title: "Bench Availability Index", component: PlaceholderWidget("Bench Availability"), allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], grid: { xs: 12, md: 6 } },
  { id: "tasks", title: "Workload Tasks Due Today", component: PlaceholderWidget("Recruiter System Tasks"), allowedRoles: ["ADMIN", "RECRUITER"], grid: { xs: 12 } },
  { id: "ops", title: "System Administration Analytics", component: PlaceholderWidget("Admin Health Telemetry"), allowedRoles: ["ADMIN"], grid: { xs: 12 } },
];

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const currentRole = user?.role || "RECRUITER";

  // Filter components declaratively on screen load base mapping RBAC authorization arrays
  const visibleWidgets = WIDGET_REGISTRY.filter((widget) =>
    widget.allowedRoles.includes(currentRole)
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Block Row */}
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Welcome Back, {user?.firstName || "Operator"}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Here is your current operational workspace status overview ({currentRole} Console)
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Full span row always rendered for high level numbers overview summary layout updates */}
        <Grid item xs={12}>
          <SummaryCards />
        </Grid>

        {/* Dynamically looped grid matrices processing child blocks safely based on metadata layouts */}
        {visibleWidgets.map((widget) => {
          const WidgetComponent = widget.component;
          return (
            <Grid item xs={widget.grid.xs} md={widget.grid.md} key={widget.id}>
              <WidgetComponent />
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};