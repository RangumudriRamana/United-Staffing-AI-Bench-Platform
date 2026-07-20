import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Card from "@mui/material/Card";
import CardHeader from "@mui/material/CardHeader";
import CardContent from "@mui/material/CardContent";
import Skeleton from "@mui/material/Skeleton";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
export const WidgetContainer = ({ title, isLoading, isError, onRetry, children, skeletonHeight = 140, }) => {
    return (_jsxs(Card, { elevation: 2, sx: { height: "100%", display: "flex", flexDirection: "column" }, children: [_jsx(CardHeader, { title: _jsx(Typography, { variant: "subtitle1", fontWeight: "bold", children: title }), sx: { pb: 1 } }), _jsxs(CardContent, { sx: { flexGrow: 1, pt: 0 }, children: [isLoading && (_jsxs(Box, { sx: { display: "flex", flexDirection: "column", gap: 1 }, children: [_jsx(Skeleton, { variant: "text", width: "60%", height: 24 }), _jsx(Skeleton, { variant: "rectangular", height: skeletonHeight, sx: { borderRadius: 1 } })] })), isError && !isLoading && (_jsxs(Box, { sx: { py: 3, textAlign: "center" }, children: [_jsx(Typography, { variant: "body2", color: "error", sx: { mb: 2 }, children: "Failed to refresh metric workspace data stream." }), onRetry && (_jsx(Button, { size: "small", variant: "outlined", color: "primary", onClick: onRetry, children: "Retry Sync" }))] })), !isLoading && !isError && children] })] }));
};
