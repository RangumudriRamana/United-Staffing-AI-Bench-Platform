import { useState } from "react";

import type { Requirement } from "@/features/requirements/types";
import requirementService from "@/services/requirement.service";

interface Props {
  requirements: Requirement[];
}

export default function RequirementsTable({
  requirements,
}: Props) {
  const [selectedRequirement, setSelectedRequirement] =
    useState<Requirement | null>(null);

  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const handleView = async (requirement: Requirement) => {
    setError("");
    setLoadingId(requirement.public_id);

    try {
      const response = await requirementService.getById(
        requirement.public_id
      );

      setSelectedRequirement(response);
    } catch (err: any) {
      setError(
        err?.response?.data?.message ||
          err?.response?.data?.detail ||
          "Failed to load requirement details."
      );
    } finally {
      setLoadingId(null);
    }
  };

  const closeDetails = () => {
    setSelectedRequirement(null);
    setError("");
  };

  return (
    <>
      <div className="overflow-hidden rounded-lg border bg-white shadow-sm">
        <table className="w-full">
          <thead className="bg-slate-100">
            <tr>
              <th className="px-4 py-3 text-left">
                Job Title
              </th>

              <th className="px-4 py-3 text-left">
                Location
              </th>

              <th className="px-4 py-3 text-left">
                Employment
              </th>

              <th className="px-4 py-3 text-left">
                Priority
              </th>

              <th className="px-4 py-3 text-left">
                Status
              </th>

              <th className="px-4 py-3 text-left">
                Positions
              </th>

              <th className="px-4 py-3 text-left">
                Actions
              </th>
            </tr>
          </thead>

          <tbody>
            {requirements.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="py-10 text-center text-slate-500"
                >
                  No requirements found.
                </td>
              </tr>
            ) : (
              requirements.map((requirement) => (
                <tr
                  key={requirement.public_id}
                  className="border-t hover:bg-slate-50"
                >
                  <td className="px-4 py-3 font-medium">
                    {requirement.job_title}
                  </td>

                  <td className="px-4 py-3">
                    {requirement.location || "N/A"}
                  </td>

                  <td className="px-4 py-3">
                    {requirement.employment_type}
                  </td>

                  <td className="px-4 py-3">
                    {requirement.priority}
                  </td>

                  <td className="px-4 py-3">
                    {requirement.status}
                  </td>

                  <td className="px-4 py-3">
                    {requirement.positions}
                  </td>

                  <td className="px-4 py-3">
                    <button
                      type="button"
                      className="text-blue-600 hover:underline disabled:opacity-50"
                      disabled={
                        loadingId === requirement.public_id
                      }
                      onClick={() =>
                        handleView(requirement)
                      }
                    >
                      {loadingId === requirement.public_id
                        ? "Loading..."
                        : "View"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {selectedRequirement && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl bg-white shadow-xl">
            <div className="flex items-center justify-between border-b p-5">
              <div>
                <h2 className="text-xl font-semibold">
                  {selectedRequirement.job_title}
                </h2>

                <p className="text-sm text-slate-500">
                  Requirement Details
                </p>
              </div>

              <button
                type="button"
                onClick={closeDetails}
                className="text-2xl text-slate-500 hover:text-black"
              >
                ×
              </button>
            </div>

            <div className="grid grid-cols-1 gap-5 p-6 md:grid-cols-2">
              <Detail
                label="Job Code"
                value={selectedRequirement.job_code}
              />

              <Detail
                label="Location"
                value={selectedRequirement.location}
              />

              <Detail
                label="Employment Type"
                value={
                  selectedRequirement.employment_type
                }
              />

              <Detail
                label="Work Model"
                value={selectedRequirement.work_model}
              />

              <Detail
                label="Priority"
                value={selectedRequirement.priority}
              />

              <Detail
                label="Status"
                value={selectedRequirement.status}
              />

              <Detail
                label="Positions"
                value={selectedRequirement.positions}
              />

              <Detail
                label="Vendor ID"
                value={selectedRequirement.vendor_id}
              />

              <Detail
                label="Client ID"
                value={selectedRequirement.client_id}
              />

              <Detail
                label="Owner Recruiter ID"
                value={
                  selectedRequirement.owner_recruiter_id
                }
              />

              <Detail
                label="Currency"
                value={selectedRequirement.currency}
              />

              <Detail
                label="Rate Range"
                value={formatRate(selectedRequirement)}
              />

              <Detail
                label="Received Date"
                value={selectedRequirement.received_date}
              />

              <Detail
                label="Target Start Date"
                value={
                  selectedRequirement.target_start_date
                }
              />
            </div>

            {selectedRequirement.description && (
              <div className="border-t p-6">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Description
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm text-slate-900">
                  {selectedRequirement.description}
                </p>
              </div>
            )}

            {selectedRequirement.notes && (
              <div className="border-t p-6">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Notes
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm text-slate-900">
                  {selectedRequirement.notes}
                </p>
              </div>
            )}

            <div className="border-t p-6">
              <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-500">
                Technologies
              </p>

              {selectedRequirement.technologies.length === 0 ? (
                <p className="text-sm text-slate-500">
                  No technologies assigned.
                </p>
              ) : (
                <div className="space-y-2">
                  {selectedRequirement.technologies.map(
                    (technology) => (
                      <div
                        key={technology.technology_id}
                        className="rounded-lg border p-3"
                      >
                        <div className="font-medium">
                          Technology ID:{" "}
                          {technology.technology_id}
                        </div>

                        <div className="text-sm text-slate-600">
                          Minimum experience:{" "}
                          {technology.minimum_years} years
                        </div>

                        <div className="text-sm text-slate-600">
                          Mandatory:{" "}
                          {technology.mandatory
                            ? "Yes"
                            : "No"}
                        </div>

                        {technology.notes && (
                          <div className="text-sm text-slate-600">
                            Notes: {technology.notes}
                          </div>
                        )}
                      </div>
                    )
                  )}
                </div>
              )}
            </div>

            <div className="flex justify-end border-t p-5">
              <button
                type="button"
                onClick={closeDetails}
                className="rounded-lg border px-4 py-2 hover:bg-slate-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

interface DetailProps {
  label: string;
  value: string | number | null | undefined;
}

function Detail({ label, value }: DetailProps) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-sm text-slate-900">
        {value ?? "N/A"}
      </p>
    </div>
  );
}

function formatRate(requirement: Requirement) {
  if (
    requirement.rate_min === null &&
    requirement.rate_max === null
  ) {
    return "N/A";
  }

  if (requirement.rate_min !== null && requirement.rate_max !== null) {
    return `${requirement.currency} ${requirement.rate_min} - ${requirement.rate_max}`;
  }

  if (requirement.rate_min !== null) {
    return `${requirement.currency} ${requirement.rate_min}+`;
  }

  return `Up to ${requirement.currency} ${requirement.rate_max}`;
}