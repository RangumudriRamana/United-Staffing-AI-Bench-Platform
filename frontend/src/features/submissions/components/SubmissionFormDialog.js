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
export const SubmissionFormDialog = ({ open, onClose, onSubmit, isLoading, initialData, }) => {
    const [formData, setFormData] = useState({
        consultantName: "",
        requirementTitle: "",
        matchScore: 85,
        status: "Submitted",
    });
    useEffect(() => {
        if (initialData) {
            setFormData({
                consultantName: initialData.consultantName || "",
                requirementTitle: initialData.requirementTitle || "",
                matchScore: initialData.matchScore || 85,
                status: initialData.status || "Submitted",
            });
        }
        else {
            setFormData({ consultantName: "", requirementTitle: "", matchScore: 85, status: "Submitted" });
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
    return (_jsx(Dialog, { open: open, onClose: onClose, maxWidth: "sm", fullWidth: true, children: _jsxs("form", { onSubmit: handleSubmit, children: [_jsx(DialogTitle, { children: isEditMode ? "Edit Submission" : "Create New Submission" }), _jsx(DialogContent, { children: _jsxs(Box, { sx: { display: "flex", flexDirection: "column", gap: 2, mt: 1 }, children: [_jsx(TextField, { name: "consultantName", label: "Consultant Name", placeholder: "e.g. John Doe", value: formData.consultantName, onChange: handleChange, required: true, fullWidth: true }), _jsx(TextField, { name: "requirementTitle", label: "Requirement Title", placeholder: "e.g. Senior Full Stack Engineer", value: formData.requirementTitle, onChange: handleChange, required: true, fullWidth: true }), _jsx(TextField, { type: "number", name: "matchScore", label: "AI Match Score (%)", value: formData.matchScore, onChange: handleChange, required: true, fullWidth: true }), _jsxs(TextField, { select: true, name: "status", label: "Status", value: formData.status, onChange: handleChange, fullWidth: true, children: [_jsx(MenuItem, { value: "Submitted", children: "Submitted" }), _jsx(MenuItem, { value: "Interviewing", children: "Interviewing" }), _jsx(MenuItem, { value: "Placed", children: "Placed" }), _jsx(MenuItem, { value: "Rejected", children: "Rejected" })] })] }) }), _jsxs(DialogActions, { sx: { p: 2 }, children: [_jsx(Button, { onClick: onClose, disabled: isLoading, children: "Cancel" }), _jsx(Button, { type: "submit", variant: "contained", disabled: isLoading, children: isLoading ? "Saving..." : isEditMode ? "Update Submission" : "Save Submission" })] })] }) }));
};
