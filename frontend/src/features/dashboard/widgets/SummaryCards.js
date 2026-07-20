import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useQuery } from "@tanstack/react-query";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import PeopleIcon from "@mui/icons-material/People";
import AssignmentIcon from "@mui/icons-material/Assignment";
import SendIcon from "@mui/icons-material/Send";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import Skeleton from "@mui/material/Skeleton";
// Independent Fetch Hook
const fetchSummaryStats = async () => {
    // TODO: Point directly to backend metrics endpoint when available
    await new Promise((resolve) => setTimeout(resolve, 800)); // Progressive loading simulation
    return { activeConsultants: 42, openRequirements: 18, activeSubmissions: 156, interviewsToday: 5 };
};
export const SummaryCards = () => {
    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ["dashboard", "summaryStats"],
        queryFn: fetchSummaryStats,
    });
    const metrics = [
        { label: "Active Consultants", val: data?.activeConsultants, icon: _jsx(PeopleIcon, { color: "primary" }) },
        { label: "Open Requirements", val: data?.openRequirements, icon: _jsx(AssignmentIcon, { color: "success" }) },
        { label: "Active Submissions", val: data?.activeSubmissions, icon: _jsx(SendIcon, { color: "warning" }) },
        { label: "Interviews Today", val: data?.interviewsToday, icon: _jsx(CalendarMonthIcon, { color: "error" }) },
    ];
    if (isLoading) {
        return (_jsx(Grid, { container: true, spacing: 2, children: [1, 2, 3, 4].map((i) => (_jsx(Grid, { item: true, xs: 12, sm: 6, md: 3, children: _jsx(Skeleton, { variant: "rectangular", height: 90, sx: { borderRadius: 2 } }) }, i))) }));
    }
    if (isError) {
        return (_jsxs(Paper, { sx: { p: 3, textAlign: "center", color: "error.main" }, children: ["Error mounting dashboard overview telemetry. ", _jsx("span", { style: { cursor: "pointer", textDecoration: "underline" }, onClick: () => refetch(), children: "Retry" })] }));
    }
    return (_jsx(Grid, { container: true, spacing: 2, children: metrics.map((m, idx) => (_jsx(Grid, { item: true, xs: 12, sm: 6, md: 3, children: _jsxs(Paper, { elevation: 2, sx: { p: 2, display: "flex", alignItems: "center", justifyContent: "space-between", borderRadius: 2 }, children: [_jsxs(Box, { children: [_jsx(Typography, { variant: "body2", color: "text.secondary", fontWeight: "medium", children: m.label }), _jsx(Typography, { variant: "h4", sx: { fontWeight: "bold", mt: 0.5 }, children: m.val })] }), _jsx(Box, { sx: { p: 1.5, bgcolor: "action.hover", borderRadius: "50%", display: "flex" }, children: m.icon })] }) }, idx))) }));
};
