import React from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import SearchIcon from "@mui/icons-material/Search";

interface RequirementFiltersProps {
  onFilterChange: (filters: { search: string }) => void;
}

export const RequirementFilters: React.FC<RequirementFiltersProps> = ({ onFilterChange }) => {
  return (
    <Box sx={{ mb: 3, display: "flex", gap: 2, alignItems: "center" }}>
      <TextField
        placeholder="Search requirements by title, client, or tech..."
        size="small"
        sx={{ width: 350 }}
        onChange={(e) => onFilterChange({ search: e.target.value })}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
        }}
      />
    </Box>
  );
};