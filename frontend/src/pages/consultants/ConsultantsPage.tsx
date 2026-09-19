import { useMemo, useState } from "react";

import ConsultantTable from "@/components/consultants/ConsultantTable";
import ConsultantToolbar from "@/components/consultants/ConsultantToolbar";
import { useConsultants } from "@/hooks/useConsultants";
import AddConsultantDialog from "@/components/consultants/AddConsultantDialog";


export default function ConsultantsPage() {
  const {
    data,
    isLoading,
    error,
  } = useConsultants();

  const [search, setSearch] = useState("");
  const [openDialog, setOpenDialog] = useState(false);

  const consultants = data?.data ?? [];

  const filteredConsultants = useMemo(() => {
    return consultants.filter((consultant: any) => {
      const fullName =
        `${consultant.first_name} ${consultant.last_name}`.toLowerCase();

      return (
        fullName.includes(search.toLowerCase()) ||
        consultant.email
          .toLowerCase()
          .includes(search.toLowerCase())
      );
    });
  }, [consultants, search]);

  if (isLoading) {
    return <div>Loading consultants...</div>;
  }

  if (error) {
    return (
      <div className="text-red-600">
        Failed to load consultants.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Consultants
        </h1>

        <p className="text-muted-foreground">
          Manage all consultants
        </p>
      </div>

      <ConsultantToolbar
        search={search}
        onSearchChange={setSearch}
        onAdd={() => setOpenDialog(true)}
        />

      <ConsultantTable
        consultants={filteredConsultants}
      />
      <AddConsultantDialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
       />
    </div>
  );
}
