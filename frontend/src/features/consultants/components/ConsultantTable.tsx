import React from "react";
import { EntityDataGrid } from "@/components/common/EntityDataGrid";
import Chip from "@mui/material/Chip";
import Button from "@mui/material/Button";

interface Consultant {
  id?: string | number;
  public_id?: string;
  first_name?: string;
  last_name?: string;
  name?: string;
  current_title?: string;
  tech?: string;
  visa_status?: string;
  marketing_status?: string;
  status?: string;
}

interface ConsultantTableProps {
  data?: Consultant[];
  isLoading?: boolean;
  page: number;
  pageSize: number;
  totalRows: number;
  onPageChange: (event: unknown, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onViewDetails: (id: string) => void;
}

export const ConsultantTable: React.FC<ConsultantTableProps> = ({ 
  data, 
  isLoading, 
  page,
  pageSize,
  totalRows,
  onPageChange,
  onRowsPerPageChange,
  onViewDetails 
}) => {
  // Ensure every row satisfies EntityDataGrid's requirement for a guaranteed `id`
  const formattedData = (data || []).map((item, index) => ({
    ...item,
    id: item.public_id || item.id || `consultant_${index}`,
  }));

  const columns = [
    { 
      id: "name", 
      label: "Consultant Name", 
      render: (row: any) => row.name || `${row.first_name || ''} ${row.last_name || ''}`.trim() || 'N/A' 
    },
    { 
      id: "current_title", 
      label: "Current Title", 
      render: (row: any) => row.current_title || row.tech || 'N/A' 
    },
    { 
      id: "visa_status", 
      label: "Visa Status", 
      render: (row: any) => row.visa_status || 'N/A' 
    },
    { 
      id: "marketing_status", 
      label: "Marketing Status", 
      render: (row: any) => {
        const statusVal = row.marketing_status || row.status || 'NEW';
        return (
          <Chip 
            label={statusVal} 
            size="small" 
            color={statusVal === 'READY_FOR_MARKETING' || statusVal === 'Available' ? 'success' : 'default'} 
          />
        );
      } 
    },
    { 
      id: "actions", 
      label: "Actions", 
      render: (row: any) => {
        const rowId = row.public_id || row.id;
        return (
          <Button 
            variant="outlined" 
            size="small" 
            onClick={() => rowId && onViewDetails(String(rowId))}
          >
            View
          </Button>
        );
      } 
    },
  ];

  return (
    <EntityDataGrid 
      columns={columns} 
      data={formattedData} 
      isLoading={isLoading}
      page={page}
      pageSize={pageSize}
      totalRows={totalRows}
      onPageChange={onPageChange}
      onRowsPerPageChange={onRowsPerPageChange}
    />
  );
};