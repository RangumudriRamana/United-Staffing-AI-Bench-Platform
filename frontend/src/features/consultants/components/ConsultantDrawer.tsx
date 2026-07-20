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

interface ConsultantDrawerProps {
  open: boolean;
  onClose: () => void;
  consultant: any;
  onEdit?: (consultant: any) => void;
  onDelete?: (id: string) => void;
  isDeleting?: boolean;
}

export const ConsultantDrawer: React.FC<ConsultantDrawerProps> = ({ 
  open, 
  onClose, 
  consultant, 
  onEdit, 
  onDelete,
  isDeleting 
}) => {
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 420, p: 3, display: "flex", flexDirection: "column", height: "100%" }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
          <Typography variant="h6">Consultant Details</Typography>
          <IconButton onClick={onClose}><CloseIcon /></IconButton>
        </Box>
        <Divider sx={{ mb: 3 }} />
        
        {consultant ? (
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">Full Name</Typography>
            <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>{consultant.name}</Typography>
            
            <Typography variant="subtitle2" color="text.secondary">Technology</Typography>
            <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>{consultant.tech}</Typography>
            
            <Typography variant="subtitle2" color="text.secondary">Status</Typography>
            <Box sx={{ mt: 0.5, mb: 3 }}>
              <Chip 
                label={consultant.status} 
                size="small" 
                color={consultant.status === 'Available' ? 'success' : 'default'} 
              />
            </Box>
          </Box>
        ) : (
          <Box sx={{ flexGrow: 1 }}><Typography>Loading...</Typography></Box>
        )}

        {consultant && (
          <Box sx={{ display: "flex", gap: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Button 
              variant="outlined" 
              color="primary" 
              fullWidth 
              startIcon={<EditIcon />}
              onClick={() => onEdit && onEdit(consultant)}
            >
              Edit
            </Button>
            <Button 
              variant="outlined" 
              color="error" 
              fullWidth 
              startIcon={<DeleteIcon />}
              disabled={isDeleting}
              onClick={() => onDelete && onDelete(consultant.id)}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </Button>
          </Box>
        )}
      </Box>
    </Drawer>
  );
};