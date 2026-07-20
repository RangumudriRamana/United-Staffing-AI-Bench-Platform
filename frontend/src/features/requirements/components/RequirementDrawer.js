import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Drawer from "@mui/material/Drawer";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import Divider from "@mui/material/Divider";
import Button from "@mui/material/Button";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import Chip from "@mui/material/Chip";
export const RequirementDrawer = ({ open, onClose, requirement, onEdit, onDelete, isDeleting }) => {
    return (_jsx(Drawer, { anchor: "right", open: open, onClose: onClose, children: _jsxs(Box, { sx: { width: 420, p: 3, display: "flex", flexDirection: "column", height: "100%" }, children: [_jsxs(Box, { sx: { display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }, children: [_jsx(Typography, { variant: "h6", children: "Requirement Details" }), _jsx(IconButton, { onClick: onClose, children: _jsx(CloseIcon, {}) })] }), _jsx(Divider, { sx: { mb: 3 } }), requirement ? (_jsxs(Box, { sx: { flexGrow: 1 }, children: [_jsx(Typography, { variant: "subtitle2", color: "text.secondary", children: "Job Title" }), _jsx(Typography, { variant: "body1", sx: { mb: 2, fontWeight: 500 }, children: requirement.title }), _jsx(Typography, { variant: "subtitle2", color: "text.secondary", children: "Client" }), _jsx(Typography, { variant: "body1", sx: { mb: 2, fontWeight: 500 }, children: requirement.client }), _jsx(Typography, { variant: "subtitle2", color: "text.secondary", children: "Technology" }), _jsx(Typography, { variant: "body1", sx: { mb: 2, fontWeight: 500 }, children: requirement.tech }), _jsx(Typography, { variant: "subtitle2", color: "text.secondary", children: "Status" }), _jsx(Box, { sx: { mt: 0.5, mb: 3 }, children: _jsx(Chip, { label: requirement.status, size: "small", color: requirement.status === 'Open' ? 'success' : 'default' }) })] })) : (_jsx(Box, { sx: { flexGrow: 1 }, children: _jsx(Typography, { children: "Loading..." }) })), requirement && (_jsxs(Box, { sx: { display: "flex", gap: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }, children: [_jsx(Button, { variant: "outlined", color: "primary", fullWidth: true, startIcon: _jsx(EditIcon, {}), onClick: () => onEdit && onEdit(requirement), children: "Edit" }), _jsx(Button, { variant: "outlined", color: "error", fullWidth: true, startIcon: _jsx(DeleteIcon, {}), disabled: isDeleting, onClick: () => onDelete && onDelete(requirement.id), children: isDeleting ? "Deleting..." : "Delete" })] }))] }) }));
};
