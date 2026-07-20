import React, { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import AddIcon from "@mui/icons-material/Add";
import { PageHeader } from "@/components/common/PageHeader";

// Hooks
import { useSubmissions } from "../hooks/useSubmissions";
import { useSubmissionMutations } from "../hooks/useSubmissionMutations";
import { useSubmissionFilters } from "../hooks/useSubmissionFilters";

// Components
import { SubmissionFilters } from "../components/SubmissionFilters";
import { SubmissionTable } from "../components/SubmissionTable";
import { SubmissionDrawer } from "../components/SubmissionDrawer";
import { SubmissionFormDialog } from "../components/SubmissionFormDialog";

export const SubmissionListPage: React.FC = () => {
  const { filters, setPage, setLimit, setSearch } = useSubmissionFilters();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingSubmission, setEditingSubmission] = useState<any>(null);

  const { data, isLoading } = useSubmissions(filters);
  const { create, update, archive, isCreating, isUpdating, isArchiving } = useSubmissionMutations();

  const handleFilterChange = (newFilters: { search: string }) => {
    setSearch(newFilters.search);
  };

  const handleOpenAdd = () => {
    setEditingSubmission(null);
    setIsFormOpen(true);
  };

  const handleOpenEdit = (submission: any) => {
    setEditingSubmission(submission);
    setIsFormOpen(true);
  };

  const handleFormSubmit = (formData: any) => {
    if (editingSubmission) {
      update(
        { id: editingSubmission.id, payload: formData },
        {
          onSuccess: () => {
            setIsFormOpen(false);
            setEditingSubmission(null);
          },
        }
      );
    } else {
      create(formData, {
        onSuccess: () => {
          setIsFormOpen(false);
        },
      });
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm("Are you sure you want to delete this submission?")) {
      archive(id, {
        onSuccess: () => {
          setSelectedId(null);
        },
      });
    }
  };

  const selectedSubmission = data?.data?.find((s: any) => s.id === selectedId);

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader 
        title="Submissions & AI Matching" 
        subtitle="Manage candidate submissions, track AI match scores, and monitor client pipelines."
        action={
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={handleOpenAdd}
          >
            New Submission
          </Button>
        } 
      />

      <SubmissionFilters onFilterChange={handleFilterChange} />
      
      <SubmissionTable 
        data={data?.data} 
        isLoading={isLoading} 
        page={filters.page}
        pageSize={filters.limit}
        totalRows={data?.total || 0}
        onPageChange={(_event: unknown, newPage: number) => setPage(newPage)}
        onRowsPerPageChange={(e: React.ChangeEvent<HTMLInputElement>) => setLimit(parseInt(e.target.value, 10))}
        onViewDetails={(id: string) => setSelectedId(id)} 
      />

      <SubmissionDrawer 
        open={!!selectedId} 
        onClose={() => setSelectedId(null)} 
        submission={selectedSubmission}
        onEdit={(submission) => {
          setSelectedId(null);
          handleOpenEdit(submission);
        }}
        onDelete={handleDelete}
        isDeleting={isArchiving}
      />

      <SubmissionFormDialog 
        open={isFormOpen} 
        onClose={() => {
          setIsFormOpen(false);
          setEditingSubmission(null);
        }} 
        onSubmit={handleFormSubmit}
        isLoading={isCreating || isUpdating}
        initialData={editingSubmission}
      />
    </Box>
  );
};

export default SubmissionListPage;