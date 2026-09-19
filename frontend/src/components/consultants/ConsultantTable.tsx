import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import StatusBadge from "./StatusBadge";
import EditConsultantDialog from "./EditConsultantDialog";
import consultantService from "@/services/consultant.service";
import type { Consultant } from "@/features/consultants/types";

interface Props {
  consultants: Consultant[];
}

export default function ConsultantTable({ consultants }: Props) {
  const queryClient = useQueryClient();

  const [selectedConsultant, setSelectedConsultant] =
    useState<Consultant | null>(null);

  const [editingConsultant, setEditingConsultant] =
    useState<Consultant | null>(null);

  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const handleView = async (consultant: Consultant) => {
    setError("");
    setLoadingId(consultant.public_id);

    try {
      const response = await consultantService.getById(
        consultant.public_id
      );

      setSelectedConsultant(response.data ?? response);
    } catch (err: any) {
      setError(
        err?.response?.data?.message ||
          err?.response?.data?.detail ||
          "Failed to load consultant details."
      );
    } finally {
      setLoadingId(null);
    }
  };

  const handleEdit = (consultant: Consultant) => {
    setError("");
    setEditingConsultant(consultant);
  };

  const handleArchive = async (consultant: Consultant) => {
    const confirmed = window.confirm(
      `Are you sure you want to archive ${consultant.first_name} ${consultant.last_name}?`
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setLoadingId(consultant.public_id);

    try {
      await consultantService.archive(consultant.public_id);

      await queryClient.invalidateQueries({
        queryKey: ["consultants"],
      });
    } catch (err: any) {
      console.error("ARCHIVE CONSULTANT ERROR:", err);

      setError(
        err?.response?.data?.message ||
          err?.response?.data?.detail ||
          "Failed to archive consultant."
      );
    } finally {
      setLoadingId(null);
    }
  };

  const handleSaved = async () => {
    await queryClient.invalidateQueries({
      queryKey: ["consultants"],
    });
  };

  const closeDetails = () => {
    setSelectedConsultant(null);
    setError("");
  };

  const closeEdit = () => {
    setEditingConsultant(null);
  };

  return (
    <>
      <div className="overflow-hidden rounded-lg border bg-white shadow-sm">
        <table className="w-full">
          <thead className="bg-slate-100">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Email</th>
              <th className="px-4 py-3 text-left">Visa</th>
              <th className="px-4 py-3 text-left">Experience</th>
              <th className="px-4 py-3 text-left">Marketing</th>
              <th className="px-4 py-3 text-left">Actions</th>
            </tr>
          </thead>

          <tbody>
            {consultants.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="py-10 text-center text-slate-500"
                >
                  No consultants found.
                </td>
              </tr>
            ) : (
              consultants.map((consultant) => {
                const isLoading =
                  loadingId === consultant.public_id;

                return (
                  <tr
                    key={consultant.public_id}
                    className="border-t hover:bg-slate-50"
                  >
                    <td className="px-4 py-3 font-medium">
                      {consultant.first_name}{" "}
                      {consultant.last_name}
                    </td>

                    <td className="px-4 py-3">
                      {consultant.email}
                    </td>

                    <td className="px-4 py-3">
                      {consultant.visa_status}
                    </td>

                    <td className="px-4 py-3">
                      {consultant.total_experience_years} Years
                    </td>

                    <td className="px-4 py-3">
                      <StatusBadge
                        status={consultant.marketing_status}
                      />
                    </td>

                    <td className="space-x-3 px-4 py-3">
                      <button
                        type="button"
                        className="text-blue-600 hover:underline disabled:opacity-50"
                        disabled={isLoading}
                        onClick={() => handleView(consultant)}
                      >
                        {isLoading ? "Loading..." : "View"}
                      </button>

                      <button
                        type="button"
                        className="text-green-600 hover:underline disabled:opacity-50"
                        disabled={isLoading}
                        onClick={() => handleEdit(consultant)}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="text-red-600 hover:underline disabled:opacity-50"
                        disabled={isLoading}
                        onClick={() => handleArchive(consultant)}
                      >
                        {isLoading ? "Archiving..." : "Archive"}
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* VIEW DETAILS */}
      {selectedConsultant && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-xl">
            <div className="flex items-center justify-between border-b p-5">
              <div>
                <h2 className="text-xl font-semibold">
                  {selectedConsultant.first_name}{" "}
                  {selectedConsultant.last_name}
                </h2>

                <p className="text-sm text-slate-500">
                  Consultant Details
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
                label="Email"
                value={selectedConsultant.email}
              />

              <Detail
                label="Phone"
                value={selectedConsultant.phone}
              />

              <Detail
                label="Current Title"
                value={selectedConsultant.current_title}
              />

              <Detail
                label="Experience"
                value={`${selectedConsultant.total_experience_years} Years`}
              />

              <Detail
                label="Current Location"
                value={selectedConsultant.current_location}
              />

              <Detail
                label="Preferred Location"
                value={selectedConsultant.preferred_location}
              />

              <Detail
                label="Visa Status"
                value={selectedConsultant.visa_status}
              />

              <Detail
                label="Visa Expiration"
                value={selectedConsultant.visa_expiration}
              />

              <Detail
                label="Remote Preference"
                value={selectedConsultant.remote_preference}
              />

              <Detail
                label="Marketing Status"
                value={selectedConsultant.marketing_status}
              />

              <Detail
                label="Rate Type"
                value={selectedConsultant.rate_type}
              />

              <Detail
                label="Expected Rate"
                value={
                  selectedConsultant.expected_rate !== null &&
                  selectedConsultant.expected_rate !== undefined
                    ? String(selectedConsultant.expected_rate)
                    : "N/A"
                }
              />

              <Detail
                label="Availability Date"
                value={selectedConsultant.availability_date}
              />

              <Detail
                label="Work Authorized"
                value={
                  selectedConsultant.work_authorized
                    ? "Yes"
                    : "No"
                }
              />

              <Detail
                label="Relocation Available"
                value={
                  selectedConsultant.relocation_available
                    ? "Yes"
                    : "No"
                }
              />
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

      {/* EDIT */}
      <EditConsultantDialog
        consultant={editingConsultant}
        open={editingConsultant !== null}
        onClose={closeEdit}
        onSaved={handleSaved}
      />
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
        {value || "N/A"}
      </p>
    </div>
  );
}