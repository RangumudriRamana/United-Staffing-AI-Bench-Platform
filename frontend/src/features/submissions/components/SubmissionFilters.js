import { jsx as _jsx } from "react/jsx-runtime";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import SearchIcon from "@mui/icons-material/Search";
export const SubmissionFilters = ({ onFilterChange }) => {
    return (_jsx(Box, { sx: { mb: 3, display: "flex", gap: 2, alignItems: "center" }, children: _jsx(TextField, { placeholder: "Search submissions by consultant or requirement...", size: "small", sx: { width: 350 }, onChange: (e) => onFilterChange({ search: e.target.value }), InputProps: {
                startAdornment: (_jsx(InputAdornment, { position: "start", children: _jsx(SearchIcon, { color: "action" }) })),
            } }) }));
};
