import {
  Activity,
  BriefcaseBusiness,
  ChartNoAxesCombined,
  Clock3,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useExecutiveDashboard } from "@/hooks/useAnalytics";

function formatPercentage(value: number) {
  return `${value.toFixed(1)}%`;
}

export default function AnalyticsPage() {
  const {
    data,
    isLoading,
    isError,
    error,
  } = useExecutiveDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Executive Analytics
          </h1>
          <p className="text-sm text-muted-foreground">
            Firm-wide staffing performance and bench health.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {Array.from({ length: 5 }).map((_, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="h-4 w-24 animate-pulse rounded bg-muted" />
                <div className="mt-4 h-8 w-16 animate-pulse rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Executive Analytics
          </h1>
          <p className="text-sm text-muted-foreground">
            Firm-wide staffing performance and bench health.
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <p className="font-medium">
              Unable to load executive analytics.
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              {error instanceof Error
                ? error.message
                : "Please try again later."}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const {
    summary,
    bench_health,
    recruiter_performance,
    forecast,
  } = data;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Executive Analytics
        </h1>

        <p className="text-sm text-muted-foreground">
          Firm-wide staffing performance, bench health, recruiter
          performance, and pipeline forecast.
        </p>
      </div>

      {/* Executive Summary */}
      <section className="space-y-3">
        <div>
          <h2 className="text-lg font-semibold">
            Executive Summary
          </h2>

          <p className="text-sm text-muted-foreground">
            Current staffing operations at a glance.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Total Consultants
                </p>

                <Users className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.total_consultants}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Available Consultants
                </p>

                <Activity className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.available_consultants}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Active Requirements
                </p>

                <BriefcaseBusiness className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.active_requirements}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Active Submissions
                </p>

                <Target className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.active_submissions}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Placements This Month
                </p>

                <TrendingUp className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.placements_this_month}
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Bench Health + Forecast */}
      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Bench Health</CardTitle>

            <p className="text-sm text-muted-foreground">
              Current consultant availability and bench status.
            </p>
          </CardHeader>

          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">
                  Available
                </p>

                <p className="mt-2 text-2xl font-semibold">
                  {bench_health.available}
                </p>
              </div>

              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">
                  Marketing Active
                </p>

                <p className="mt-2 text-2xl font-semibold">
                  {bench_health.marketing_active}
                </p>
              </div>

              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">
                  Placed
                </p>

                <p className="mt-2 text-2xl font-semibold">
                  {bench_health.placed}
                </p>
              </div>

              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">
                  Idle &gt; 30 Days
                </p>

                <p className="mt-2 text-2xl font-semibold">
                  {bench_health.idle_greater_30_days}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pipeline Forecast</CardTitle>

            <p className="text-sm text-muted-foreground">
              Current forecast indicators for this month.
            </p>
          </CardHeader>

          <CardContent>
            <div className="space-y-5">
              <div className="rounded-lg border p-5">
                <div className="flex items-center gap-3">
                  <ChartNoAxesCombined className="h-5 w-5 text-muted-foreground" />

                  <div>
                    <p className="text-sm text-muted-foreground">
                      Expected Placements This Month
                    </p>

                    <p className="mt-1 text-3xl font-semibold">
                      {forecast.expected_placements_this_month}
                    </p>
                  </div>
                </div>
              </div>

              <div className="rounded-lg border p-5">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-muted-foreground" />

                  <div>
                    <p className="text-sm text-muted-foreground">
                      Pipeline Growth Velocity
                    </p>

                    <p className="mt-1 text-lg font-semibold">
                      {forecast.pipeline_growth_velocity}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Recruiter Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Recruiter Performance</CardTitle>

          <p className="text-sm text-muted-foreground">
            Submission and placement performance across recruiters.
          </p>
        </CardHeader>

        <CardContent>
          {recruiter_performance.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center">
              <p className="font-medium">
                No recruiter performance data available.
              </p>

              <p className="mt-1 text-sm text-muted-foreground">
                Recruiter performance will appear here when data is
                available.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="px-4 py-3 font-medium">
                      Recruiter
                    </th>

                    <th className="px-4 py-3 font-medium">
                      Submissions
                    </th>

                    <th className="px-4 py-3 font-medium">
                      Placements
                    </th>

                    <th className="px-4 py-3 font-medium">
                      Conversion Rate
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {recruiter_performance.map((recruiter) => (
                    <tr
                      key={recruiter.recruiter_name}
                      className="border-b last:border-0"
                    >
                      <td className="px-4 py-3 font-medium">
                        {recruiter.recruiter_name}
                      </td>

                      <td className="px-4 py-3">
                        {recruiter.submissions_count}
                      </td>

                      <td className="px-4 py-3">
                        {recruiter.placements_count}
                      </td>

                      <td className="px-4 py-3">
                        {formatPercentage(
                          recruiter.conversion_rate
                        )}
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
        <Clock3 className="h-4 w-4" />
        <span>
          Analytics data is loaded from the platform's executive
          dashboard.
        </span>
      </div>
    </div>
  );
}