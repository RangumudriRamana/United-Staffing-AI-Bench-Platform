import { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";

import { useRequirements } from "@/hooks/useRequirements";
import { useAIMatch, useAIMatchHistory } from "@/hooks/useAIMatching";

import type { Requirement } from "@/features/requirements/types";
import type { BatchMatchItem } from "@/features/ai/types";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function AIMatchingPage() {
  const [selectedRequirementId, setSelectedRequirementId] = useState("");
  const [matches, setMatches] = useState<BatchMatchItem[]>([]);

  const requirementsQuery = useRequirements();
  const matchMutation = useAIMatch();
  const historyQuery = useAIMatchHistory();

  const requirements: Requirement[] = requirementsQuery.data ?? [];

  const selectedRequirement = requirements.find(
    (requirement) => requirement.public_id === selectedRequirementId,
  );

  const handleRunMatching = () => {
    if (!selectedRequirementId) {
      return;
    }

    matchMutation.mutate(
      {
        requirement_id: selectedRequirementId,
      },
      {
        onSuccess: (data) => {
          setMatches(data.matches);
        },
      },
    );
  };

  const formatScore = (score: number) => {
    return `${Math.round(score)}%`;
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <Sparkles className="h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">
            AI Matching
          </h1>
        </div>

        <p className="mt-1 text-sm text-muted-foreground">
          Find the best consultant matches for an open requirement.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Find Consultant Matches</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="requirement"
              className="text-sm font-medium"
            >
              Select Requirement
            </label>

            <select
              id="requirement"
              value={selectedRequirementId}
              onChange={(event) =>
                setSelectedRequirementId(event.target.value)
              }
              disabled={
                requirementsQuery.isLoading || matchMutation.isPending
              }
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">
                {requirementsQuery.isLoading
                  ? "Loading requirements..."
                  : "Select a requirement"}
              </option>

              {requirements.map((requirement) => (
                <option
                  key={requirement.public_id}
                  value={requirement.public_id}
                >
                  {requirement.job_title}
                  {requirement.job_code
                    ? ` — ${requirement.job_code}`
                    : ""}
                </option>
              ))}
            </select>
          </div>

          {selectedRequirement && (
            <div className="rounded-lg border bg-muted/30 p-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Job Title
                  </p>
                  <p className="text-sm font-medium">
                    {selectedRequirement.job_title}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">
                    Employment
                  </p>
                  <p className="text-sm font-medium">
                    {selectedRequirement.employment_type}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">
                    Work Model
                  </p>
                  <p className="text-sm font-medium">
                    {selectedRequirement.work_model}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">
                    Location
                  </p>
                  <p className="text-sm font-medium">
                    {selectedRequirement.location || "—"}
                  </p>
                </div>
              </div>
            </div>
          )}

          <Button
            type="button"
            onClick={handleRunMatching}
            disabled={!selectedRequirementId || matchMutation.isPending}
          >
            {matchMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Finding Matches...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Find Matches
              </>
            )}
          </Button>

          {requirementsQuery.isError && (
            <p className="text-sm text-destructive">
              Failed to load requirements.
            </p>
          )}

          {matchMutation.isError && (
            <p className="text-sm text-destructive">
              Failed to run AI matching. Please try again.
            </p>
          )}
        </CardContent>
      </Card>

      {matches.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>
              Matching Consultants ({matches.length})
            </CardTitle>
          </CardHeader>

          <CardContent>
            <div className="space-y-3">
              {matches.map((match) => (
                <div
                  key={match.consultant_id}
                  className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0">
                    <p className="font-medium">
                      {match.consultant_name}
                    </p>

                    <p className="mt-1 text-sm text-muted-foreground">
                      {match.recommendation}
                    </p>
                  </div>

                  <div className="shrink-0 text-left sm:text-right">
                    <p className="text-2xl font-semibold">
                      {formatScore(match.score)}
                    </p>

                    <p className="text-xs text-muted-foreground">
                      Match Score
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {!matches.length && !matchMutation.isPending && (
        <Card>
          <CardContent className="py-10 text-center">
            <Sparkles className="mx-auto h-8 w-8 text-muted-foreground" />

            <p className="mt-3 text-sm font-medium">
              No matches to display
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              Select a requirement and run AI matching to see consultant
              recommendations.
            </p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Recent AI Match History</CardTitle>
        </CardHeader>

        <CardContent>
          {historyQuery.isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin" />
            </div>
          ) : historyQuery.isError ? (
            <p className="text-sm text-destructive">
              Failed to load AI match history.
            </p>
          ) : historyQuery.data?.history.length ? (
            <div className="space-y-3">
              {historyQuery.data.history.map((item, index) => (
                <div
                  key={`${item.consultant_id}-${item.requirement_id}-${item.matched_at}-${index}`}
                  className="flex flex-col gap-2 rounded-lg border p-4"
                >
                  <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                    <p className="text-sm font-medium">
                      Consultant: {item.consultant_name}
                    </p>

                    <p className="text-sm font-semibold">
                      {formatScore(item.match_score)}
                    </p>
                  </div>

                  <p className="text-sm text-muted-foreground">
                    Requirement: {item.requirement_name}
                  </p>

                  <p className="text-sm">
                    {item.recommendation}
                  </p>

                  <p className="text-xs text-muted-foreground">
                    {new Date(item.matched_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No AI match history yet.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
