import { useState } from "react";

import { useRequirements } from "@/hooks/useRequirements";
import RequirementsTable from "@/components/requirements/RequirementsTable";

export default function RequirementsPage() {
  const [search, setSearch] = useState("");

  const { data, isLoading, error } = useRequirements(
    search.trim()
      ? {
          search: search.trim(),
        }
      : undefined
  );

  if (isLoading && !data) {
    return <div>Loading requirements...</div>;
  }

  if (error) {
    return (
      <div className="text-red-600">
        Failed to load requirements.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Requirements
        </h1>

        <p className="text-muted-foreground">
          Manage job requirements and staffing opportunities
        </p>
      </div>

      <div className="flex items-center justify-between gap-4">
        <input
          type="text"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search requirements..."
          className="w-full max-w-md rounded-lg border px-4 py-2 outline-none focus:ring-2"
        />
      </div>

      <RequirementsTable
        requirements={data ?? []}
      />
    </div>
  );
}