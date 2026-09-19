import { useMemo, useState } from "react";

import type { Vendor, VendorContact, Client } from "@/features/vendors/types";
import { useVendors } from "@/hooks/useVendors";
import {
  useCreateMarketingActivity,
  type CreateMarketingActivityPayload,
} from "@/hooks/useCreateMarketingActivity";

interface Props {
  open: boolean;
  consultantPublicId: string | null;
  consultantName: string;
  onClose: () => void;
  onCreated?: () => void;
}

const initialForm = {
  vendorPublicId: "",
  vendorContactPublicId: "",
  clientPublicId: "",
  activityType: "PROFILE_MARKETING",
  channel: "EMAIL",
  outcome: "SENT",
  subject: "",
  notes: "",
  followUpRequired: false,
};

export default function RecordMarketingActivityDialog({
  open,
  consultantPublicId,
  consultantName,
  onClose,
  onCreated,
}: Props) {
  const { data: vendorsData, isLoading: isVendorsLoading } = useVendors();
  const createActivity = useCreateMarketingActivity();

  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");

  if (!open || !consultantPublicId) {
    return null;
  }

  const vendors: Vendor[] = vendorsData?.data ?? [];

  const selectedVendor = useMemo(
    () =>
      vendors.find(
        (vendor) => vendor.public_id === form.vendorPublicId
      ),
    [vendors, form.vendorPublicId]
  );

  const contacts: VendorContact[] =
    selectedVendor?.contacts?.filter((contact) => contact.is_active) ?? [];

  const clients: Client[] = selectedVendor?.clients ?? [];

  const updateField = (
    field: keyof typeof initialForm,
    value: string | boolean
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleVendorChange = (vendorPublicId: string) => {
    setForm((current) => ({
      ...current,
      vendorPublicId,
      vendorContactPublicId: "",
      clientPublicId: "",
    }));
  };

  const handleClose = () => {
    if (createActivity.isPending) {
      return;
    }

    setForm(initialForm);
    setError("");
    onClose();
  };

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    setError("");

    if (!form.vendorPublicId) {
      setError("Vendor is required.");
      return;
    }

    if (!form.vendorContactPublicId && !form.clientPublicId) {
      setError("Select a vendor contact or client.");
      return;
    }

    if (!consultantPublicId) {
      setError("Consultant is required.");
      return;
    }

    const payload: CreateMarketingActivityPayload = {
      consultant_public_id: consultantPublicId,
      vendor_public_id: form.vendorPublicId,
      vendor_contact_public_id:
        form.vendorContactPublicId || null,
      client_public_id:
        form.clientPublicId || null,
      activity_type: form.activityType,
      channel: form.channel,
      outcome: form.outcome,
      subject: form.subject.trim() || null,
      notes: form.notes.trim() || null,
      follow_up_required: form.followUpRequired,
    };

    try {
      await createActivity.mutateAsync(payload);

      setForm(initialForm);
      onCreated?.();
      onClose();
    } catch (err: any) {
      const message =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        "Failed to record marketing activity.";

      setError(
        Array.isArray(message)
          ? message
              .map((item) => item?.msg || "Invalid value")
              .join(", ")
          : message
      );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <form
        onSubmit={handleSubmit}
        className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-xl"
      >
        <div className="sticky top-0 flex items-center justify-between border-b bg-white p-5">
          <div>
            <h2 className="text-xl font-semibold">
              Record Marketing Activity
            </h2>

            <p className="mt-1 text-sm text-muted-foreground">
              Consultant: {consultantName}
            </p>
          </div>

          <button
            type="button"
            onClick={handleClose}
            disabled={createActivity.isPending}
            className="text-2xl leading-none text-slate-500 hover:text-black disabled:opacity-50"
          >
            ×
          </button>
        </div>

        <div className="space-y-6 p-6">
          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <section>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Outreach Target
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <SelectField
                label="Vendor"
                required
                value={form.vendorPublicId}
                disabled={isVendorsLoading}
                onChange={handleVendorChange}
                options={[
                  {
                    value: "",
                    label: isVendorsLoading
                      ? "Loading vendors..."
                      : "Select vendor",
                  },
                  ...vendors.map((vendor) => ({
                    value: vendor.public_id,
                    label: vendor.name,
                  })),
                ]}
              />

              <SelectField
                label="Vendor Contact"
                value={form.vendorContactPublicId}
                onChange={(value) =>
                  updateField("vendorContactPublicId", value)
                }
                options={[
                  {
                    value: "",
                    label:
                      contacts.length > 0
                        ? "Select contact"
                        : "No contacts available",
                  },
                  ...contacts.map((contact) => ({
                    value: contact.public_id,
                    label: `${contact.name} — ${contact.email}`,
                  })),
                ]}
              />

              <SelectField
                label="Client"
                value={form.clientPublicId}
                onChange={(value) =>
                  updateField("clientPublicId", value)
                }
                options={[
                  {
                    value: "",
                    label:
                      clients.length > 0
                        ? "Select client"
                        : "No clients available",
                  },
                  ...clients.map((client) => ({
                    value: client.public_id,
                    label: client.display_name || client.name,
                  })),
                ]}
              />
            </div>
          </section>

          <section>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Activity Details
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <SelectField
                label="Activity Type"
                required
                value={form.activityType}
                onChange={(value) =>
                  updateField("activityType", value)
                }
                options={[
                  {
                    value: "PROFILE_MARKETING",
                    label: "Profile Marketing",
                  },
                  {
                    value: "PROFILE_FOLLOW_UP",
                    label: "Profile Follow-Up",
                  },
                  {
                    value: "REQUIREMENT_OUTREACH",
                    label: "Requirement Outreach",
                  },
                  {
                    value: "VENDOR_OUTREACH",
                    label: "Vendor Outreach",
                  },
                  {
                    value: "CLIENT_OUTREACH",
                    label: "Client Outreach",
                  },
                  {
                    value: "MARKETING_REFRESH",
                    label: "Marketing Refresh",
                  },
                ]}
              />

              <SelectField
                label="Channel"
                required
                value={form.channel}
                onChange={(value) =>
                  updateField("channel", value)
                }
                options={[
                  { value: "EMAIL", label: "Email" },
                  { value: "PHONE_CALL", label: "Phone Call" },
                  { value: "LINKEDIN", label: "LinkedIn" },
                  { value: "PORTAL", label: "Portal" },
                  { value: "SMS", label: "SMS" },
                  { value: "OTHER", label: "Other" },
                ]}
              />

              <SelectField
                label="Outcome"
                required
                value={form.outcome}
                onChange={(value) =>
                  updateField("outcome", value)
                }
                options={[
                  { value: "SENT", label: "Sent" },
                  { value: "DELIVERED", label: "Delivered" },
                  { value: "RESPONDED", label: "Responded" },
                  { value: "INTERESTED", label: "Interested" },
                  { value: "NO_RESPONSE", label: "No Response" },
                  {
                    value: "NOT_INTERESTED",
                    label: "Not Interested",
                  },
                  {
                    value: "REQUIREMENT_RECEIVED",
                    label: "Requirement Received",
                  },
                  {
                    value: "FOLLOW_UP_REQUIRED",
                    label: "Follow-Up Required",
                  },
                  { value: "FAILED", label: "Failed" },
                ]}
              />

              <Field
                label="Subject"
                value={form.subject}
                onChange={(value) =>
                  updateField("subject", value)
                }
              />
            </div>

            <div className="mt-4">
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Notes
              </label>

              <textarea
                value={form.notes}
                onChange={(event) =>
                  updateField("notes", event.target.value)
                }
                rows={4}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
                placeholder="Add outreach details, response, or follow-up notes..."
              />
            </div>

            <label className="mt-4 flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={form.followUpRequired}
                onChange={(event) =>
                  updateField(
                    "followUpRequired",
                    event.target.checked
                  )
                }
              />
              Follow-up required
            </label>
          </section>
        </div>

        <div className="sticky bottom-0 flex justify-end gap-3 border-t bg-white p-5">
          <button
            type="button"
            onClick={handleClose}
            disabled={createActivity.isPending}
            className="rounded-lg border px-4 py-2 disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={createActivity.isPending || isVendorsLoading}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {createActivity.isPending
              ? "Recording..."
              : "Record Activity"}
          </button>
        </div>
      </form>
    </div>
  );
}

interface FieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function Field({
  label,
  value,
  onChange,
}: FieldProps) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}
      </label>

      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
      />
    </div>
  );
}

interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  required?: boolean;
  disabled?: boolean;
}

function SelectField({
  label,
  value,
  onChange,
  options,
  required = false,
  disabled = false,
}: SelectFieldProps) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}
        {required && (
          <span className="ml-1 text-red-500">*</span>
        )}
      </label>

      <select
        required={required}
        disabled={disabled}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500 disabled:bg-slate-100"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}