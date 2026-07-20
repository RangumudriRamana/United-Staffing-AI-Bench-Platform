import { useSearchParams } from "react-router-dom";
export function useSubmissionFilters() {
    const [searchParams, setSearchParams] = useSearchParams();
    const page = parseInt(searchParams.get("page") || "0", 10);
    const limit = parseInt(searchParams.get("limit") || "10", 10);
    const search = searchParams.get("search") || "";
    const status = searchParams.get("status") || "";
    const setPage = (newPage) => {
        setParams({ page: newPage.toString() });
    };
    const setLimit = (newLimit) => {
        setParams({ limit: newLimit.toString(), page: "0" });
    };
    const setSearch = (newSearch) => {
        setParams({ search: newSearch, page: "0" });
    };
    const setStatus = (newStatus) => {
        setParams({ status: newStatus, page: "0" });
    };
    const resetFilters = () => {
        setSearchParams({});
    };
    const setParams = (updates) => {
        const newParams = new URLSearchParams(searchParams);
        Object.entries(updates).forEach(([key, value]) => {
            if (value) {
                newParams.set(key, value);
            }
            else {
                newParams.delete(key);
            }
        });
        setSearchParams(newParams);
    };
    return {
        filters: { page, limit, search, status },
        setPage,
        setLimit,
        setSearch,
        setStatus,
        resetFilters,
    };
}
