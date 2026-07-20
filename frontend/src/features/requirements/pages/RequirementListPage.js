import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
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
export const RequirementListPage = () => {
    const { filters, setPage, setLimit, setSearch } = useRequirementFilters();
    const [selectedId, setSelectedId] = useState(null);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [editingRequirement, setEditingRequirement] = useState(null);
    const { data, isLoading } = useRequirements(filters);
    const { create, update, archive, isCreating, isUpdating, isArchiving } = useRequirementMutations();
    const handleFilterChange = (newFilters) => {
        setSearch(newFilters.search);
    };
    const handleOpenAdd = () => {
        setEditingRequirement(null);
        setIsFormOpen(true);
    };
    const handleOpenEdit = (requirement) => {
        setEditingRequirement(requirement);
        setIsFormOpen(true);
    };
    const handleFormSubmit = (formData) => {
        if (editingRequirement) {
            update({ id: editingRequirement.id, payload: formData }, {
                onSuccess: () => {
                    setIsFormOpen(false);
                    setEditingRequirement(null);
                },
            });
        }
        else {
            create(formData, {
                onSuccess: () => {
                    setIsFormOpen(false);
                },
            });
        }
    };
    const handleDelete = (id) => {
        if (window.confirm("Are you sure you want to delete this requirement?")) {
            archive(id, {
                onSuccess: () => {
                    setSelectedId(null);
                },
            });
        }
    };
    const selectedRequirement = data?.data?.find((r) => r.id === selectedId);
    return (_jsxs(Box, { sx: { p: 3 }, children: [_jsx(PageHeader, { title: "Job Requirements", subtitle: "Manage client openings, technology needs, and active pipelines.", action: _jsx(Button, { variant: "contained", startIcon: _jsx(AddIcon, {}), onClick: handleOpenAdd, children: "Add Requirement" }) }), _jsx(RequirementFilters, { onFilterChange: handleFilterChange }), _jsx(RequirementTable, { data: data?.data, isLoading: isLoading, page: filters.page, pageSize: filters.limit, totalRows: data?.total || 0, onPageChange: (_event, newPage) => setPage(newPage), onRowsPerPageChange: (e) => setLimit(parseInt(e.target.value, 10)), onViewDetails: (id) => setSelectedId(id) }), _jsx(RequirementDrawer, { open: !!selectedId, onClose: () => setSelectedId(null), requirement: selectedRequirement, onEdit: (requirement) => {
                    setSelectedId(null);
                    handleOpenEdit(requirement);
                }, onDelete: handleDelete, isDeleting: isArchiving }), _jsx(RequirementFormDialog, { open: isFormOpen, onClose: () => {
                    setIsFormOpen(false);
                    setEditingRequirement(null);
                }, onSubmit: handleFormSubmit, isLoading: isCreating || isUpdating, initialData: editingRequirement })] }));
};
export default RequirementListPage;
