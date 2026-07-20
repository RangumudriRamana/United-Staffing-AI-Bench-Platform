import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
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
export const SubmissionListPage = () => {
    const { filters, setPage, setLimit, setSearch } = useSubmissionFilters();
    const [selectedId, setSelectedId] = useState(null);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [editingSubmission, setEditingSubmission] = useState(null);
    const { data, isLoading } = useSubmissions(filters);
    const { create, update, archive, isCreating, isUpdating, isArchiving } = useSubmissionMutations();
    const handleFilterChange = (newFilters) => {
        setSearch(newFilters.search);
    };
    const handleOpenAdd = () => {
        setEditingSubmission(null);
        setIsFormOpen(true);
    };
    const handleOpenEdit = (submission) => {
        setEditingSubmission(submission);
        setIsFormOpen(true);
    };
    const handleFormSubmit = (formData) => {
        if (editingSubmission) {
            update({ id: editingSubmission.id, payload: formData }, {
                onSuccess: () => {
                    setIsFormOpen(false);
                    setEditingSubmission(null);
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
        if (window.confirm("Are you sure you want to delete this submission?")) {
            archive(id, {
                onSuccess: () => {
                    setSelectedId(null);
                },
            });
        }
    };
    const selectedSubmission = data?.data?.find((s) => s.id === selectedId);
    return (_jsxs(Box, { sx: { p: 3 }, children: [_jsx(PageHeader, { title: "Submissions & AI Matching", subtitle: "Manage candidate submissions, track AI match scores, and monitor client pipelines.", action: _jsx(Button, { variant: "contained", startIcon: _jsx(AddIcon, {}), onClick: handleOpenAdd, children: "New Submission" }) }), _jsx(SubmissionFilters, { onFilterChange: handleFilterChange }), _jsx(SubmissionTable, { data: data?.data, isLoading: isLoading, page: filters.page, pageSize: filters.limit, totalRows: data?.total || 0, onPageChange: (_event, newPage) => setPage(newPage), onRowsPerPageChange: (e) => setLimit(parseInt(e.target.value, 10)), onViewDetails: (id) => setSelectedId(id) }), _jsx(SubmissionDrawer, { open: !!selectedId, onClose: () => setSelectedId(null), submission: selectedSubmission, onEdit: (submission) => {
                    setSelectedId(null);
                    handleOpenEdit(submission);
                }, onDelete: handleDelete, isDeleting: isArchiving }), _jsx(SubmissionFormDialog, { open: isFormOpen, onClose: () => {
                    setIsFormOpen(false);
                    setEditingSubmission(null);
                }, onSubmit: handleFormSubmit, isLoading: isCreating || isUpdating, initialData: editingSubmission })] }));
};
export default SubmissionListPage;
