import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { useAuthStore } from "@/store/authStore";
// Widgets
import { SummaryCards } from "../widgets/SummaryCards";
import { ActivityWidget } from "../widgets/ActivityWidget";
// A basic placeholder widget for remaining checklist modules
const PlaceholderWidget = (title) => () => (_jsx(Box, { sx: { p: 4, border: "1px dashed variant", borderRadius: 2, textAlign: "center", bgcolor: "action.hover" }, children: _jsxs(Typography, { variant: "body2", color: "text.secondary", children: [title, " Context Data Pipeline Frame"] }) }));
// Metadata Blueprint Configuration Engine
const WIDGET_REGISTRY = [
    { id: "activity", title: "Activity Watch", component: ActivityWidget, allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], grid: { xs: 12, md: 6 } },
    { id: "bench", title: "Bench Availability Index", component: PlaceholderWidget("Bench Availability"), allowedRoles: ["ADMIN", "MANAGER", "RECRUITER"], grid: { xs: 12, md: 6 } },
    { id: "tasks", title: "Workload Tasks Due Today", component: PlaceholderWidget("Recruiter System Tasks"), allowedRoles: ["ADMIN", "RECRUITER"], grid: { xs: 12 } },
    { id: "ops", title: "System Administration Analytics", component: PlaceholderWidget("Admin Health Telemetry"), allowedRoles: ["ADMIN"], grid: { xs: 12 } },
];
export const DashboardPage = () => {
    const { user } = useAuthStore();
    const currentRole = user?.role || "RECRUITER";
    // Filter components declaratively on screen load base mapping RBAC authorization arrays
    const visibleWidgets = WIDGET_REGISTRY.filter((widget) => widget.allowedRoles.includes(currentRole));
    return (_jsxs(Box, { sx: { p: 3 }, children: [_jsx(Box, { sx: { display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }, children: _jsxs(Box, { children: [_jsxs(Typography, { variant: "h4", component: "h1", fontWeight: "bold", children: ["Welcome Back, ", user?.firstName || "Operator"] }), _jsxs(Typography, { variant: "body2", color: "text.secondary", children: ["Here is your current operational workspace status overview (", currentRole, " Console)"] })] }) }), _jsxs(Grid, { container: true, spacing: 3, children: [_jsx(Grid, { item: true, xs: 12, children: _jsx(SummaryCards, {}) }), visibleWidgets.map((widget) => {
                        const WidgetComponent = widget.component;
                        return (_jsx(Grid, { item: true, xs: widget.grid.xs, md: widget.grid.md, children: _jsx(WidgetComponent, {}) }, widget.id));
                    })] })] }));
};
