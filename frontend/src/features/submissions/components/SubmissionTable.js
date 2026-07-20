import { jsx as _jsx } from "react/jsx-runtime";
import { EntityDataGrid } from "@/components/common/EntityDataGrid";
import Chip from "@mui/material/Chip";
import Button from "@mui/material/Button";
export const SubmissionTable = ({ data, isLoading, page, pageSize, totalRows, onPageChange, onRowsPerPageChange, onViewDetails }) => {
    const columns = [
        { id: "consultantName", label: "Consultant", render: (row) => row.consultantName },
        { id: "requirementTitle", label: "Requirement", render: (row) => row.requirementTitle },
        {
            id: "matchScore",
            label: "AI Match Score",
            render: (row) => (_jsx(Chip, { label: `${row.matchScore || 0}%`, size: "small", color: row.matchScore >= 80 ? 'success' : row.matchScore >= 50 ? 'warning' : 'default' }))
        },
        {
            id: "status",
            label: "Status",
            render: (row) => (_jsx(Chip, { label: row.status, size: "small", color: row.status === 'Submitted' ? 'primary' : 'default' }))
        },
        {
            id: "actions",
            label: "Actions",
            render: (row) => (_jsx(Button, { variant: "outlined", size: "small", onClick: () => onViewDetails(row.id), children: "View" }))
        },
    ];
    return (_jsx(EntityDataGrid, { columns: columns, data: data, isLoading: isLoading, page: page, pageSize: pageSize, totalRows: totalRows, onPageChange: onPageChange, onRowsPerPageChange: onRowsPerPageChange }));
};
