import React from "react";
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

interface SubmissionDrawerProps {
  open: boolean;
  onClose: () => void;
  submission: any;
  onEdit?: (submission: any) => void;
  onDelete?: (id: string) => void;
  isDeleting?: boolean;
}

export const SubmissionDrawer: React.FC<SubmissionDrawerProps> = ({ 
  open, 
  onClose, 
  submission, 
  onEdit, 
  onDelete,
  isDeleting 
}) => {
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 420, p: 3, display: "flex", flexDirection: "column", height: "100%" }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
          <Typography variant="h6">Submission Details</Typography>
          <IconButton onClick={onClose}><CloseIcon /></IconButton>
        </Box>
        <Divider sx={{ mb: 3 }} />
        
        {submission ? (
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">Consultant</Typography>
            <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>{submission.consultantName}</Typography>
            
            <Typography variant="subtitle2" color="text.secondary">Requirement</Typography>
            <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>{submission.requirementTitle}</Typography>
            
            <Typography variant="subtitle2" color="text.secondary">AI Match Score</Typography>
            <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>{submission.matchScore}%</Typography>

            <Typography variant="subtitle2" color="text.secondary">Status</Typography>
            <Box sx={{ mt: 0.5, mb: 3 }}>
              <Chip 
                label={submission.status} 
                size="small" 
                color={submission.status === 'Submitted' ? 'primary' : 'default'} 
              />
            </Box>
          </Box>
        ) : (
          <Box sx={{ flexGrow: 1 }}><Typography>Loading...</Typography></Box>
        )}

        {submission && (
          <Box sx={{ display: "flex", gap: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Button 
              variant="outlined" 
              color="primary" 
              fullWidth 
              startIcon={<EditIcon />}
              onClick={() => onEdit && onEdit(submission)}
            >
              Edit
            </Button>
            <Button 
              variant="outlined" 
              color="error" 
              fullWidth 
              startIcon={<DeleteIcon />}
              disabled={isDeleting}
              onClick={() => onDelete && onDelete(submission.id)}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </Button>
          </Box>
        )}
      </Box>
    </Drawer>
  );
};