import React, { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import AddIcon from "@mui/icons-material/Add";
import { PageHeader } from "@/components/common/PageHeader";

// Hooks
import { useRequirements } from "../hooks/useRequirements";
import { useRequirementMutations } from "../hooks/useRequirementMutations";
import { useRequirementFilters } from "../hooks/useRequirementFilters";

// Components
import { RequirementFilters } from "../components/RequirementFilters";
import { RequirementTable } from "../components/RequirementTable";
import { RequirementDrawer } from "../components/RequirementDrawer";
import { RequirementFormDialog } from "../components/RequirementFormDialog";

export const RequirementListPage: React.FC = () => {
  const { filters, setPage, setLimit, setSearch } = useRequirementFilters();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRequirement, setEditingRequirement] = useState<any>(null);

  const { data, isLoading } = useRequirements(filters);
  const { create, update, archive, isCreating, isUpdating, isArchiving } = useRequirementMutations();

  const handleFilterChange = (newFilters: { search: string }) => {
    setSearch(newFilters.search);
  };

  const handleOpenAdd = () => {
    setEditingRequirement(null);
    setIsFormOpen(true);
  };

  const handleOpenEdit = (requirement: any) => {
    setEditingRequirement(requirement);
    setIsFormOpen(true);
  };

  const handleFormSubmit = (formData: any) => {
    if (editingRequirement) {
      update(
        { id: editingRequirement.id, payload: formData },
        {
          onSuccess: () => {
            setIsFormOpen(false);
            setEditingRequirement(null);
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
    if (window.confirm("Are you sure you want to delete this requirement?")) {
      archive(id, {
        onSuccess: () => {
          setSelectedId(null);
        },
      });
    }
  };

  const selectedRequirement = data?.data?.find((r: any) => r.id === selectedId);

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader 
        title="Job Requirements" 
        subtitle="Manage client openings, technology needs, and active pipelines."
        action={
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={handleOpenAdd}
          >
            Add Requirement
          </Button>
        } 
      />

      <RequirementFilters onFilterChange={handleFilterChange} />
      
      <RequirementTable 
        data={data?.data} 
        isLoading={isLoading} 
        page={filters.page}
        pageSize={filters.limit}
        totalRows={data?.total || 0}
        onPageChange={(_event: unknown, newPage: number) => setPage(newPage)}
        onRowsPerPageChange={(e: React.ChangeEvent<HTMLInputElement>) => setLimit(parseInt(e.target.value, 10))}
        onViewDetails={(id: string) => setSelectedId(id)} 
      />

      <RequirementDrawer 
        open={!!selectedId} 
        onClose={() => setSelectedId(null)} 
        requirement={selectedRequirement}
        onEdit={(requirement) => {
          setSelectedId(null);
          handleOpenEdit(requirement);
        }}
        onDelete={handleDelete}
        isDeleting={isArchiving}
      />

      <RequirementFormDialog 
        open={isFormOpen} 
        onClose={() => {
          setIsFormOpen(false);
          setEditingRequirement(null);
        }} 
        onSubmit={handleFormSubmit}
        isLoading={isCreating || isUpdating}
        initialData={editingRequirement}
      />
    </Box>
  );
};

export default RequirementListPage;