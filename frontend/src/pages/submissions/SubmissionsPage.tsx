import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import { useSubmissions } from "@/hooks/useSubmissions";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}

function formatStatus(status: string) {
  return status.replaceAll("_", " ");
}

export default function SubmissionsPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  const { data, isLoading, error, refetch } = useSubmissions(
    search.trim()
      ? {
          job_title: search.trim(),
        }
      : undefined
  );

  const submissions = data ?? [];

  if (isLoading && !data) {
    return (
      <div className="p-6">
        Loading submissions...
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div>
          <h1 className="text-2xl font-semibold">
            Submissions
          </h1>

          <p className="text-sm text-muted-foreground">
            Track consultant submissions and pipeline progress.
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-destructive">
              Failed to load submissions.
            </p>

            <Button
              variant="outline"
              className="mt-4"
              onClick={() => refetch()}
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">
            Submissions
          </h1>

          <p className="text-sm text-muted-foreground">
            Track consultant submissions and pipeline progress.
          </p>
        </div>

        <Button onClick={() => navigate("/submissions/new")}>
          New Submission
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Submission Pipeline</CardTitle>

          <CardDescription>
            Search and review consultant submissions.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="mb-5 flex items-center gap-3">
            <Input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by job title..."
              className="max-w-sm"
            />

            <Button
              variant="outline"
              onClick={() => setSearch("")}
              disabled={!search}
            >
              Clear
            </Button>
          </div>

          {submissions.length === 0 ? (
            <div className="rounded-lg border p-8 text-center">
              <p className="text-sm text-muted-foreground">
                No submissions found.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/40">
                    <th className="px-4 py-3 text-left font-medium">
                      Job
                    </th>

                    <th className="px-4 py-3 text-left font-medium">
                      Client
                    </th>

                    <th className="px-4 py-3 text-left font-medium">
                      Employment
                    </th>

                    <th className="px-4 py-3 text-left font-medium">
                      Rate
                    </th>

                    <th className="px-4 py-3 text-left font-medium">
                      Status
                    </th>

                    <th className="px-4 py-3 text-left font-medium">
                      Submitted
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {submissions.map((submission) => (
                    <tr
                      key={submission.public_id}
                      onClick={() =>
                        navigate(`/submissions/${submission.public_id}`)
                      }
                      className="cursor-pointer border-b last:border-0 hover:bg-muted/30"
                    >
                      <td className="px-4 py-4">
                        <div className="font-medium">
                          {submission.job_title}
                        </div>

                        <div className="text-xs text-muted-foreground">
                          {submission.job_id ?? "No Job ID"}
                        </div>
                      </td>

                      <td className="px-4 py-4">
                        <div>
                          {submission.client_name_snapshot}
                        </div>

                        <div className="text-xs text-muted-foreground">
                          {submission.job_location ?? "Location not specified"}
                        </div>
                      </td>

                      <td className="px-4 py-4">
                        {submission.employment_type}
                      </td>

                      <td className="px-4 py-4">
                        {submission.currency} {submission.rate}
                      </td>

                      <td className="px-4 py-4">
                        <span className="inline-flex rounded-full border px-2.5 py-1 text-xs font-medium">
                          {formatStatus(
                            submission.submission_status
                          )}
                        </span>
                      </td>

                      <td className="px-4 py-4 text-muted-foreground">
                        {formatDate(
                          submission.submitted_at
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="mt-4 text-sm text-muted-foreground">
            Showing {submissions.length} submissions
          </div>
        </CardContent>
      </Card>
    </div>
  );
}