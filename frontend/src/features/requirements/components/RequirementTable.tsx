import React from "react";
import { EntityDataGrid } from "@/components/common/EntityDataGrid";
import Chip from "@mui/material/Chip";
import Button from "@mui/material/Button";

interface Requirement {
  id: string;
  title: string;
  client: string;
  tech: string;
  status: string;
}

interface RequirementTableProps {
  data?: Requirement[];
  isLoading?: boolean;
  page: number;
  pageSize: number;
  totalRows: number;
  onPageChange: (event: unknown, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onViewDetails: (id: string) => void;
}

export const RequirementTable: React.FC<RequirementTableProps> = ({ 
  data, 
  isLoading, 
  page,
  pageSize,
  totalRows,
  onPageChange,
  onRowsPerPageChange,
  onViewDetails 
}) => {
  const columns = [
    { id: "title", label: "Job Title", render: (row: Requirement) => row.title },
    { id: "client", label: "Client", render: (row: Requirement) => row.client },
    { id: "tech", label: "Technology", render: (row: Requirement) => row.tech },
    { 
      id: "status", 
      label: "Status", 
      render: (row: Requirement) => (
        <Chip 
          label={row.status} 
          size="small" 
          color={row.status === 'Open' ? 'success' : 'default'} 
        />
      ) 
    },
    { 
      id: "actions", 
      label: "Actions", 
      render: (row: Requirement) => (
        <Button 
          variant="outlined" 
          size="small" 
          onClick={() => onViewDetails(row.id)}
        >
          View
        </Button>
      ) 
    },
  ];

  return (
    <EntityDataGrid 
      columns={columns} 
      data={data} 
      isLoading={isLoading}
      page={page}
      pageSize={pageSize}
      totalRows={totalRows}
      onPageChange={onPageChange}
      onRowsPerPageChange={onRowsPerPageChange}
    />
  );
};