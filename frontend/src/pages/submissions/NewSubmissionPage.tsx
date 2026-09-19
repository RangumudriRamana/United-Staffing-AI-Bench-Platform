import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useConsultants } from "@/hooks/useConsultants";
import { useVendors } from "@/hooks/useVendors";
import { useClients } from "@/hooks/useClients";
import { useCreateSubmission } from "@/hooks/useSubmissionMutations";

import type { Consultant } from "@/features/consultants/types";
import type {
  Client,
  Vendor,
} from "@/features/vendors/types";
import type {
  CreateSubmissionRequest,
  EmploymentType,
} from "@/features/submissions/types";

const initialForm = {
  consultant_public_id: "",
  vendor_public_id: "",
  vendor_contact_public_id: "",
  client_public_id: "",
  job_title: "",
  job_id: "",
  job_location: "",
  employment_type: "C2C" as EmploymentType,
  rate: "",
  currency: "USD",
  expected_start_date: "",
  submission_notes: "",
};

export default function NewSubmissionPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");

  const {
    data: consultantsData,
    isLoading: consultantsLoading,
  } = useConsultants();

  const {
    data: vendorsData,
    isLoading: vendorsLoading,
  } = useVendors();

  const {
    data: clients,
    isLoading: clientsLoading,
  } = useClients(form.vendor_public_id || undefined);

  const createSubmission = useCreateSubmission();

  const consultants: Consultant[] =
    consultantsData?.data ?? [];

  const vendors: Vendor[] =
    vendorsData?.data ?? [];

  const selectedVendor = useMemo(
    () =>
      vendors.find(
        (vendor) =>
          vendor.public_id === form.vendor_public_id
      ),
    [vendors, form.vendor_public_id]
  );

  const contacts =
    selectedVendor?.contacts?.filter(
      (contact) => contact.is_active
    ) ?? [];

  useEffect(() => {
    if (!form.vendor_public_id) {
      setForm((current) => ({
        ...current,
        client_public_id: "",
        vendor_contact_public_id: "",
      }));
      return;
    }

    setForm((current) => ({
      ...current,
      client_public_id: "",
      vendor_contact_public_id: "",
    }));
  }, [form.vendor_public_id]);

  const updateField = (
    field: keyof typeof initialForm,
    value: string
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleVendorChange = (value: string) => {
    setForm((current) => ({
      ...current,
      vendor_public_id: value,
      client_public_id: "",
      vendor_contact_public_id: "",
    }));

    setError("");
  };

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    setError("");

    if (!form.consultant_public_id) {
      setError("Consultant is required.");
      return;
    }

    if (!form.vendor_public_id) {
      setError("Vendor is required.");
      return;
    }

    if (!form.client_public_id) {
      setError("Client is required.");
      return;
    }

    if (!form.job_title.trim()) {
      setError("Job title is required.");
      return;
    }

    const rate = Number(form.rate);

    if (!form.rate || Number.isNaN(rate) || rate <= 0) {
      setError("Rate must be greater than 0.");
      return;
    }

    const selectedConsultant = consultants.find(
      (consultant) =>
        consultant.public_id ===
        form.consultant_public_id
    );

    const selectedClient = clients?.find(
      (client: Client) =>
        client.public_id === form.client_public_id
    );

    if (!selectedConsultant) {
      setError("Selected consultant could not be found.");
      return;
    }

    if (!selectedVendor) {
      setError("Selected vendor could not be found.");
      return;
    }

    if (!selectedClient) {
      setError("Selected client could not be found.");
      return;
    }

    const payload: CreateSubmissionRequest = {
      consultant_public_id:
        form.consultant_public_id,

      vendor_public_id:
        form.vendor_public_id,

      vendor_contact_public_id:
        form.vendor_contact_public_id || null,

      client_public_id:
        form.client_public_id,

      requirement_public_id: null,

      client_name_snapshot:
        selectedClient.display_name ||
        selectedClient.name,

      vendor_name_snapshot:
        selectedVendor.name,

      job_title_snapshot:
        form.job_title.trim(),

      job_id:
        form.job_id.trim() || null,

      job_title:
        form.job_title.trim(),

      job_location:
        form.job_location.trim() || null,

      employment_type:
        form.employment_type,

      rate,

      currency:
        form.currency.trim() || "USD",

      expected_start_date:
        form.expected_start_date || null,

      submission_notes:
        form.submission_notes.trim() || null,
    };

    try {
      const submission =
        await createSubmission.mutateAsync(
          payload
        );

      navigate(
        `/submissions/${submission.public_id}`
      );
    } catch (err: any) {
      const message =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to create submission.";

      setError(
        Array.isArray(message)
          ? message
              .map(
                (item) =>
                  item?.msg || "Invalid value"
              )
              .join(", ")
          : message
      );
    }
  };

  const loading =
    consultantsLoading || vendorsLoading;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          New Submission
        </h1>

        <p className="text-muted-foreground">
          Create a new consultant submission.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-xl border bg-white shadow-sm"
      >
        <div className="space-y-8 p-6">
          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {loading && (
            <div className="rounded-lg border bg-slate-50 px-4 py-3 text-sm text-slate-600">
              Loading submission data...
            </div>
          )}

          {/* Consultant */}
          <section>
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Consultant
            </h2>

            <SelectField
              label="Consultant"
              required
              value={form.consultant_public_id}
              onChange={(value) =>
                updateField(
                  "consultant_public_id",
                  value
                )
              }
              disabled={consultantsLoading}
              placeholder={
                consultantsLoading
                  ? "Loading consultants..."
                  : "Select consultant"
              }
              options={consultants.map(
                (consultant) => ({
                  value: consultant.public_id,
                  label: `${consultant.first_name} ${consultant.last_name} — ${consultant.email}`,
                })
              )}
            />
          </section>

          {/* Vendor / Client / Contact */}
          <section>
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Vendor & Client
            </h2>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <SelectField
                label="Vendor"
                required
                value={form.vendor_public_id}
                onChange={handleVendorChange}
                disabled={vendorsLoading}
                placeholder={
                  vendorsLoading
                    ? "Loading vendors..."
                    : "Select vendor"
                }
                options={vendors.map(
                  (vendor) => ({
                    value: vendor.public_id,
                    label: vendor.name,
                  })
                )}
              />

              <SelectField
                label="Client"
                required
                value={form.client_public_id}
                onChange={(value) =>
                  updateField(
                    "client_public_id",
                    value
                  )
                }
                disabled={
                  !form.vendor_public_id ||
                  clientsLoading
                }
                placeholder={
                  !form.vendor_public_id
                    ? "Select vendor first"
                    : clientsLoading
                      ? "Loading clients..."
                      : "Select client"
                }
                options={(clients ?? []).map(
                  (client: Client) => ({
                    value: client.public_id,
                    label:
                      client.display_name ||
                      client.name,
                  })
                )}
              />

              <SelectField
                label="Vendor Contact"
                value={
                  form.vendor_contact_public_id
                }
                onChange={(value) =>
                  updateField(
                    "vendor_contact_public_id",
                    value
                  )
                }
                disabled={
                  !form.vendor_public_id ||
                  contacts.length === 0
                }
                placeholder={
                  !form.vendor_public_id
                    ? "Select vendor first"
                    : contacts.length === 0
                      ? "No active contacts"
                      : "Select contact"
                }
                options={contacts.map(
                  (contact) => ({
                    value: contact.public_id,
                    label: `${contact.name} — ${contact.email}`,
                  })
                )}
              />
            </div>
          </section>

          {/* Job */}
          <section>
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Job Information
            </h2>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Field
                label="Job Title"
                required
                value={form.job_title}
                onChange={(value) =>
                  updateField(
                    "job_title",
                    value
                  )
                }
              />

              <Field
                label="Job ID"
                value={form.job_id}
                onChange={(value) =>
                  updateField(
                    "job_id",
                    value
                  )
                }
              />

              <Field
                label="Job Location"
                value={form.job_location}
                onChange={(value) =>
                  updateField(
                    "job_location",
                    value
                  )
                }
              />

              <SelectField
                label="Employment Type"
                required
                value={form.employment_type}
                onChange={(value) =>
                  updateField(
                    "employment_type",
                    value
                  )
                }
                options={[
                  {
                    value: "C2C",
                    label: "C2C",
                  },
                  {
                    value: "W2",
                    label: "W2",
                  },
                  {
                    value: "1099",
                    label: "1099",
                  },
                  {
                    value: "FULL_TIME",
                    label: "Full Time",
                  },
                ]}
              />
            </div>
          </section>

          {/* Rate */}
          <section>
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Rate & Start Date
            </h2>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <Field
                label="Rate"
                required
                type="number"
                min="0"
                step="0.01"
                value={form.rate}
                onChange={(value) =>
                  updateField(
                    "rate",
                    value
                  )
                }
              />

              <Field
                label="Currency"
                value={form.currency}
                onChange={(value) =>
                  updateField(
                    "currency",
                    value
                  )
                }
              />

              <Field
                label="Expected Start Date"
                type="date"
                value={
                  form.expected_start_date
                }
                onChange={(value) =>
                  updateField(
                    "expected_start_date",
                    value
                  )
                }
              />
            </div>
          </section>

          {/* Notes */}
          <section>
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Notes
            </h2>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Submission Notes
              </label>

              <textarea
                value={form.submission_notes}
                onChange={(event) =>
                  updateField(
                    "submission_notes",
                    event.target.value
                  )
                }
                rows={4}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
              />
            </div>
          </section>
        </div>

        <div className="flex justify-end gap-3 border-t bg-slate-50 p-5">
          <button
            type="button"
            onClick={() =>
              navigate("/submissions")
            }
            disabled={
              createSubmission.isPending
            }
            className="rounded-lg border bg-white px-4 py-2 disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={
              createSubmission.isPending ||
              consultantsLoading ||
              vendorsLoading
            }
            className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {createSubmission.isPending
              ? "Creating..."
              : "Create Submission"}
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
  type?: string;
  required?: boolean;
  min?: string;
  step?: string;
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false,
  min,
  step,
}: FieldProps) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}

        {required && (
          <span className="ml-1 text-red-500">
            *
          </span>
        )}
      </label>

      <input
        type={type}
        required={required}
        min={min}
        step={step}
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
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
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
}

function SelectField({
  label,
  value,
  onChange,
  options,
  placeholder = "Select",
  required = false,
  disabled = false,
}: SelectFieldProps) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}

        {required && (
          <span className="ml-1 text-red-500">
            *
          </span>
        )}
      </label>

      <select
        required={required}
        value={value}
        disabled={disabled}
        onChange={(event) =>
          onChange(event.target.value)
        }
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-500 disabled:cursor-not-allowed disabled:bg-slate-100"
      >
        <option value="">
          {placeholder}
        </option>

        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
          >
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}