import React, { useState, useEffect } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";

interface ConsultantFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading: boolean;
  initialData?: any; // If present, dialog acts as an "Edit" form
}

export const ConsultantFormDialog: React.FC<ConsultantFormDialogProps> = ({
  open,
  onClose,
  onSubmit,
  isLoading,
  initialData,
}) => {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    current_title: "",
    visa_status: "H1B",
    total_experience_years: 0,
    expected_rate: 0,
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        first_name: initialData.first_name || "",
        last_name: initialData.last_name || "",
        email: initialData.email || "",
        current_title: initialData.current_title || "",
        visa_status: initialData.visa_status || "H1B",
        total_experience_years: initialData.total_experience_years || 0,
        expected_rate: initialData.expected_rate || 0,
      });
    } else {
      setFormData({
        first_name: "",
        last_name: "",
        email: "",
        current_title: "",
        visa_status: "H1B",
        total_experience_years: 0,
        expected_rate: 0,
      });
    }
  }, [initialData, open]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "total_experience_years" || name === "expected_rate" ? Number(value) : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const isEditMode = Boolean(initialData);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isEditMode ? "Edit Consultant" : "Add New Consultant"}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            <Box sx={{ display: "flex", gap: 2 }}>
              <TextField 
                name="first_name"
                label="First Name" 
                placeholder="e.g. John" 
                value={formData.first_name}
                onChange={handleChange}
                required
                fullWidth 
              />
              <TextField 
                name="last_name"
                label="Last Name" 
                placeholder="e.g. Doe" 
                value={formData.last_name}
                onChange={handleChange}
                required
                fullWidth 
              />
            </Box>
            <TextField 
              name="email"
              label="Email Address" 
              type="email"
              placeholder="john.doe@example.com" 
              value={formData.email}
              onChange={handleChange}
              required
              fullWidth 
            />
            <TextField 
              name="current_title"
              label="Current Title" 
              placeholder="e.g. Senior Full Stack Engineer" 
              value={formData.current_title}
              onChange={handleChange}
              fullWidth 
            />
            <TextField
              select
              name="visa_status"
              label="Visa Status"
              value={formData.visa_status}
              onChange={handleChange}
              required
              fullWidth
            >
              <MenuItem value="H1B">H1B</MenuItem>
              <MenuItem value="US_CITIZEN">US Citizen</MenuItem>
              <MenuItem value="GREEN_CARD">Green Card</MenuItem>
              <MenuItem value="OPT">OPT</MenuItem>
              <MenuItem value="L1">L1</MenuItem>
              <MenuItem value="TN">TN</MenuItem>
              <MenuItem value="OTHER">Other</MenuItem>
            </TextField>
            <Box sx={{ display: "flex", gap: 2 }}>
              <TextField 
                name="total_experience_years"
                label="Experience (Years)" 
                type="number"
                value={formData.total_experience_years}
                onChange={handleChange}
                fullWidth 
              />
              <TextField 
                name="expected_rate"
                label="Expected Rate ($/hr)" 
                type="number"
                value={formData.expected_rate}
                onChange={handleChange}
                fullWidth 
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={onClose} disabled={isLoading}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? "Saving..." : isEditMode ? "Update Consultant" : "Save Consultant"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};