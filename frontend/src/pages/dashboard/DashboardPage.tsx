import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useExecutiveDashboard } from "@/hooks/useAnalytics";

export default function DashboardPage() {
  const navigate = useNavigate();

  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useExecutiveDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Welcome 👋
          </h2>

          <p className="text-muted-foreground">
            United Staffing AI Bench Platform
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          Loading dashboard...
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Welcome 👋
          </h2>

          <p className="text-muted-foreground">
            United Staffing AI Bench Platform
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-red-600">
            Failed to load dashboard data.
          </p>

          <Button
            className="mt-4"
            type="button"
            onClick={() => refetch()}
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const { summary, bench_health, forecast } = data;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">
          Welcome 👋
        </h2>

        <p className="text-muted-foreground">
          United Staffing AI Bench Platform
        </p>
      </div>

      {/* EXECUTIVE KPIs */}
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Consultants
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {summary.total_consultants}
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            {summary.available_consultants} available
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Requirements
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {summary.active_requirements}
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Active requirements
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Submissions
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {summary.active_submissions}
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Recorded submissions
          </p>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Placements
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {summary.placements_this_month}
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            This month
          </p>
        </div>
      </div>

      {/* BENCH HEALTH */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h3 className="mb-5 text-xl font-semibold">
          Bench Health
        </h3>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <p className="text-sm text-gray-500">
              Available
            </p>

            <p className="mt-1 text-2xl font-bold">
              {bench_health.available}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              Marketing Active
            </p>

            <p className="mt-1 text-2xl font-bold">
              {bench_health.marketing_active}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              Placed
            </p>

            <p className="mt-1 text-2xl font-bold">
              {bench_health.placed}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              Idle &gt; 30 Days
            </p>

            <p className="mt-1 text-2xl font-bold">
              {bench_health.idle_greater_30_days}
            </p>
          </div>
        </div>
      </div>

      {/* FORECAST */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h3 className="mb-5 text-xl font-semibold">
          Forecast
        </h3>

        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <p className="text-sm text-gray-500">
              Expected Placements
            </p>

            <p className="mt-1 text-2xl font-bold">
              {forecast.expected_placements_this_month}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              Pipeline Growth
            </p>

            <p className="mt-1 text-2xl font-bold">
              {forecast.pipeline_growth_velocity}
            </p>
          </div>
        </div>
      </div>

      {/* QUICK ACTIONS */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-xl font-semibold">
          Quick Actions
        </h3>

        <div className="flex flex-wrap gap-3">
          <Button
            type="button"
            onClick={() => navigate("/consultants")}
          >
            Add Consultant
          </Button>

          <Button
            variant="outline"
            type="button"
            onClick={() => navigate("/requirements")}
          >
            Create Requirement
          </Button>

          <Button
            variant="secondary"
            type="button"
            onClick={() => navigate("/ai-matching")}
          >
            AI Match
          </Button>
        </div>
      </div>
    </div>
  );
}