import React, { useState, useEffect } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";

interface SubmissionFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading: boolean;
  initialData?: any;
}

export const SubmissionFormDialog: React.FC<SubmissionFormDialogProps> = ({
  open,
  onClose,
  onSubmit,
  isLoading,
  initialData,
}) => {
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
    } else {
      setFormData({ consultantName: "", requirementTitle: "", matchScore: 85, status: "Submitted" });
    }
  }, [initialData, open]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const isEditMode = Boolean(initialData);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isEditMode ? "Edit Submission" : "Create New Submission"}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            <TextField 
              name="consultantName"
              label="Consultant Name" 
              placeholder="e.g. John Doe" 
              value={formData.consultantName}
              onChange={handleChange}
              required
              fullWidth 
            />
            <TextField 
              name="requirementTitle"
              label="Requirement Title" 
              placeholder="e.g. Senior Full Stack Engineer" 
              value={formData.requirementTitle}
              onChange={handleChange}
              required
              fullWidth 
            />
            <TextField 
              type="number"
              name="matchScore"
              label="AI Match Score (%)" 
              value={formData.matchScore}
              onChange={handleChange}
              required
              fullWidth 
            />
            <TextField
              select
              name="status"
              label="Status"
              value={formData.status}
              onChange={handleChange}
              fullWidth
            >
              <MenuItem value="Submitted">Submitted</MenuItem>
              <MenuItem value="Interviewing">Interviewing</MenuItem>
              <MenuItem value="Placed">Placed</MenuItem>
              <MenuItem value="Rejected">Rejected</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={onClose} disabled={isLoading}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? "Saving..." : isEditMode ? "Update Submission" : "Save Submission"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};