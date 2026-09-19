import { CheckCircle2, Clock3, ListTodo } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTasks } from "@/hooks/useTasks";
import { useCompleteTask } from "@/hooks/useCompleteTask";
import type { Task } from "@/features/tasks/types";

export default function TasksPage() {
  const { data: tasks = [], isLoading, error } = useTasks();
  const completeTask = useCompleteTask();

  const handleComplete = async (task: Task) => {
    try {
      await completeTask.mutateAsync(task.public_id);
    } catch {
      // Error state is handled below through the mutation state.
    }
  };

  const openTasks = tasks.filter(
    (task) =>
      task.status === "OPEN" ||
      task.status === "IN_PROGRESS"
  );

  const urgentTasks = openTasks.filter(
    (task) => task.priority === "URGENT"
  );

  const highPriorityTasks = openTasks.filter(
    (task) => task.priority === "HIGH"
  );

  const formatDate = (value: string) =>
    new Date(value).toLocaleString();

  const formatLabel = (value: string) =>
    value.replaceAll("_", " ");

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">My Tasks</h1>
          <p className="text-muted-foreground">
            Review and complete your operational follow-up tasks.
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

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">My Tasks</h1>
          <p className="text-muted-foreground">
            Review and complete your operational follow-up tasks.
          </p>
        </div>

        <Card>
          <CardContent className="p-6 text-red-600">
            Failed to load your tasks.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* PAGE HEADER */}
      <div>
        <h1 className="text-3xl font-bold">My Tasks</h1>
        <p className="text-muted-foreground">
          Review and complete your operational follow-up tasks.
        </p>
      </div>

      {/* SUMMARY */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Open Tasks
            </CardTitle>

            <ListTodo className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {openTasks.length}
            </div>

            <p className="mt-1 text-xs text-muted-foreground">
              Tasks requiring action
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Urgent
            </CardTitle>

            <Clock3 className="h-5 w-5 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-3xl font-bold">
              {urgentTasks.length}
            </div>

            <p className="mt-1 text-xs text-muted-foreground">
              Urgent tasks requiring attention
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
              {highPriorityTasks.length}
            </div>

            <p className="mt-1 text-xs text-muted-foreground">
              High-priority tasks
            </p>
          </CardContent>
        </Card>
      </div>

      {/* TASK LIST */}
      <Card>
        <CardHeader>
          <CardTitle>Active Task Queue</CardTitle>

          <p className="text-sm text-muted-foreground">
            Tasks assigned to the currently authenticated user.
          </p>
        </CardHeader>

        <CardContent className="p-0">
          {openTasks.length === 0 ? (
            <div className="py-12 text-center text-sm text-muted-foreground">
              No active tasks found.
            </div>
          ) : (
            <div className="divide-y">
              {openTasks.map((task) => (
                <div
                  key={task.public_id}
                  className="flex flex-col gap-4 p-5 md:flex-row md:items-start md:justify-between"
                >
                  <div className="min-w-0">
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

                    <div className="mt-2 text-sm text-muted-foreground">
                      {formatLabel(task.task_type)}
                    </div>

                    {task.description && (
                      <p className="mt-2 text-sm">
                        {task.description}
                      </p>
                    )}

                    <div className="mt-3 text-xs text-muted-foreground">
                      Due: {formatDate(task.due_at)}
                    </div>
                  </div>

                  <button
                    type="button"
                    className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={completeTask.isPending}
                    onClick={() => handleComplete(task)}
                  >
                    {completeTask.isPending
                      ? "Completing..."
                      : "Complete"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {completeTask.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to complete the task. Please try again.
        </div>
      )}
    </div>
  );
}