import { jsx as _jsx } from "react/jsx-runtime";
import { EntityDataGrid } from "@/components/common/EntityDataGrid";
import Chip from "@mui/material/Chip";
import Button from "@mui/material/Button";
export const RequirementTable = ({ data, isLoading, page, pageSize, totalRows, onPageChange, onRowsPerPageChange, onViewDetails }) => {
    const columns = [
        { id: "title", label: "Job Title", render: (row) => row.title },
        { id: "client", label: "Client", render: (row) => row.client },
        { id: "tech", label: "Technology", render: (row) => row.tech },
        {
            id: "status",
            label: "Status",
            render: (row) => (_jsx(Chip, { label: row.status, size: "small", color: row.status === 'Open' ? 'success' : 'default' }))
        },
        {
            id: "actions",
            label: "Actions",
            render: (row) => (_jsx(Button, { variant: "outlined", size: "small", onClick: () => onViewDetails(row.id), children: "View" }))
        },
    ];
    return (_jsx(EntityDataGrid, { columns: columns, data: data, isLoading: isLoading, page: page, pageSize: pageSize, totalRows: totalRows, onPageChange: onPageChange, onRowsPerPageChange: onRowsPerPageChange }));
};
