import React, { useState } from "react";
import { FilterBar } from "@/components/common/FilterBar";
import { SearchInput } from "@/components/common/SearchInput";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";

interface FilterState {
  search: string;
  technology: string;
}

interface ConsultantFiltersProps {
  onFilterChange: (filters: FilterState) => void;
}

export const ConsultantFilters: React.FC<ConsultantFiltersProps> = ({ onFilterChange }) => {
  const [filters, setFilters] = useState<FilterState>({ search: "", technology: "" });

  const handleChange = (newFilters: Partial<FilterState>) => {
    const updated = { ...filters, ...newFilters };
    setFilters(updated);
    onFilterChange(updated);
  };

  return (
    <FilterBar>
      <SearchInput 
        placeholder="Search by name or email..." 
        onSearch={(val) => handleChange({ search: val })} 
      />
      <TextField
        select
        size="small"
        label="Technology"
        value={filters.technology}
        onChange={(e) => handleChange({ technology: e.target.value })}
        sx={{ minWidth: 150 }}
      >
        <MenuItem value="">All Technologies</MenuItem>
        <MenuItem value="react">React</MenuItem>
        <MenuItem value="python">Python</MenuItem>
        <MenuItem value="aws">AWS</MenuItem>
      </TextField>
    </FilterBar>
  );
};