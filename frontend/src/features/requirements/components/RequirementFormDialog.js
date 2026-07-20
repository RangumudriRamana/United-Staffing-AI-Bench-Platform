import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
export const RequirementFormDialog = ({ open, onClose, onSubmit, isLoading, initialData, }) => {
    const [formData, setFormData] = useState({
        title: "",
        client: "",
        tech: "",
        status: "Open",
    });
    useEffect(() => {
        if (initialData) {
            setFormData({
                title: initialData.title || "",
                client: initialData.client || "",
                tech: initialData.tech || "",
                status: initialData.status || "Open",
            });
        }
        else {
            setFormData({ title: "", client: "", tech: "", status: "Open" });
        }
    }, [initialData, open]);
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };
    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };
    const isEditMode = Boolean(initialData);
    return (_jsx(Dialog, { open: open, onClose: onClose, maxWidth: "sm", fullWidth: true, children: _jsxs("form", { onSubmit: handleSubmit, children: [_jsx(DialogTitle, { children: isEditMode ? "Edit Requirement" : "Add New Requirement" }), _jsx(DialogContent, { children: _jsxs(Box, { sx: { display: "flex", flexDirection: "column", gap: 2, mt: 1 }, children: [_jsx(TextField, { name: "title", label: "Job Title", placeholder: "e.g. Senior Full Stack Engineer", value: formData.title, onChange: handleChange, required: true, fullWidth: true }), _jsx(TextField, { name: "client", label: "Client Name", placeholder: "e.g. Acme Corp", value: formData.client, onChange: handleChange, required: true, fullWidth: true }), _jsx(TextField, { name: "tech", label: "Primary Technology", placeholder: "e.g. React / Node.js", value: formData.tech, onChange: handleChange, required: true, fullWidth: true }), _jsxs(TextField, { select: true, name: "status", label: "Status", value: formData.status, onChange: handleChange, fullWidth: true, children: [_jsx(MenuItem, { value: "Open", children: "Open" }), _jsx(MenuItem, { value: "In Progress", children: "In Progress" }), _jsx(MenuItem, { value: "Closed", children: "Closed" })] })] }) }), _jsxs(DialogActions, { sx: { p: 2 }, children: [_jsx(Button, { onClick: onClose, disabled: isLoading, children: "Cancel" }), _jsx(Button, { type: "submit", variant: "contained", disabled: isLoading, children: isLoading ? "Saving..." : isEditMode ? "Update Requirement" : "Save Requirement" })] })] }) }));
};
