import React from "react";
import { EntityDataGrid } from "@/components/common/EntityDataGrid";
import Chip from "@mui/material/Chip";
import Button from "@mui/material/Button";

interface Submission {
  id: string;
  consultantName: string;
  requirementTitle: string;
  matchScore: number;
  status: string;
}

interface SubmissionTableProps {
  data?: Submission[];
  isLoading?: boolean;
  page: number;
  pageSize: number;
  totalRows: number;
  onPageChange: (event: unknown, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onViewDetails: (id: string) => void;
}

export const SubmissionTable: React.FC<SubmissionTableProps> = ({ 
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
    { id: "consultantName", label: "Consultant", render: (row: Submission) => row.consultantName },
    { id: "requirementTitle", label: "Requirement", render: (row: Submission) => row.requirementTitle },
    { 
      id: "matchScore", 
      label: "AI Match Score", 
      render: (row: Submission) => (
        <Chip 
          label={`${row.matchScore || 0}%`} 
          size="small" 
          color={row.matchScore >= 80 ? 'success' : row.matchScore >= 50 ? 'warning' : 'default'} 
        />
      ) 
    },
    { 
      id: "status", 
      label: "Status", 
      render: (row: Submission) => (
        <Chip 
          label={row.status} 
          size="small" 
          color={row.status === 'Submitted' ? 'primary' : 'default'} 
        />
      ) 
    },
    { 
      id: "actions", 
      label: "Actions", 
      render: (row: Submission) => (
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