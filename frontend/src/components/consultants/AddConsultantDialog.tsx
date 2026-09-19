import { useState } from "react";
import consultantService from "@/services/consultant.service";
import type {
  CreateConsultantRequest,
  VisaStatus,
  RateType,
} from "@/features/consultants/types";

interface Props {
  open: boolean;
  onClose: () => void;
  onCreated?: () => void;
}

const initialForm: CreateConsultantRequest = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  current_title: "",
  total_experience_years: 0,
  current_location: "",
  preferred_location: "",
  relocation_available: false,
  remote_preference: "Hybrid",
  visa_status: "H1B",
  visa_expiration: "",
  work_authorized: true,
  availability_date: "",
  rate_type: "Hourly",
  expected_rate: 0,
};

export default function AddConsultantDialog({
  open,
  onClose,
  onCreated,
}: Props) {
  const [form, setForm] =
    useState<CreateConsultantRequest>(initialForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  if (!open) return null;

  const updateField = <K extends keyof CreateConsultantRequest>(
    field: K,
    value: CreateConsultantRequest[K]
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleClose = () => {
    if (saving) return;
    setForm(initialForm);
    setError("");
    onClose();
  };

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    setError("");

    if (!form.first_name.trim() || !form.last_name.trim()) {
      setError("First name and last name are required.");
      return;
    }

    if (!form.email.trim()) {
      setError("Email is required.");
      return;
    }

    setSaving(true);

    try {
      await consultantService.create({
        ...form,
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone: form.phone?.trim() || null,
        current_title: form.current_title?.trim() || null,
        current_location: form.current_location?.trim() || null,
        preferred_location:
          form.preferred_location?.trim() || null,
        visa_expiration: form.visa_expiration || null,
        availability_date: form.availability_date || null,
        expected_rate:
          form.expected_rate && form.expected_rate > 0
            ? form.expected_rate
            : null,
      });

      setForm(initialForm);
      onClose();
      onCreated?.();
    } catch (err: any) {
      const message =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        "Failed to create consultant.";

      setError(
        Array.isArray(message)
          ? message
              .map((item) => item?.msg || "Invalid value")
              .join(", ")
          : message
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <form
        onSubmit={handleSubmit}
        className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl bg-white shadow-xl"
      >
        <div className="sticky top-0 flex items-center justify-between border-b bg-white p-5">
          <h2 className="text-xl font-semibold">
            Add Consultant
          </h2>

          <button
            type="button"
            onClick={handleClose}
            disabled={saving}
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
              Basic Information
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Field
                label="First Name"
                required
                value={form.first_name}
                onChange={(value) =>
                  updateField("first_name", value)
                }
              />

              <Field
                label="Last Name"
                required
                value={form.last_name}
                onChange={(value) =>
                  updateField("last_name", value)
                }
              />

              <Field
                label="Email"
                required
                type="email"
                value={form.email}
                onChange={(value) =>
                  updateField("email", value)
                }
              />

              <Field
                label="Phone"
                value={form.phone ?? ""}
                onChange={(value) =>
                  updateField("phone", value)
                }
              />
            </div>
          </section>

          <section>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Professional Information
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Field
                label="Current Title"
                value={form.current_title ?? ""}
                onChange={(value) =>
                  updateField("current_title", value)
                }
              />

              <Field
                label="Total Experience (Years)"
                type="number"
                min="0"
                value={String(form.total_experience_years ?? 0)}
                onChange={(value) =>
                  updateField(
                    "total_experience_years",
                    Number(value) || 0
                  )
                }
              />

              <Field
                label="Current Location"
                value={form.current_location ?? ""}
                onChange={(value) =>
                  updateField("current_location", value)
                }
              />

              <Field
                label="Preferred Location"
                value={form.preferred_location ?? ""}
                onChange={(value) =>
                  updateField("preferred_location", value)
                }
              />
            </div>
          </section>

          <section>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Work Preferences
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <SelectField
                label="Remote Preference"
                value={form.remote_preference ?? "Hybrid"}
                onChange={(value) =>
                  updateField("remote_preference", value)
                }
                options={["Remote", "Hybrid", "Onsite"]}
              />

              <SelectField
                label="Visa Status"
                value={form.visa_status}
                onChange={(value) =>
                  updateField(
                    "visa_status",
                    value as VisaStatus
                  )
                }
                options={[
                  "H1B",
                  "H4 EAD",
                  "GC",
                  "USC",
                  "OPT",
                  "STEM OPT",
                  "CPT",
                  "L2 EAD",
                  "TN",
                  "E3",
                  "Other",
                ]}
              />

              <Field
                label="Visa Expiration"
                type="date"
                value={form.visa_expiration ?? ""}
                onChange={(value) =>
                  updateField("visa_expiration", value)
                }
              />

              <Field
                label="Availability Date"
                type="date"
                value={form.availability_date ?? ""}
                onChange={(value) =>
                  updateField("availability_date", value)
                }
              />

              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.relocation_available ?? false}
                  onChange={(event) =>
                    updateField(
                      "relocation_available",
                      event.target.checked
                    )
                  }
                />
                Relocation Available
              </label>

              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.work_authorized ?? true}
                  onChange={(event) =>
                    updateField(
                      "work_authorized",
                      event.target.checked
                    )
                  }
                />
                Work Authorized
              </label>
            </div>
          </section>

          <section>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Rate Information
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <SelectField
                label="Rate Type"
                value={form.rate_type ?? "Hourly"}
                onChange={(value) =>
                  updateField(
                    "rate_type",
                    value as RateType
                  )
                }
                options={[
                  "Hourly",
                  "Daily",
                  "Monthly",
                  "Annual",
                ]}
              />

              <Field
                label="Expected Rate"
                type="number"
                min="0"
                value={String(form.expected_rate ?? 0)}
                onChange={(value) =>
                  updateField(
                    "expected_rate",
                    Number(value) || 0
                  )
                }
              />
            </div>
          </section>
        </div>

        <div className="sticky bottom-0 flex justify-end gap-3 border-t bg-white p-5">
          <button
            type="button"
            onClick={handleClose}
            disabled={saving}
            className="rounded-lg border px-4 py-2 disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Consultant"}
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
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false,
  min,
}: FieldProps) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}
        {required && (
          <span className="ml-1 text-red-500">*</span>
        )}
      </label>

      <input
        type={type}
        required={required}
        min={min}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
      />
    </div>
  );
}

interface SelectFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: SelectFieldProps) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}
      </label>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}