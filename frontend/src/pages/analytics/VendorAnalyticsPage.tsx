import * as React from "react";
import {
  Activity,
  Clock3,
  HeartPulse,
  TrendingUp,
  Users,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useVendorAnalytics } from "@/hooks/useAnalytics";
import { useVendors } from "@/hooks/useVendors";

export default function VendorAnalyticsPage() {
  const {
    data: vendorsData,
    isLoading: vendorsLoading,
    isError: vendorsError,
  } = useVendors();

  const [selectedVendorId, setSelectedVendorId] = React.useState("");

  const vendors = vendorsData?.data ?? [];

  const {
    data,
    isLoading,
    isError,
    error,
  } = useVendorAnalytics(selectedVendorId);

  if (vendorsLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Vendor Analytics
          </h1>

          <p className="text-sm text-muted-foreground">
            Vendor relationship health, submission funnel, and response
            velocity.
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <div className="h-9 w-full animate-pulse rounded bg-muted" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (vendorsError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Vendor Analytics
          </h1>

          <p className="text-sm text-muted-foreground">
            Vendor relationship health, submission funnel, and response
            velocity.
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <p className="font-medium">
              Unable to load vendors.
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              Please try again later.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Vendor Analytics
        </h1>

        <p className="text-sm text-muted-foreground">
          Vendor relationship health, submission funnel, and response
          velocity.
        </p>
      </div>

      {/* Vendor Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Select Vendor</CardTitle>

          <p className="text-sm text-muted-foreground">
            Choose a vendor to review its commercial relationship metrics.
          </p>
        </CardHeader>

        <CardContent>
          {vendors.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center">
              <p className="font-medium">
                No vendors available.
              </p>

              <p className="mt-1 text-sm text-muted-foreground">
                Add a vendor before viewing vendor analytics.
              </p>
            </div>
          ) : (
            <select
              value={selectedVendorId}
              onChange={(event) =>
                setSelectedVendorId(event.target.value)
              }
              className="flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-xs outline-none sm:max-w-md"
            >
              <option value="">
                Select a vendor
              </option>

              {vendors.map((vendor) => (
                <option
                  key={vendor.public_id}
                  value={vendor.public_id}
                >
                  {vendor.name}
                </option>
              ))}
            </select>
          )}
        </CardContent>
      </Card>

      {/* Empty Selection State */}
      {!selectedVendorId && vendors.length > 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <Activity className="mx-auto h-8 w-8 text-muted-foreground" />

            <p className="mt-3 font-medium">
              Select a vendor to view analytics.
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              Vendor funnel, relationship health, and response velocity will
              appear here.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Analytics Loading */}
      {selectedVendorId && isLoading && (
        <div className="grid gap-6 lg:grid-cols-2">
          {Array.from({ length: 4 }).map((_, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="h-5 w-36 animate-pulse rounded bg-muted" />

                <div className="mt-5 space-y-3">
                  <div className="h-12 animate-pulse rounded bg-muted" />
                  <div className="h-12 animate-pulse rounded bg-muted" />
                  <div className="h-12 animate-pulse rounded bg-muted" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Analytics Error */}
      {selectedVendorId && isError && (
        <Card>
          <CardContent className="p-6">
            <p className="font-medium">
              Unable to load vendor analytics.
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              {error instanceof Error
                ? error.message
                : "Please try again later."}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Analytics Data */}
      {selectedVendorId && data && !isLoading && !isError && (
        <>
          {/* Vendor Header */}
          <div>
            <h2 className="text-lg font-semibold">
              {data.vendor_name}
            </h2>

            <p className="text-sm text-muted-foreground">
              Commercial relationship analytics for this vendor.
            </p>
          </div>

          {/* Relationship Health + Velocity */}
          <section className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <HeartPulse className="h-5 w-5 text-muted-foreground" />

                  <div>
                    <CardTitle>
                      Relationship Health
                    </CardTitle>

                    <p className="mt-1 text-sm text-muted-foreground">
                      Overall vendor relationship assessment.
                    </p>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <div className="rounded-lg border p-5">
                  <p className="text-sm text-muted-foreground">
                    Health Score
                  </p>

                  <p className="mt-2 text-3xl font-semibold">
                    {data.health.health_score}
                  </p>

                  <p className="mt-1 text-sm font-medium">
                    {data.health.status_label}
                  </p>
                </div>

                {data.health.contributing_factors.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium">
                      Contributing Factors
                    </p>

                    <ul className="mt-3 space-y-2">
                      {data.health.contributing_factors.map(
                        (factor, index) => (
                          <li
                            key={`${factor}-${index}`}
                            className="rounded-lg border p-3 text-sm text-muted-foreground"
                          >
                            {factor}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <Clock3 className="h-5 w-5 text-muted-foreground" />

                  <div>
                    <CardTitle>
                      Response Velocity
                    </CardTitle>

                    <p className="mt-1 text-sm text-muted-foreground">
                      Average time between key staffing events.
                    </p>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">
                      Requirement → Submission
                    </p>

                    <p className="mt-2 text-2xl font-semibold">
                      {data.velocity.avg_days_req_to_submission}
                    </p>

                    <p className="mt-1 text-xs text-muted-foreground">
                      days
                    </p>
                  </div>

                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">
                      Submission → Interview
                    </p>

                    <p className="mt-2 text-2xl font-semibold">
                      {data.velocity.avg_days_submission_to_interview}
                    </p>

                    <p className="mt-1 text-xs text-muted-foreground">
                      days
                    </p>
                  </div>

                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">
                      Interview → Feedback
                    </p>

                    <p className="mt-2 text-2xl font-semibold">
                      {data.velocity.avg_days_interview_to_feedback}
                    </p>

                    <p className="mt-1 text-xs text-muted-foreground">
                      days
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Funnel */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <TrendingUp className="h-5 w-5 text-muted-foreground" />

                <div>
                  <CardTitle>
                    Vendor Submission Funnel
                  </CardTitle>

                  <p className="mt-1 text-sm text-muted-foreground">
                    Progression through the vendor staffing pipeline.
                  </p>
                </div>
              </div>
            </CardHeader>

            <CardContent>
              {data.funnel.length === 0 ? (
                <div className="rounded-lg border border-dashed p-8 text-center">
                  <p className="font-medium">
                    No funnel data available.
                  </p>

                  <p className="mt-1 text-sm text-muted-foreground">
                    Funnel metrics will appear as staffing activity is
                    recorded.
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[600px] text-sm">
                    <thead>
                      <tr className="border-b text-left">
                        <th className="px-4 py-3 font-medium">
                          Stage
                        </th>

                        <th className="px-4 py-3 font-medium">
                          Count
                        </th>

                        <th className="px-4 py-3 font-medium">
                          Conversion Rate
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {data.funnel.map((stage) => (
                        <tr
                          key={stage.stage_name}
                          className="border-b last:border-0"
                        >
                          <td className="px-4 py-3 font-medium">
                            {stage.stage_name}
                          </td>

                          <td className="px-4 py-3">
                            {stage.count}
                          </td>

                          <td className="px-4 py-3">
                            {stage.conversion_rate.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Analytics Footer */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Users className="h-4 w-4" />

            <span>
              Vendor analytics are loaded from the commercial operations
              analytics service.
            </span>
          </div>
        </>
      )}
    </div>
  );
}