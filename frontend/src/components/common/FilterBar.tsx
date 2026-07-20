import React from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";

interface FilterBarProps {
  children: React.ReactNode;
}

export const FilterBar: React.FC<FilterBarProps> = ({ children }) => {
  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 2, 
        mb: 3, 
        display: "flex", 
        flexWrap: "wrap", 
        gap: 2, 
        alignItems: "center",
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 2
      }}
    >
      {children}
    </Paper>
  );
};