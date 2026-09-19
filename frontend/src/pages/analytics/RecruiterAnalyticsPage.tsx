import {
  Activity,
  AlertTriangle,
  Clock3,
  MessageSquare,
  Send,
  Target,
  Trophy,
  Users,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useRecruiterDashboard } from "@/hooks/useAnalytics";

function formatPercentage(value: number) {
  return `${value.toFixed(1)}%`;
}

function formatDateTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function getSeverityClass(severity: string) {
  switch (severity.toUpperCase()) {
    case "HIGH":
      return "border-destructive/30 bg-destructive/5";
    case "MEDIUM":
      return "border-amber-500/30 bg-amber-500/5";
    default:
      return "border-border bg-muted/20";
  }
}

export default function RecruiterAnalyticsPage() {
  const {
    data,
    isLoading,
    isError,
    error,
  } = useRecruiterDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Recruiter Dashboard
          </h1>

          <p className="text-sm text-muted-foreground">
            Personal recruiting performance, follow-ups, and recent activity.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {Array.from({ length: 5 }).map((_, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="h-4 w-28 animate-pulse rounded bg-muted" />
                <div className="mt-4 h-8 w-16 animate-pulse rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {Array.from({ length: 2 }).map((_, index) => (
            <Card key={index}>
              <CardHeader>
                <div className="h-5 w-36 animate-pulse rounded bg-muted" />
              </CardHeader>

              <CardContent>
                <div className="space-y-4">
                  <div className="h-16 animate-pulse rounded bg-muted" />
                  <div className="h-16 animate-pulse rounded bg-muted" />
                  <div className="h-16 animate-pulse rounded bg-muted" />
                </div>
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
            Recruiter Dashboard
          </h1>

          <p className="text-sm text-muted-foreground">
            Personal recruiting performance, follow-ups, and recent activity.
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <p className="font-medium">
              Unable to load recruiter dashboard.
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
    followups,
    timeline,
  } = data;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Recruiter Dashboard
        </h1>

        <p className="text-sm text-muted-foreground">
          Personal recruiting performance, follow-ups, and recent activity.
        </p>
      </div>

      {/* KPI Summary */}
      <section className="space-y-3">
        <div>
          <h2 className="text-lg font-semibold">
            Performance Summary
          </h2>

          <p className="text-sm text-muted-foreground">
            Your current recruiting activity and placement performance.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Active Consultants
                </p>

                <Users className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.active_consultants}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Total Submissions
                </p>

                <Send className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.total_submissions}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Interviews Scheduled
                </p>

                <MessageSquare className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.interviews_scheduled}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Placements Secured
                </p>

                <Trophy className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {summary.placements_secured}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Conversion Rate
                </p>

                <Target className="h-5 w-5 text-muted-foreground" />
              </div>

              <p className="mt-3 text-3xl font-semibold">
                {formatPercentage(
                  summary.placement_conversion_rate
                )}
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Follow-ups + Activity */}
      <section className="grid gap-6 lg:grid-cols-2">
        {/* Follow-up Queue */}
        <Card>
          <CardHeader>
            <CardTitle>Actionable Follow-ups</CardTitle>

            <p className="text-sm text-muted-foreground">
              Items that may require recruiter attention.
            </p>
          </CardHeader>

          <CardContent>
            {followups.length === 0 ? (
              <div className="rounded-lg border border-dashed p-8 text-center">
                <p className="font-medium">
                  No follow-ups available.
                </p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Your follow-up queue is currently clear.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {followups.map((item, index) => (
                  <div
                    key={`${item.task_type}-${item.target_public_id ?? index}`}
                    className={`rounded-lg border p-4 ${getSeverityClass(
                      item.severity
                    )}`}
                  >
                    <div className="flex items-start gap-3">
                      {item.severity.toUpperCase() === "HIGH" ? (
                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
                      ) : (
                        <Activity className="mt-0.5 h-5 w-5 shrink-0" />
                      )}

                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="font-medium">
                            {item.task_type.replaceAll("_", " ")}
                          </p>

                          <span className="text-xs font-medium uppercase text-muted-foreground">
                            {item.severity}
                          </span>
                        </div>

                        <p className="mt-1 text-sm text-muted-foreground">
                          {item.description}
                        </p>

                        {item.target_public_id && (
                          <p className="mt-2 text-xs text-muted-foreground">
                            Reference: {item.target_public_id}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>

            <p className="text-sm text-muted-foreground">
              Latest recruiting events recorded by the platform.
            </p>
          </CardHeader>

          <CardContent>
            {timeline.length === 0 ? (
              <div className="rounded-lg border border-dashed p-8 text-center">
                <p className="font-medium">
                  No recent activity.
                </p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Recruiting activity will appear here as events are recorded.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {timeline.map((event, index) => (
                  <div
                    key={`${event.occurred_at}-${event.event_type}-${index}`}
                    className="flex gap-3"
                  >
                    <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border bg-muted/30">
                      <Activity className="h-4 w-4" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="font-medium">
                        {event.event_type.replaceAll("_", " ")}
                      </p>

                      <p className="mt-1 text-sm text-muted-foreground">
                        {event.summary}
                      </p>

                      <p className="mt-2 text-xs text-muted-foreground">
                        {formatDateTime(event.occurred_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Dashboard Footer */}
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Clock3 className="h-4 w-4" />

        <span>
          Recruiter analytics are loaded from the authenticated recruiter
          workspace.
        </span>
      </div>
    </div>
  );
}