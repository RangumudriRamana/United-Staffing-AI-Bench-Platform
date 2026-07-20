import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import { WidgetContainer } from "../components/WidgetContainer";
const fetchRecentActivity = async () => {
    await new Promise((resolve) => setTimeout(resolve, 1400)); // Longer lag to test progressive loading isolation
    return [
        { id: 1, action: "New Submission", desc: "John Doe submitted to Senior React Architect", time: "12m ago" },
        { id: 2, action: "Interview Scheduled", desc: "Jane Smith mapped to United Health Technical Loop", time: "1h ago" },
        { id: 3, action: "Placement Complete", desc: "Robert Lee locked to DevOps Lead contract contract", time: "3h ago" },
    ];
};
export const ActivityWidget = () => {
    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ["dashboard", "recentActivity"],
        queryFn: fetchRecentActivity,
    });
    return (_jsx(WidgetContainer, { title: "Recent Activity Stream", isLoading: isLoading, isError: isError, onRetry: refetch, children: _jsx(List, { dense: true, disablePadding: true, sx: { width: "100%" }, children: data?.map((act, index) => (_jsxs(React.Fragment, { children: [_jsx(ListItem, { alignItems: "flex-start", sx: { px: 0, py: 1.5 }, children: _jsx(ListItemText, { primary: _jsx(Typography, { variant: "body2", fontWeight: "bold", children: act.action }), secondary: _jsxs("span", { style: { display: "flex", justifyContent: "space-between", gap: 8, marginTop: 2 }, children: [_jsx(Typography, { variant: "caption", color: "text.secondary", children: act.desc }), _jsx(Typography, { variant: "caption", color: "text.disabled", sx: { minWidth: "fit-content" }, children: act.time })] }) }) }), index < data.length - 1 && _jsx(Divider, {})] }, act.id))) }) }));
};
