import { useMemo, useState } from "react";
import {
  CheckCircle2,
  Clock3,
  Megaphone,
  Search,
  Users,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useConsultants } from "@/hooks/useConsultants";
import { useMarketingTransition } from "@/hooks/useMarketingTransition";
import { useMarketingHistory } from "@/hooks/useMarketingHistory";
import { useMarketingActivities } from "@/hooks/useMarketingActivities";
import type { MarketingHistoryRecord } from "@/hooks/useMarketingHistory";

import RecordMarketingActivityDialog from "@/components/marketing/RecordMarketingActivityDialog";


export default function MarketingWorkspacePage() {
  const { data, isLoading, error } = useConsultants();
  const marketingTransition = useMarketingTransition();

  const [search, setSearch] = useState("");
  const [actionError, setActionError] = useState("");
  const [actionId, setActionId] = useState<string | null>(null);
  const [selectedConsultantId, setSelectedConsultantId] = useState<string | null>(
  null
  );
  const [activityConsultantId, setActivityConsultantId] = useState<string | null>(
  null
  );
  const [activityHistoryConsultantId, setActivityHistoryConsultantId] =
    useState<string | null>(null);

    const consultants = data?.data ?? [];

    const {
    data: marketingHistory = [],
    isLoading: isHistoryLoading,
    error: historyError,
  } = useMarketingHistory(selectedConsultantId);
  const {
  data: marketingActivities = [],
  isLoading: isActivitiesLoading,
  error: activitiesError,
} = useMarketingActivities(activityHistoryConsultantId);


  const activityConsultant = consultants.find(
  (consultant: any) =>
    consultant.public_id === activityConsultantId
  );
  const activityHistoryConsultant = consultants.find(
  (consultant: any) =>
    consultant.public_id === activityHistoryConsultantId
  );

  const handleMarketingAction = async (consultant: any) => {
    const isPreparing =
      consultant.marketing_status === "NEW";

    const targetStatus = isPreparing
      ? "READY_FOR_MARKETING"
      : "MARKETING_ACTIVE";

    const actionLabel = isPreparing
      ? "prepare"
      : "start marketing";

    const confirmed = window.confirm(
      `${actionLabel.charAt(0).toUpperCase()}${actionLabel.slice(1)} ${consultant.first_name} ${consultant.last_name}?`
    );

    if (!confirmed) {
      return;
    }

    setActionError("");
    setActionId(consultant.public_id);

    try {
      await marketingTransition.mutateAsync({
        publicId: consultant.public_id,
        payload: {
          target_status: targetStatus,
          reason: isPreparing
            ? "Profile prepared for marketing"
            : "Marketing campaign started",
          notes: isPreparing
            ? "Consultant moved from NEW to READY_FOR_MARKETING."
            : "Consultant moved from READY_FOR_MARKETING to MARKETING_ACTIVE.",
        },
      });
    } catch (err: any) {
      setActionError(
        err?.response?.data?.message ||
          err?.response?.data?.detail ||
          "Failed to update consultant marketing status."
      );
    } finally {
      setActionId(null);
    }
  };

  const marketingQueue = useMemo(() => {
    const normalizedSearch = search.toLowerCase().trim();

    const marketingQueueStatuses = [
      "NEW",
      "READY_FOR_MARKETING",
    ];

    return consultants.filter((consultant: any) => {
      const fullName =
        `${consultant.first_name} ${consultant.last_name}`.toLowerCase();

      const matchesStatus = marketingQueueStatuses.includes(
        consultant.marketing_status
      );

      const matchesSearch =
        !normalizedSearch ||
        fullName.includes(normalizedSearch) ||
        consultant.email?.toLowerCase().includes(normalizedSearch) ||
        consultant.current_title?.toLowerCase().includes(normalizedSearch);

      return matchesStatus && matchesSearch;
    });
  }, [consultants, search]);

    const activeMarketingConsultants = useMemo(() => {
    const normalizedSearch = search.toLowerCase().trim();

    return consultants.filter((consultant: any) => {
      const fullName =
        `${consultant.first_name} ${consultant.last_name}`.toLowerCase();

      const matchesStatus =
        consultant.marketing_status === "MARKETING_ACTIVE";

      const matchesSearch =
        !normalizedSearch ||
        fullName.includes(normalizedSearch) ||
        consultant.email?.toLowerCase().includes(normalizedSearch) ||
        consultant.current_title?.toLowerCase().includes(normalizedSearch);

      return matchesStatus && matchesSearch;
    });
  }, [consultants, search]);

  const availableCount = consultants.filter(
    (consultant: any) =>
      consultant.marketing_status === "NEW" ||
      consultant.marketing_status === "READY_FOR_MARKETING" ||
      consultant.marketing_status === "MARKETING_ACTIVE"
  ).length;

  const marketedCount = consultants.filter(
    (consultant: any) =>
      consultant.marketing_status === "MARKETING_ACTIVE"
  ).length;

  const activeMarketingCount = consultants.filter(
    (consultant: any) =>
      consultant.marketing_status === "MARKETING_ACTIVE"
  ).length;

  const formatHistoryDate = (value: string) =>
    new Date(value).toLocaleString();

  const formatHistoryStatus = (status: string) =>
    status.replaceAll("_", " ");

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Marketing Workspace</h1>
          <p className="text-muted-foreground">
            Identify consultants who need to be marketed.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="h-20 animate-pulse rounded bg-slate-100" />
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardContent className="p-6">
            <div className="h-48 animate-pulse rounded bg-slate-100" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Marketing Workspace</h1>
          <p className="text-muted-foreground">
            Identify consultants who need to be marketed.
          </p>
        </div>

        <Card>
          <CardContent className="p-6 text-red-600">
            Failed to load consultants for the marketing workspace.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div>
        <h1 className="text-3xl font-bold">Marketing Workspace</h1>

        <p className="text-muted-foreground">
          Identify consultants who need to be marketed and prioritize today's
          outreach.
        </p>
      </div>

      {/* SUMMARY */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Available Consultants
            </CardTitle>

            <Users className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">{availableCount}</div>

            <p className="mt-1 text-xs text-muted-foreground">
              Available for marketing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Marketing Queue
            </CardTitle>

            <Megaphone className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {marketingQueue.length}
            </div>

            <p className="mt-1 text-xs text-muted-foreground">
              Consultants requiring attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Active Marketing
            </CardTitle>

            <Clock3 className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {activeMarketingCount}
            </div>

            <p className="mt-1 text-xs text-muted-foreground">
              Consultants with marketing activity
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Marketed
            </CardTitle>

            <CheckCircle2 className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">{marketedCount}</div>

            <p className="mt-1 text-xs text-muted-foreground">
              Currently marked as marketed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* SEARCH */}
      <Card>
        <CardContent className="p-4">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

            <input
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search consultant, email, or title..."
              className="w-full rounded-md border bg-white py-2 pl-9 pr-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus:ring-2 focus:ring-ring"
            />
          </div>
        </CardContent>
      </Card>

      {/* MARKETING QUEUE */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Marketing Queue</CardTitle>

          <p className="text-sm text-muted-foreground">
            Consultants currently visible from the consultant management
            module.
          </p>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-100">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Consultant
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Title
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Visa
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Rate
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Availability
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Marketing Status
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody>
                {marketingQueue.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="py-12 text-center text-sm text-muted-foreground"
                    >
                      No consultants found in the marketing queue.
                    </td>
                  </tr>
                ) : (
                  marketingQueue.map((consultant: any) => (
                    <tr
                      key={consultant.public_id}
                      className="border-t hover:bg-slate-50"
                    >
                      <td className="px-4 py-3">
                        <div className="font-medium">
                          {consultant.first_name}{" "}
                          {consultant.last_name}
                        </div>

                        <div className="text-xs text-muted-foreground">
                          {consultant.email}
                        </div>
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.current_title || "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.visa_status || "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.expected_rate !== null &&
                        consultant.expected_rate !== undefined
                          ? `${consultant.rate_type || ""} ${consultant.expected_rate}`
                          : "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.availability_date || "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.marketing_status || "N/A"}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center gap-2">
                          {consultant.marketing_status === "NEW" ? (
                            <button
                              type="button"
                              className="rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                              disabled={actionId === consultant.public_id}
                              onClick={() => handleMarketingAction(consultant)}
                            >
                              {actionId === consultant.public_id
                                ? "Preparing..."
                                : "Prepare"}
                            </button>
                          ) : consultant.marketing_status === "READY_FOR_MARKETING" ? (
                            <button
                              type="button"
                              className="rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                              disabled={actionId === consultant.public_id}
                              onClick={() => handleMarketingAction(consultant)}
                            >
                              {actionId === consultant.public_id
                                ? "Starting..."
                                : "Start Marketing"}
                            </button>
                          ) : (
                            <span className="text-muted-foreground">
                              No action
                            </span>
                          )}

                          <button
                            type="button"
                            className="rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-slate-50"
                            onClick={() => setSelectedConsultantId(consultant.public_id)}
                          >
                            History
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

            <Card>
        <CardHeader>
          <CardTitle>Active Marketing</CardTitle>

          <p className="text-sm text-muted-foreground">
            Consultants currently in active marketing campaigns.
          </p>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-100">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Consultant
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Title
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Visa
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Rate
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Availability
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Marketing Status
                  </th>

                  <th className="px-4 py-3 text-left text-sm font-medium">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody>
                {activeMarketingConsultants.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="py-12 text-center text-sm text-muted-foreground"
                    >
                      No consultants are currently in active marketing.
                    </td>
                  </tr>
                ) : (
                  activeMarketingConsultants.map((consultant: any) => (
                    <tr
                      key={consultant.public_id}
                      className="border-t hover:bg-slate-50"
                    >
                      <td className="px-4 py-3">
                        <div className="font-medium">
                          {consultant.first_name}{" "}
                          {consultant.last_name}
                        </div>

                        <div className="text-xs text-muted-foreground">
                          {consultant.email}
                        </div>
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.current_title || "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.visa_status || "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.expected_rate !== null &&
                        consultant.expected_rate !== undefined
                          ? `${consultant.rate_type || ""} ${consultant.expected_rate}`
                          : "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.availability_date || "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        {consultant.marketing_status || "N/A"}
                      </td>

                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            className="rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-slate-50"
                            onClick={() =>
                              setActivityHistoryConsultantId(consultant.public_id)
                            }
                          >
                            Activity History
                          </button>

                          <button
                            type="button"
                            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                            onClick={() =>
                              setActivityConsultantId(consultant.public_id)
                            }
                          >
                            Record Activity
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

            {selectedConsultantId && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Marketing History</CardTitle>
              <p className="text-sm text-muted-foreground">
                Real lifecycle history retrieved from the consultant marketing
                history API.
              </p>
            </div>

            <button
              type="button"
              className="rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-slate-50"
              onClick={() => setSelectedConsultantId(null)}
            >
              Close
            </button>
          </CardHeader>

          <CardContent>
            {isHistoryLoading ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                Loading marketing history...
              </div>
            ) : historyError ? (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                Failed to load marketing history.
              </div>
            ) : marketingHistory.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No marketing history found.
              </div>
            ) : (
              <div className="space-y-4">
                {marketingHistory.map(
                  (record: MarketingHistoryRecord, index: number) => (
                    <div
                      key={record.public_id}
                      className="relative rounded-lg border p-4"
                    >
                      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                        <div>
                          <div className="font-medium">
                            {formatHistoryStatus(record.status)}
                          </div>

                          <div className="text-sm text-muted-foreground">
                            Changed by user #{record.changed_by}
                          </div>
                        </div>

                        <div className="text-sm text-muted-foreground">
                          {formatHistoryDate(record.effective_from)}
                        </div>
                      </div>

                      {record.reason && (
                        <div className="mt-3 text-sm">
                          <span className="font-medium">Reason:</span>{" "}
                          {record.reason}
                        </div>
                      )}

                      {record.notes && (
                        <div className="mt-1 text-sm text-muted-foreground">
                          <span className="font-medium text-foreground">
                            Notes:
                          </span>{" "}
                          {record.notes}
                        </div>
                      )}

                      <div className="mt-2 text-xs text-muted-foreground">
                        {record.effective_until
                          ? `Ended: ${formatHistoryDate(
                              record.effective_until
                            )}`
                          : "Currently active"}
                      </div>

                      {index < marketingHistory.length - 1 && (
                        <div className="absolute -bottom-4 left-6 hidden h-4 border-l md:block" />
                      )}
                    </div>
                  )
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
      {activityHistoryConsultantId && (
  <Card className="mt-6">
    <CardHeader>
      <CardTitle>
        Marketing Activity History
        {activityHistoryConsultant && (
          <span className="ml-2 text-sm font-normal text-slate-500">
            — {activityHistoryConsultant.first_name}{" "}
            {activityHistoryConsultant.last_name}
          </span>
        )}
      </CardTitle>
    </CardHeader>

    <CardContent>
      {isActivitiesLoading ? (
        <p className="text-sm text-slate-500">
          Loading marketing activities...
        </p>
      ) : activitiesError ? (
        <p className="text-sm text-red-600">
          Failed to load marketing activities.
        </p>
      ) : marketingActivities.length === 0 ? (
        <p className="text-sm text-slate-500">
          No marketing activities recorded for this consultant.
        </p>
      ) : (
        <div className="space-y-3">
          {marketingActivities.map((activity: any) => (
            <div
              key={activity.public_id}
              className="rounded-lg border p-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="font-medium">
                  {activity.activity_type}
                </div>

                <div className="text-xs text-slate-500">
                  {activity.occurred_at
                    ? new Date(activity.occurred_at).toLocaleString()
                    : "No date"}
                </div>
              </div>

              <div className="mt-2 flex flex-wrap gap-2 text-sm text-slate-600">
                <span>Channel: {activity.channel}</span>
                <span>•</span>
                <span>Outcome: {activity.outcome}</span>
              </div>

              {activity.subject && (
                <div className="mt-2 text-sm">
                  <span className="font-medium">Subject:</span>{" "}
                  {activity.subject}
                </div>
              )}

              {activity.notes && (
                <div className="mt-1 text-sm text-slate-600">
                  <span className="font-medium text-slate-700">
                    Notes:
                  </span>{" "}
                  {activity.notes}
                </div>
              )}

              {activity.follow_up_required && (
                <div className="mt-2 text-sm font-medium">
                  Follow-up required
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </CardContent>
  </Card>
)}

      {actionError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {actionError}
        </div>
      )}
      {activityConsultantId && activityConsultant && (
        <RecordMarketingActivityDialog
          open={Boolean(activityConsultantId)}
          consultantPublicId={activityConsultantId}
          consultantName={`${activityConsultant.first_name} ${activityConsultant.last_name}`}
          onClose={() => setActivityConsultantId(null)}
          onCreated={() => {
            setActivityConsultantId(null);
          }}
        />
      )}

      <div className="text-sm text-muted-foreground">
        Marketing Workspace uses the existing consultant marketing workflow.
      </div>
    </div>
  );
}
