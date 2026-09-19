import { useEffect, useState } from "react";
import consultantService from "@/services/consultant.service";
import type {
  Consultant,
  VisaStatus,
  RateType,
} from "@/features/consultants/types";

interface Props {
  consultant: Consultant | null;
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export default function EditConsultantDialog({
  consultant,
  open,
  onClose,
  onSaved,
}: Props) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [currentTitle, setCurrentTitle] = useState("");
  const [experience, setExperience] = useState("0");
  const [currentLocation, setCurrentLocation] = useState("");
  const [preferredLocation, setPreferredLocation] = useState("");
  const [relocationAvailable, setRelocationAvailable] = useState(false);
  const [remotePreference, setRemotePreference] = useState("Hybrid");
  const [visaStatus, setVisaStatus] =
  useState<VisaStatus>("H1B");
  const [visaExpiration, setVisaExpiration] = useState("");
  const [workAuthorized, setWorkAuthorized] = useState(true);
  const [rateType, setRateType] =
  useState<RateType>("Hourly");
  const [expectedRate, setExpectedRate] = useState("");

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!consultant) return;

    setFirstName(consultant.first_name ?? "");
    setLastName(consultant.last_name ?? "");
    setEmail(consultant.email ?? "");
    setPhone(consultant.phone ?? "");
    setCurrentTitle(consultant.current_title ?? "");
    setExperience(String(consultant.total_experience_years ?? 0));
    setCurrentLocation(consultant.current_location ?? "");
    setPreferredLocation(consultant.preferred_location ?? "");
    setRelocationAvailable(consultant.relocation_available ?? false);
    setRemotePreference(consultant.remote_preference ?? "Hybrid");
    setVisaStatus(consultant.visa_status ?? "H1B");
    setVisaExpiration(consultant.visa_expiration ?? "");
    setWorkAuthorized(consultant.work_authorized ?? true);
    setRateType(consultant.rate_type ?? "Hourly");
    setExpectedRate(
      consultant.expected_rate !== null &&
        consultant.expected_rate !== undefined
        ? String(consultant.expected_rate)
        : ""
    );

    setError("");
  }, [consultant]);

  if (!open || !consultant) {
    return null;
  }

  const handleSave = async () => {
    setSaving(true);
    setError("");

    try {
      await consultantService.update(consultant.public_id, {
        first_name: firstName,
        last_name: lastName,
        email,
        phone: phone || null,
        current_title: currentTitle || null,
        total_experience_years: Number(experience),
        current_location: currentLocation || null,
        preferred_location: preferredLocation || null,
        relocation_available: relocationAvailable,
        remote_preference: remotePreference,
        visa_status: visaStatus,
        visa_expiration: visaExpiration || null,
        work_authorized: workAuthorized,
        rate_type: rateType,
        expected_rate: expectedRate
          ? Number(expectedRate)
          : null,
      });

      onSaved();
      onClose();
    } catch (err: any) {
      console.error("UPDATE CONSULTANT ERROR:", err);

      setError(
        err?.response?.data?.message ||
          "Failed to update consultant."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-xl font-semibold">
              Edit Consultant
            </h2>

            <p className="text-sm text-slate-500">
              Update consultant profile
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-2xl text-slate-500 hover:text-slate-800"
          >
            ×
          </button>
        </div>

        <div className="grid grid-cols-1 gap-5 p-6 md:grid-cols-2">
          <Field
            label="First Name"
            value={firstName}
            onChange={setFirstName}
          />

          <Field
            label="Last Name"
            value={lastName}
            onChange={setLastName}
          />

          <Field
            label="Email"
            value={email}
            onChange={setEmail}
            type="email"
          />

          <Field
            label="Phone"
            value={phone}
            onChange={setPhone}
          />

          <Field
            label="Current Title"
            value={currentTitle}
            onChange={setCurrentTitle}
          />

          <Field
            label="Experience (Years)"
            value={experience}
            onChange={setExperience}
            type="number"
          />

          <Field
            label="Current Location"
            value={currentLocation}
            onChange={setCurrentLocation}
          />

          <Field
            label="Preferred Location"
            value={preferredLocation}
            onChange={setPreferredLocation}
          />

          <SelectField
            label="Visa Status"
            value={visaStatus}
            onChange={(value) =>
              setVisaStatus(value as VisaStatus)
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
            value={visaExpiration}
            onChange={setVisaExpiration}
            type="date"
          />

          <SelectField
            label="Remote Preference"
            value={remotePreference}
            onChange={setRemotePreference}
            options={[
              "Remote",
              "Hybrid",
              "Onsite",
            ]}
          />

          <SelectField
            label="Rate Type"
            value={rateType}
            onChange={(value) =>
              setRateType(value as RateType)
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
            value={expectedRate}
            onChange={setExpectedRate}
            type="number"
          />

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={relocationAvailable}
              onChange={(e) =>
                setRelocationAvailable(e.target.checked)
              }
            />

            <span className="text-sm">
              Relocation Available
            </span>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={workAuthorized}
              onChange={(e) =>
                setWorkAuthorized(e.target.checked)
              }
            />

            <span className="text-sm">
              Work Authorized
            </span>
          </label>
        </div>

        {error && (
          <div className="mx-6 mb-4 rounded-md bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 border-t px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="rounded-md border px-4 py-2 hover:bg-slate-50"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="rounded-md bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}
      </label>

      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border px-3 py-2 outline-none focus:border-blue-500"
      />
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label}
      </label>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border px-3 py-2 outline-none focus:border-blue-500"
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