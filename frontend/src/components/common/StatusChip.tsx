import React from 'react';
import { Chip, ChipProps } from '@mui/material';

// Expandable type for standard system enums (Consultant status, Visa, Availability, etc.)
export type StatusType = 
  | 'AVAILABLE' 
  | 'DEPLOYED' 
  | 'BENCH' 
  | 'INACTIVE' 
  | 'H1B' 
  | 'GC' 
  | 'CITIZEN' 
  | 'OPT' 
  | string;

interface StatusChipProps extends Omit<ChipProps, 'color'> {
  status: StatusType;
}

const statusConfig: Record<string, { label: string; color: 'success' | 'primary' | 'warning' | 'error' | 'default' }> = {
  AVAILABLE: { label: 'Available', color: 'success' },
  DEPLOYED: { label: 'Deployed', color: 'primary' },
  BENCH: { label: 'On Bench', color: 'warning' },
  INACTIVE: { label: 'Inactive', color: 'error' },
  H1B: { label: 'H1-B', color: 'primary' },
  GC: { label: 'Green Card', color: 'success' },
  CITIZEN: { label: 'US Citizen', color: 'success' },
  OPT: { label: 'OPT', color: 'warning' },
};

export const StatusChip: React.FC<StatusChipProps> = ({ status, ...props }) => {
  const normalizedKey = status?.toUpperCase() || '';
  const config = statusConfig[normalizedKey] || { label: status, color: 'default' };

  return (
    <Chip
      label={config.label}
      color={config.color}
      size="small"
      variant="outlined"
      {...props}
      style={{ fontWeight: 500, textTransform: 'capitalize', ...props.style }}
    />
  );
};

export default StatusChip;