import {
  AlertCircle,
  BriefcaseBusiness,
  CalendarDays,
  CheckCircle2,
  ListTodo,
  Megaphone,
  Send,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePlanner } from "@/hooks/usePlanner";

export default function PlannerPage() {
  const { data, isLoading, error } = usePlanner();

  const summary = data?.summary;
  const tasks = data?.tasks ?? [];

  const formatLabel = (value: string) =>
    value.replaceAll("_", " ");

  const formatDate = (value: string) =>
    new Date(value).toLocaleString();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Daily Planner</h1>
          <p className="text-muted-foreground">
            Your daily operational overview for staffing activities.
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <div className="h-48 animate-pulse rounded bg-slate-100" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Daily Planner</h1>
          <p className="text-muted-foreground">
            Your daily operational overview for staffing activities.
          </p>
        </div>

        <Card>
          <CardContent className="p-6 text-red-600">
            Failed to load the daily planner.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div>
        <h1 className="text-3xl font-bold">Daily Planner</h1>
        <p className="text-muted-foreground">
          Operational overview for {summary.planner_date}.
        </p>
      </div>

      {/* SUMMARY */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Open Tasks
            </CardTitle>
            <ListTodo className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {summary.open_tasks}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Tasks requiring action today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Urgent Tasks
            </CardTitle>
            <AlertCircle className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {summary.urgent_tasks}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Urgent items requiring attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              High Priority
            </CardTitle>
            <CheckCircle2 className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {summary.high_priority_tasks}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              High-priority items today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Marketing Follow-ups
            </CardTitle>
            <Megaphone className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {summary.marketing_follow_ups}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Marketing follow-ups today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Submission Follow-ups
            </CardTitle>
            <Send className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {summary.submission_follow_ups}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Submission follow-ups today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Vendor Outreach
            </CardTitle>
            <BriefcaseBusiness className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {summary.vendor_outreach}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Vendor outreach items today
            </p>
          </CardContent>
        </Card>
      </div>

      {/* DAILY TASKS */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarDays className="h-5 w-5" />
            Today&apos;s Plan
          </CardTitle>

          <p className="text-sm text-muted-foreground">
            Tasks scheduled for this planner date.
          </p>
        </CardHeader>

        <CardContent className="p-0">
          {tasks.length === 0 ? (
            <div className="py-12 text-center text-sm text-muted-foreground">
              No planned activities for today.
            </div>
          ) : (
            <div className="divide-y">
              {tasks.map((task) => (
                <div
                  key={task.public_id}
                  className="flex flex-col gap-3 p-5"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-medium">
                      {task.title}
                    </h3>

                    <span className="rounded-full border px-2 py-0.5 text-xs">
                      {formatLabel(task.priority)}
                    </span>

                    <span className="rounded-full border px-2 py-0.5 text-xs">
                      {formatLabel(task.status)}
                    </span>
                  </div>

                  <div className="text-sm text-muted-foreground">
                    {formatLabel(task.task_type)}
                  </div>

                  <div className="text-xs text-muted-foreground">
                    Due: {formatDate(task.due_at)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}