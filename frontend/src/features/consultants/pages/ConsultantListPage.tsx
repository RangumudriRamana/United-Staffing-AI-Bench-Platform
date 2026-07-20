import React, { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import AddIcon from "@mui/icons-material/Add";
import { PageHeader } from "@/components/common/PageHeader";

// Hooks
import { useConsultants } from "../hooks/useConsultants";
import { useConsultantMutations } from "../hooks/useConsultantMutations";
import { useConsultantFilters } from "../hooks/useConsultantFilters";

// Components
import { ConsultantFilters } from "../components/ConsultantFilters";
import { ConsultantTable } from "../components/ConsultantTable";
import { ConsultantDrawer } from "../components/ConsultantDrawer";
import { ConsultantFormDialog } from "../components/ConsultantFormDialog";

export const ConsultantListPage: React.FC = () => {
  // Use centralized URL-synchronized filters hook
  const { filters, setPage, setLimit, setSearch } = useConsultantFilters();

  // Local UI State
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingConsultant, setEditingConsultant] = useState<any>(null);

  // Data Layer (matching hook's exact return names: create, update, archive)
  const { data, isLoading } = useConsultants(filters);
  const { create, update, archive, isCreating, isUpdating, isArchiving } = useConsultantMutations();

  // Handlers
  const handleFilterChange = (newFilters: { search: string }) => {
    setSearch(newFilters.search);
  };

  const handleOpenAdd = () => {
    setEditingConsultant(null);
    setIsFormOpen(true);
  };

  const handleOpenEdit = (consultant: any) => {
    setEditingConsultant(consultant);
    setIsFormOpen(true);
  };

  const handleFormSubmit = (formData: any) => {
    console.log("Form submitted with data:", formData);

    if (editingConsultant) {
      update(
        { id: editingConsultant.id, payload: formData },
        {
          onSuccess: () => {
            setIsFormOpen(false);
            setEditingConsultant(null);
          },
          onError: (error) => {
            console.error("Failed to update consultant:", error);
          },
        }
      );
    } else {
      create(formData, {
        onSuccess: () => {
          setIsFormOpen(false);
        },
        onError: (error) => {
          console.error("Failed to create consultant:", error);
        },
      });
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm("Are you sure you want to delete/archive this consultant?")) {
      archive(id, {
        onSuccess: () => {
          setSelectedId(null); // Close drawer on delete
        },
      });
    }
  };

  const selectedConsultant = data?.data?.find((c: any) => c.id === selectedId);

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader 
        title="Consultants" 
        subtitle="Manage active profiles, bench availability, and deployment details."
        action={
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={handleOpenAdd}
          >
            Add Consultant
          </Button>
        } 
      />

      <ConsultantFilters onFilterChange={handleFilterChange} />
      
      <ConsultantTable 
        data={data?.data} 
        isLoading={isLoading} 
        page={filters.page}
        pageSize={filters.limit}
        totalRows={data?.total || 0}
        onPageChange={(_event: unknown, newPage: number) => setPage(newPage)}
        onRowsPerPageChange={(e: React.ChangeEvent<HTMLInputElement>) => setLimit(parseInt(e.target.value, 10))}
        onViewDetails={(id: string) => setSelectedId(id)} 
      />

      <ConsultantDrawer 
        open={!!selectedId} 
        onClose={() => setSelectedId(null)} 
        consultant={selectedConsultant}
        onEdit={(consultant) => {
          setSelectedId(null); // Close drawer before opening edit modal
          handleOpenEdit(consultant);
        }}
        onDelete={handleDelete}
        isDeleting={isArchiving}
      />

      <ConsultantFormDialog 
        open={isFormOpen} 
        onClose={() => {
          setIsFormOpen(false);
          setEditingConsultant(null);
        }} 
        onSubmit={handleFormSubmit}
        isLoading={isCreating || isUpdating}
        initialData={editingConsultant}
      />
    </Box>
  );
};

export default ConsultantListPage;