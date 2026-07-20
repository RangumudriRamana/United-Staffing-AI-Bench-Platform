import React from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TablePagination from "@mui/material/TablePagination";
import TableSortLabel from "@mui/material/TableSortLabel";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";

export interface Column<T> {
  id: string;
  label: string;
  sortable?: boolean;
  render: (item: T) => React.ReactNode;
}

interface EntityDataGridProps<T> {
  columns: Column<T>[];
  data?: T[];
  isLoading?: boolean;
  // Pagination Props
  page: number;         // 0-indexed for MUI
  pageSize: number;
  totalRows: number;
  onPageChange: (event: unknown, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  // Sorting Props
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  onSort?: (property: string) => void;
  // Empty State Customization
  emptyMessage?: string;
}

export function EntityDataGrid<T extends { id: string | number }>({
  columns,
  data = [],
  isLoading = false,
  page,
  pageSize,
  totalRows,
  onPageChange,
  onRowsPerPageChange,
  sortBy,
  sortOrder = 'asc',
  onSort,
  emptyMessage = "No records found.",
}: EntityDataGridProps<T>) {
  return (
    <Paper elevation={0} sx={{ width: '100%', overflow: 'hidden', border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
      <TableContainer>
        <Table stickyHeader>
          <TableHead sx={{ bgcolor: 'action.hover' }}>
            <TableRow>
              {columns.map((col) => (
                <TableCell key={col.id} sx={{ fontWeight: 'bold' }}>
                  {col.sortable && onSort ? (
                    <TableSortLabel
                      active={sortBy === col.id}
                      direction={sortBy === col.id ? sortOrder : 'asc'}
                      onClick={() => onSort(col.id)}
                    >
                      {col.label}
                    </TableSortLabel>
                  ) : (
                    col.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              // Structured Skeletons mirroring final row heights to prevent layout shifts
              Array.from(new Array(pageSize > 5 ? 5 : pageSize)).map((_, rowIndex) => (
                <TableRow key={`skeleton-${rowIndex}`}>
                  {columns.map((col, colIndex) => (
                    <TableCell key={`skeleton-cell-${colIndex}`}>
                      <Skeleton variant="text" width="80%" height={24} />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} align="center" sx={{ py: 6 }}>
                  <Typography color="text.secondary">{emptyMessage}</Typography>
                </TableCell>
              </TableRow>
            ) : (
              data.map((row) => (
                <TableRow key={row.id} hover>
                  {columns.map((col) => (
                    <TableCell key={col.id}>{col.render(row)}</TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 25, 50]}
        component="div"
        count={totalRows}
        rowsPerPage={pageSize}
        page={page}
        onPageChange={onPageChange}
        onRowsPerPageChange={onRowsPerPageChange}
      />
    </Paper>
  );
}

export default EntityDataGrid;