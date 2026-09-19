import { useState } from "react";

import { Plus } from "lucide-react";

import type {
  Client,
  Vendor,
} from "@/features/vendors/types";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useClients } from "@/hooks/useClients";
import { useVendors as useVendorsList } from "@/hooks/useVendors";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useArchiveClient,
  useArchiveVendor,
  useCreateClient,
  useCreateVendor,
  useUpdateClient,
  useUpdateVendor,
} from "@/hooks/useVendorMutations";

function formatStatus(value: string) {
  return value.replaceAll("_", " ");
}

function formatVendorType(value: string) {
  return value.replaceAll("_", " ");
}

export default function VendorsPage() {
  const { data, isLoading, error, refetch } = useVendorsList();
  const createVendor = useCreateVendor();
  const updateVendor = useUpdateVendor();
  const archiveVendor = useArchiveVendor();

  const createClient = useCreateClient();
  const updateClient = useUpdateClient();
  const archiveClient = useArchiveClient();

  const [createClientOpen, setCreateClientOpen] =
    useState(false);

  const [clientName, setClientName] = useState("");
  const [clientDisplayName, setClientDisplayName] =
    useState("");
  const [clientIndustry, setClientIndustry] =
    useState("");
  const [clientWebsite, setClientWebsite] =
    useState("");
  const [clientLocation, setClientLocation] =
    useState("");
  const [clientNotes, setClientNotes] =
    useState("");
  const [clientPreferred, setClientPreferred] =
    useState(false);

  const [editClientOpen, setEditClientOpen] =
    useState(false);

  const [editingClientId, setEditingClientId] =
    useState<string | undefined>();

  const [editClientName, setEditClientName] =
    useState("");

  const [editClientDisplayName, setEditClientDisplayName] =
    useState("");

  const [editClientIndustry, setEditClientIndustry] =
    useState("");

  const [editClientWebsite, setEditClientWebsite] =
    useState("");

  const [editClientLocation, setEditClientLocation] =
    useState("");

  const [editClientNotes, setEditClientNotes] =
    useState("");

  const [editClientPreferred, setEditClientPreferred] =
    useState(false);

  const [createVendorOpen, setCreateVendorOpen] =
    useState(false);

  const [editVendorOpen, setEditVendorOpen] =
    useState(false);

  const [vendorName, setVendorName] = useState("");
  const [vendorWebsite, setVendorWebsite] = useState("");
  const [vendorNotes, setVendorNotes] = useState("");

  const [vendorType, setVendorType] =
    useState<Vendor["vendor_type"]>("PRIME_VENDOR");

  const [vendorTier, setVendorTier] =
    useState<Vendor["tier"]>("TIER_2");

  const [vendorPreferred, setVendorPreferred] =
    useState(false);

  const [editVendorName, setEditVendorName] =
    useState("");

  const [editVendorWebsite, setEditVendorWebsite] =
    useState("");

  const [editVendorNotes, setEditVendorNotes] =
    useState("");

  const [editVendorType, setEditVendorType] =
    useState<Vendor["vendor_type"]>("PRIME_VENDOR");

  const [editVendorTier, setEditVendorTier] =
    useState<Vendor["tier"]>("TIER_2");

  const [editVendorPreferred, setEditVendorPreferred] =
    useState(false);

  const handleCreateVendor = async (
    event: React.FormEvent<HTMLFormElement>
    ) => {
    event.preventDefault();

    if (!vendorName.trim()) {
        return;
    }

    try {
        const vendor = await createVendor.mutateAsync({
        name: vendorName.trim(),
        vendor_type: vendorType,
        tier: vendorTier,
        website: vendorWebsite.trim() || null,
        preferred: vendorPreferred,
        notes: vendorNotes.trim() || null,
        });

        setCreateVendorOpen(false);

        setVendorName("");
        setVendorWebsite("");
        setVendorNotes("");
        setVendorType("PRIME_VENDOR");
        setVendorTier("TIER_2");
        setVendorPreferred(false);

        setSelectedVendorId(vendor.public_id);
    } catch {
        // The mutation error is exposed through createVendor.error.
    }
    };

  const handleOpenEditVendor = () => {
    if (!selectedVendor) {
        return;
    }

    setEditVendorName(selectedVendor.name);
    setEditVendorWebsite(selectedVendor.website ?? "");
    setEditVendorNotes(selectedVendor.notes ?? "");
    setEditVendorType(selectedVendor.vendor_type);
    setEditVendorTier(selectedVendor.tier);
    setEditVendorPreferred(selectedVendor.preferred);

    setEditVendorOpen(true);
    };

  const handleUpdateVendor = async (
    event: React.FormEvent<HTMLFormElement>
    ) => {
    event.preventDefault();

    if (!selectedVendor || !editVendorName.trim()) {
        return;
    }

    try {
        await updateVendor.mutateAsync({
        publicId: selectedVendor.public_id,
        payload: {
            name: editVendorName.trim(),
            vendor_type: editVendorType,
            tier: editVendorTier,
            website: editVendorWebsite.trim() || null,
            preferred: editVendorPreferred,
            notes: editVendorNotes.trim() || null,
        },
        });

        setEditVendorOpen(false);
    } catch {
        // The mutation error is exposed through updateVendor.error.
    }
    };
  const handleArchiveVendor = async () => {
    if (!selectedVendor) {
        return;
    }

    const confirmed = window.confirm(
        `Archive vendor "${selectedVendor.name}"?`
    );

    if (!confirmed) {
        return;
    }

    try {
        await archiveVendor.mutateAsync(
        selectedVendor.public_id
        );

        setSelectedVendorId(undefined);
    } catch {
        // The mutation error is exposed through archiveVendor.error.
    }
    };

  const handleCreateClient = async (
    event: React.FormEvent<HTMLFormElement>
    ) => {
    event.preventDefault();

    if (!selectedVendor || !clientName.trim()) {
        return;
    }

    try {
        await createClient.mutateAsync({
        vendor_public_id: selectedVendor.public_id,
        name: clientName.trim(),
        display_name: clientDisplayName.trim() || null,
        industry: clientIndustry.trim() || null,
        website: clientWebsite.trim() || null,
        primary_location: clientLocation.trim() || null,
        notes: clientNotes.trim() || null,
        preferred: clientPreferred,
        });

        setCreateClientOpen(false);

        setClientName("");
        setClientDisplayName("");
        setClientIndustry("");
        setClientWebsite("");
        setClientLocation("");
        setClientNotes("");
        setClientPreferred(false);
    } catch {
        // The mutation error is exposed through createClient.error.
    }
    };

  const handleOpenEditClient = (client: Client) => {
    setEditingClientId(client.public_id);
    setEditClientName(client.name);
    setEditClientDisplayName(client.display_name ?? "");
    setEditClientIndustry(client.industry ?? "");
    setEditClientWebsite(client.website ?? "");
    setEditClientLocation(client.primary_location ?? "");
    setEditClientNotes(client.notes ?? "");
    setEditClientPreferred(client.preferred);

    setEditClientOpen(true);
    };

  const handleUpdateClient = async (
    event: React.FormEvent<HTMLFormElement>
    ) => {
    event.preventDefault();

    if (!editingClientId || !editClientName.trim()) {
        return;
    }

    try {
        await updateClient.mutateAsync({
        publicId: editingClientId,
        payload: {
            name: editClientName.trim(),
            display_name:
            editClientDisplayName.trim() || null,
            industry:
            editClientIndustry.trim() || null,
            website:
            editClientWebsite.trim() || null,
            primary_location:
            editClientLocation.trim() || null,
            notes:
            editClientNotes.trim() || null,
            preferred: editClientPreferred,
        },
        });

        setEditClientOpen(false);
        setEditingClientId(undefined);
    } catch {
        // The mutation error is exposed through updateClient.error.
    }
    };
  const handleArchiveClient = async (client: Client) => {
    const confirmed = window.confirm(
        `Archive client "${client.display_name ?? client.name}"?`
    );

    if (!confirmed) {
        return;
    }

    try {
        await archiveClient.mutateAsync(client.public_id);
    } catch {
        // The mutation error is exposed through archiveClient.error.
    }
    };
  const vendors = data?.data ?? [];

  const [selectedVendorId, setSelectedVendorId] =
    useState<string | undefined>();

  const selectedVendor = vendors.find(
    (vendor) => vendor.public_id === selectedVendorId
  );

  const {
    data: clients,
    isLoading: clientsLoading,
    error: clientsError,
  } = useClients(selectedVendorId);

  if (isLoading) {
    return (
      <div className="p-6">
        <p className="text-sm text-muted-foreground">
          Loading vendors...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div>
          <h1 className="text-2xl font-semibold">Vendors</h1>
          <p className="text-sm text-muted-foreground">
            Manage staffing vendors, contacts, and client relationships.
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-destructive">
              Failed to load vendors.
            </p>

            <button
              type="button"
              onClick={() => refetch()}
              className="mt-4 rounded-md border px-3 py-2 text-sm"
            >
              Retry
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
    {/* Page Header */}
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div>
        <h1 className="text-2xl font-semibold">Vendors</h1>

        <p className="mt-1 text-sm text-muted-foreground">
        Manage staffing vendors, contacts, and client relationships.
        </p>
    </div>

    <Dialog
        open={createVendorOpen}
        onOpenChange={setCreateVendorOpen}
    >
        <DialogTrigger
          render={
            <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Vendor
            </Button>
          }
        />

        <DialogContent className="sm:max-w-lg">
        <DialogHeader>
            <DialogTitle>Add Vendor</DialogTitle>

            <DialogDescription>
            Create a new staffing vendor.
            </DialogDescription>
        </DialogHeader>

        <form
            onSubmit={handleCreateVendor}
            className="space-y-5"
        >
            <div className="space-y-2">
            <Label htmlFor="vendor-name">
                Vendor Name
            </Label>

            <Input
                id="vendor-name"
                value={vendorName}
                onChange={(event) =>
                setVendorName(event.target.value)
                }
                placeholder="United Staffing Vendor"
                required
            />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
                <Label htmlFor="vendor-type">
                Vendor Type
                </Label>

                <select
                id="vendor-type"
                value={vendorType}
                onChange={(event) =>
                    setVendorType(
                    event.target.value as Vendor["vendor_type"]
                    )
                }
                className="flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-xs outline-none"
                >
                <option value="PRIME_VENDOR">
                    Prime Vendor
                </option>

                <option value="IMPLEMENTATION_PARTNER">
                    Implementation Partner
                </option>

                <option value="DIRECT_CLIENT">
                    Direct Client
                </option>

                <option value="STAFFING_FIRM">
                    Staffing Firm
                </option>
                </select>
            </div>

            <div className="space-y-2">
                <Label htmlFor="vendor-tier">
                Tier
                </Label>

                <select
                id="vendor-tier"
                value={vendorTier}
                onChange={(event) =>
                    setVendorTier(
                    event.target.value as Vendor["tier"]
                    )
                }
                className="flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-xs outline-none"
                >
                <option value="TIER_1">Tier 1</option>
                <option value="TIER_2">Tier 2</option>
                <option value="TIER_3">Tier 3</option>
                </select>
            </div>
            </div>

            <div className="space-y-2">
            <Label htmlFor="vendor-website">
                Website
            </Label>

            <Input
                id="vendor-website"
                value={vendorWebsite}
                onChange={(event) =>
                setVendorWebsite(event.target.value)
                }
                placeholder="https://example.com"
            />
            </div>

            <div className="space-y-2">
            <Label htmlFor="vendor-notes">
                Notes
            </Label>

            <textarea
                id="vendor-notes"
                value={vendorNotes}
                onChange={(event) =>
                setVendorNotes(event.target.value)
                }
                placeholder="Optional notes about this vendor"
                className="min-h-24 w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none"
            />
            </div>

            <label className="flex items-center gap-2 text-sm">
            <input
                type="checkbox"
                checked={vendorPreferred}
                onChange={(event) =>
                setVendorPreferred(event.target.checked)
                }
            />

            Preferred vendor
            </label>

            {createVendor.error && (
            <p className="text-sm text-destructive">
                Failed to create vendor. Please check the
                entered details and try again.
            </p>
            )}

            <div className="flex justify-end gap-3">
            <Button
                type="button"
                variant="outline"
                onClick={() => setCreateVendorOpen(false)}
            >
                Cancel
            </Button>

            <Button
                type="submit"
                disabled={
                createVendor.isPending ||
                !vendorName.trim()
                }
            >
                {createVendor.isPending
                ? "Creating..."
                : "Create Vendor"}
            </Button>
            </div>
        </form>
        </DialogContent>
    </Dialog>
    </div>

      {/* Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Vendors
            </CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-2xl font-semibold">
              {vendors.length}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Vendors
            </CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-2xl font-semibold">
              {vendors.filter(
                (vendor) => vendor.status === "ACTIVE"
              ).length}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Preferred Vendors
            </CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-2xl font-semibold">
              {vendors.filter((vendor) => vendor.preferred).length}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Vendor List */}
      <Card>
        <CardHeader>
          <CardTitle>Vendor Directory</CardTitle>
        </CardHeader>

        <CardContent>
          {vendors.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No vendors found.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="px-3 py-3 font-medium">
                      Vendor
                    </th>

                    <th className="px-3 py-3 font-medium">
                      Type
                    </th>

                    <th className="px-3 py-3 font-medium">
                      Tier
                    </th>

                    <th className="px-3 py-3 font-medium">
                      Status
                    </th>

                    <th className="px-3 py-3 font-medium">
                      Contacts
                    </th>

                    <th className="px-3 py-3 font-medium">
                      Preferred
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {vendors.map((vendor) => (
                    <tr
                      key={vendor.public_id}
                      onClick={() =>
                        setSelectedVendorId(vendor.public_id)
                      }
                      className={`cursor-pointer border-b transition-colors hover:bg-muted/50 ${
                        selectedVendorId === vendor.public_id
                          ? "bg-muted/50"
                          : ""
                      }`}
                    >
                      <td className="px-3 py-4">
                        <div>
                          <p className="font-medium">
                            {vendor.name}
                          </p>

                          {vendor.website && (
                            <p className="text-xs text-muted-foreground">
                              {vendor.website}
                            </p>
                          )}
                        </div>
                      </td>

                      <td className="px-3 py-4">
                        {formatVendorType(vendor.vendor_type)}
                      </td>

                      <td className="px-3 py-4">
                        {formatStatus(vendor.tier)}
                      </td>

                      <td className="px-3 py-4">
                        <span className="rounded-full border px-2.5 py-1 text-xs font-medium">
                          {formatStatus(vendor.status)}
                        </span>
                      </td>

                      <td className="px-3 py-4">
                        {vendor.contacts.length}
                      </td>

                      <td className="px-3 py-4">
                        {vendor.preferred ? "Yes" : "No"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selected Vendor Details */}
      {selectedVendor && (
        <>
            <Dialog
            open={editVendorOpen}
            onOpenChange={setEditVendorOpen}
            >
            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                <DialogTitle>Edit Vendor</DialogTitle>

                <DialogDescription>
                    Update vendor information.
                </DialogDescription>
                </DialogHeader>

                <form
                onSubmit={handleUpdateVendor}
                className="space-y-5"
                >
                <div className="space-y-2">
                    <Label htmlFor="edit-vendor-name">
                    Vendor Name
                    </Label>

                    <Input
                    id="edit-vendor-name"
                    value={editVendorName}
                    onChange={(event) =>
                        setEditVendorName(event.target.value)
                    }
                    required
                    />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                    <Label htmlFor="edit-vendor-type">
                        Vendor Type
                    </Label>

                    <select
                        id="edit-vendor-type"
                        value={editVendorType}
                        onChange={(event) =>
                        setEditVendorType(
                            event.target.value as Vendor["vendor_type"]
                        )
                        }
                        className="flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-xs outline-none"
                    >
                        <option value="PRIME_VENDOR">
                        Prime Vendor
                        </option>

                        <option value="IMPLEMENTATION_PARTNER">
                        Implementation Partner
                        </option>

                        <option value="DIRECT_CLIENT">
                        Direct Client
                        </option>

                        <option value="STAFFING_FIRM">
                        Staffing Firm
                        </option>
                    </select>
                    </div>

                    <div className="space-y-2">
                    <Label htmlFor="edit-vendor-tier">
                        Tier
                    </Label>

                    <select
                        id="edit-vendor-tier"
                        value={editVendorTier}
                        onChange={(event) =>
                        setEditVendorTier(
                            event.target.value as Vendor["tier"]
                        )
                        }
                        className="flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-xs outline-none"
                    >
                        <option value="TIER_1">Tier 1</option>
                        <option value="TIER_2">Tier 2</option>
                        <option value="TIER_3">Tier 3</option>
                    </select>
                    </div>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="edit-vendor-website">
                    Website
                    </Label>

                    <Input
                    id="edit-vendor-website"
                    value={editVendorWebsite}
                    onChange={(event) =>
                        setEditVendorWebsite(event.target.value)
                    }
                    placeholder="https://example.com"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="edit-vendor-notes">
                    Notes
                    </Label>

                    <textarea
                    id="edit-vendor-notes"
                    value={editVendorNotes}
                    onChange={(event) =>
                        setEditVendorNotes(event.target.value)
                    }
                    placeholder="Optional notes about this vendor"
                    className="min-h-24 w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none"
                    />
                </div>

                <label className="flex items-center gap-2 text-sm">
                    <input
                    type="checkbox"
                    checked={editVendorPreferred}
                    onChange={(event) =>
                        setEditVendorPreferred(event.target.checked)
                    }
                    />

                    Preferred vendor
                </label>

                {updateVendor.error && (
                    <p className="text-sm text-destructive">
                    Failed to update vendor. Please check the
                    entered details and try again.
                    </p>
                )}

                <div className="flex justify-end gap-3">
                    <Button
                    type="button"
                    variant="outline"
                    onClick={() => setEditVendorOpen(false)}
                    >
                    Cancel
                    </Button>

                    <Button
                    type="submit"
                    disabled={
                        updateVendor.isPending ||
                        !editVendorName.trim()
                    }
                    >
                    {updateVendor.isPending
                        ? "Saving..."
                        : "Save Changes"}
                    </Button>
                </div>
                </form>
            </DialogContent>
            </Dialog>

            <div className="grid gap-6 lg:grid-cols-2">
          {/* Contacts */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
            <CardTitle>
                Contacts — {selectedVendor.name}
            </CardTitle>

          <div className="flex items-center gap-2">
            <Button
                type="button"
                variant="outline"
                onClick={handleOpenEditVendor}
            >
                Edit Vendor
            </Button>

            <Button
                type="button"
                variant="destructive"
                onClick={handleArchiveVendor}
                disabled={archiveVendor.isPending}
            >
                {archiveVendor.isPending
                ? "Archiving..."
                : "Archive Vendor"}
            </Button>
           </div>
          </CardHeader>
          {archiveVendor.error && (
            <p className="mt-2 text-sm text-destructive">
                Failed to archive vendor. Please try again.
            </p>
            )}

            <CardContent>
              {selectedVendor.contacts.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No contacts recorded.
                </p>
              ) : (
                <div className="space-y-3">
                  {selectedVendor.contacts.map((contact) => (
                    <div
                      key={contact.public_id}
                      className="rounded-lg border p-4"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="font-medium">
                            {contact.name}
                          </p>

                          {contact.title && (
                            <p className="text-sm text-muted-foreground">
                              {contact.title}
                            </p>
                          )}
                        </div>

                        {contact.preferred_contact && (
                          <span className="rounded-full border px-2.5 py-1 text-xs font-medium">
                            Preferred
                          </span>
                        )}
                      </div>

                      <div className="mt-3 space-y-1 text-sm">
                        <p>{contact.email}</p>

                        {contact.phone && (
                          <p className="text-muted-foreground">
                            {contact.phone}
                          </p>
                        )}

                        {contact.linkedin && (
                          <p className="text-muted-foreground">
                            {contact.linkedin}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Clients */}
          <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <CardTitle>
                Clients — {selectedVendor.name}
            </CardTitle>

            <Button
                type="button"
                onClick={() => setCreateClientOpen(true)}
            >
                <Plus className="mr-2 h-4 w-4" />
                Add Client
            </Button>
            </CardHeader>
            {/* ADD CLIENT DIALOG */}
            <Dialog
            open={createClientOpen}
            onOpenChange={setCreateClientOpen}
            >
            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                <DialogTitle>Add Client</DialogTitle>

                <DialogDescription>
                    Create a client linked to {selectedVendor.name}.
                </DialogDescription>
                </DialogHeader>

                <form
                onSubmit={handleCreateClient}
                className="space-y-5"
                >
                <div className="space-y-2">
                    <Label htmlFor="client-name">
                    Client Name
                    </Label>

                    <Input
                    id="client-name"
                    value={clientName}
                    onChange={(event) =>
                        setClientName(event.target.value)
                    }
                    placeholder="Acme Corp"
                    required
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="client-display-name">
                    Display Name
                    </Label>

                    <Input
                    id="client-display-name"
                    value={clientDisplayName}
                    onChange={(event) =>
                        setClientDisplayName(event.target.value)
                    }
                    placeholder="Acme Corporation"
                    />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                    <Label htmlFor="client-industry">
                        Industry
                    </Label>

                    <Input
                        id="client-industry"
                        value={clientIndustry}
                        onChange={(event) =>
                        setClientIndustry(event.target.value)
                        }
                        placeholder="Information Technology"
                    />
                    </div>

                    <div className="space-y-2">
                    <Label htmlFor="client-location">
                        Primary Location
                    </Label>

                    <Input
                        id="client-location"
                        value={clientLocation}
                        onChange={(event) =>
                        setClientLocation(event.target.value)
                        }
                        placeholder="Dallas, TX"
                    />
                    </div>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="client-website">
                    Website
                    </Label>

                    <Input
                    id="client-website"
                    value={clientWebsite}
                    onChange={(event) =>
                        setClientWebsite(event.target.value)
                    }
                    placeholder="https://example.com"
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="client-notes">
                    Notes
                    </Label>

                    <textarea
                    id="client-notes"
                    value={clientNotes}
                    onChange={(event) =>
                        setClientNotes(event.target.value)
                    }
                    placeholder="Optional notes about this client"
                    className="min-h-24 w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none"
                    />
                </div>

                <label className="flex items-center gap-2 text-sm">
                    <input
                    type="checkbox"
                    checked={clientPreferred}
                    onChange={(event) =>
                        setClientPreferred(event.target.checked)
                    }
                    />

                    Preferred client
                </label>

                {createClient.error && (
                    <p className="text-sm text-destructive">
                    Failed to create client. Please check the
                    entered details and try again.
                    </p>
                )}

                <div className="flex justify-end gap-3">
                    <Button
                    type="button"
                    variant="outline"
                    onClick={() => setCreateClientOpen(false)}
                    >
                    Cancel
                    </Button>

                    <Button
                    type="submit"
                    disabled={
                        createClient.isPending ||
                        !clientName.trim()
                    }
                    >
                    {createClient.isPending
                        ? "Creating..."
                        : "Create Client"}
                    </Button>
                </div>
                </form>
            </DialogContent>
                        </Dialog>

            {/* EDIT CLIENT DIALOG */}
            <Dialog
              open={editClientOpen}
              onOpenChange={setEditClientOpen}
            >
              <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                  <DialogTitle>Edit Client</DialogTitle>

                  <DialogDescription>
                    Update client information.
                  </DialogDescription>
                </DialogHeader>

                <form
                  onSubmit={handleUpdateClient}
                  className="space-y-5"
                >
                  <div className="space-y-2">
                    <Label htmlFor="edit-client-name">
                      Client Name
                    </Label>

                    <Input
                      id="edit-client-name"
                      value={editClientName}
                      onChange={(event) =>
                        setEditClientName(event.target.value)
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-client-display-name">
                      Display Name
                    </Label>

                    <Input
                      id="edit-client-display-name"
                      value={editClientDisplayName}
                      onChange={(event) =>
                        setEditClientDisplayName(event.target.value)
                      }
                    />
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="edit-client-industry">
                        Industry
                      </Label>

                      <Input
                        id="edit-client-industry"
                        value={editClientIndustry}
                        onChange={(event) =>
                          setEditClientIndustry(event.target.value)
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-client-location">
                        Primary Location
                      </Label>

                      <Input
                        id="edit-client-location"
                        value={editClientLocation}
                        onChange={(event) =>
                          setEditClientLocation(event.target.value)
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-client-website">
                      Website
                    </Label>

                    <Input
                      id="edit-client-website"
                      value={editClientWebsite}
                      onChange={(event) =>
                        setEditClientWebsite(event.target.value)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-client-notes">
                      Notes
                    </Label>

                    <textarea
                      id="edit-client-notes"
                      value={editClientNotes}
                      onChange={(event) =>
                        setEditClientNotes(event.target.value)
                      }
                      className="min-h-24 w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none"
                    />
                  </div>

                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={editClientPreferred}
                      onChange={(event) =>
                        setEditClientPreferred(event.target.checked)
                      }
                    />

                    Preferred client
                  </label>

                  {updateClient.error && (
                    <p className="text-sm text-destructive">
                      Failed to update client. Please try again.
                    </p>
                  )}

                  <div className="flex justify-end gap-3">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setEditClientOpen(false)}
                    >
                      Cancel
                    </Button>

                    <Button
                      type="submit"
                      disabled={
                        updateClient.isPending ||
                        !editClientName.trim()
                      }
                    >
                      {updateClient.isPending
                        ? "Saving..."
                        : "Save Changes"}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            <CardContent>
              {clientsLoading ? (
                <p className="text-sm text-muted-foreground">
                  Loading clients...
                </p>
              ) : clientsError ? (
                <p className="text-sm text-destructive">
                  Failed to load clients.
                </p>
              ) : !clients || clients.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No clients linked to this vendor.
                </p>
              ) : (
                <div className="space-y-3">
                  {clients.map((client) => (
                    <div
                      key={client.public_id}
                      className="rounded-lg border p-4"
                    >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                        <p className="font-medium">
                        {client.display_name ?? client.name}
                        </p>

                        {client.display_name &&
                        client.display_name !== client.name && (
                            <p className="text-sm text-muted-foreground">
                            {client.name}
                            </p>
                        )}
                    </div>

                    <div className="flex items-center gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={(event) => {
                        event.stopPropagation();
                        handleOpenEditClient(client);
                        }}
                    >
                        Edit
                    </Button>

                    <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={(event) => {
                        event.stopPropagation();
                        handleArchiveClient(client);
                        }}
                        disabled={archiveClient.isPending}
                    >
                        {archiveClient.isPending
                        ? "Archiving..."
                        : "Archive"}
                    </Button>
                    </div>
                    {archiveClient.error && (
                    <p className="mt-2 text-sm text-destructive">
                        Failed to archive client. Please try again.
                    </p>
                    )}
                    </div>

                      <div className="mt-3 space-y-1 text-sm">
                        {client.industry && (
                          <p>{client.industry}</p>
                        )}

                        {client.primary_location && (
                          <p className="text-muted-foreground">
                            {client.primary_location}
                          </p>
                        )}

                        <span className="inline-flex rounded-full border px-2 py-0.5 text-xs">
                          {formatStatus(client.status)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
            </div>
        </>
        )}
    </div>
  );
}