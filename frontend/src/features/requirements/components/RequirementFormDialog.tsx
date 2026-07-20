import React, { useState, useEffect } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";

interface RequirementFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading: boolean;
  initialData?: any;
}

export const RequirementFormDialog: React.FC<RequirementFormDialogProps> = ({
  open,
  onClose,
  onSubmit,
  isLoading,
  initialData,
}) => {
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
    } else {
      setFormData({ title: "", client: "", tech: "", status: "Open" });
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
        <DialogTitle>{isEditMode ? "Edit Requirement" : "Add New Requirement"}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            <TextField 
              name="title"
              label="Job Title" 
              placeholder="e.g. Senior Full Stack Engineer" 
              value={formData.title}
              onChange={handleChange}
              required
              fullWidth 
            />
            <TextField 
              name="client"
              label="Client Name" 
              placeholder="e.g. Acme Corp" 
              value={formData.client}
              onChange={handleChange}
              required
              fullWidth 
            />
            <TextField 
              name="tech"
              label="Primary Technology" 
              placeholder="e.g. React / Node.js" 
              value={formData.tech}
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
              <MenuItem value="Open">Open</MenuItem>
              <MenuItem value="In Progress">In Progress</MenuItem>
              <MenuItem value="Closed">Closed</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={onClose} disabled={isLoading}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? "Saving..." : isEditMode ? "Update Requirement" : "Save Requirement"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};