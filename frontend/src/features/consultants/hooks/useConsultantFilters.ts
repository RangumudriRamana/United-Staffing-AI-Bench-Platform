import { useSearchParams } from "react-router-dom";

export interface ConsultantFilterState {
  page: number;
  limit: number;
  search: string;
  status: string;
}

export function useConsultantFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse current values from URL, falling back to sensible defaults
  const page = parseInt(searchParams.get("page") || "0", 10);
  const limit = parseInt(searchParams.get("limit") || "10", 10);
  const search = searchParams.get("search") || "";
  const status = searchParams.get("status") || "";

  // Helper updaters that modify the URL search parameters cleanly
  const setPage = (newPage: number) => {
    setParams({ page: newPage.toString() });
  };

  const setLimit = (newLimit: number) => {
    setParams({ limit: newLimit.toString(), page: "0" }); // Reset to page 0 on limit change
  };

  const setSearch = (newSearch: string) => {
    setParams({ search: newSearch, page: "0" }); // Reset to page 0 on search change
  };

  const setStatus = (newStatus: string) => {
    setParams({ status: newStatus, page: "0" }); // Reset to page 0 on status filter change
  };

  const resetFilters = () => {
    setSearchParams({});
  };

  // Internal helper to merge parameters cleanly
  const setParams = (updates: Record<string, string>) => {
    const newParams = new URLSearchParams(searchParams);
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        newParams.set(key, value);
      } else {
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