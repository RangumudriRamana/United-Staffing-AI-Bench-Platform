import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { useSubmission } from "@/hooks/useSubmissions";
import {
  useCreateOffer,
  useCreatePlacement,
  useTransitionSubmission,
} from "@/hooks/useSubmissionMutations";

import type { SubmissionStatus } from "@/features/submissions/types";

function formatStatus(status: string) {
  return status.replaceAll("_", " ");
}

function formatDate(value: string | null) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleDateString();
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

const allowedTransitions: Record<
  SubmissionStatus,
  SubmissionStatus[]
> = {
  DRAFT: ["SUBMITTED", "WITHDRAWN"],

  SUBMITTED: [
    "UNDER_REVIEW",
    "REJECTED",
    "WITHDRAWN",
  ],

  UNDER_REVIEW: [
    "INTERVIEW_SCHEDULED",
    "REJECTED",
    "WITHDRAWN",
  ],

  INTERVIEW_SCHEDULED: [
    "INTERVIEW_COMPLETED",
    "REJECTED",
    "WITHDRAWN",
  ],

  INTERVIEW_COMPLETED: [
    "OFFER_RECEIVED",
    "INTERVIEW_SCHEDULED",
    "REJECTED",
    "WITHDRAWN",
  ],

  OFFER_RECEIVED: [
    "OFFER_ACCEPTED",
    "CLOSED",
    "REJECTED",
  ],

  OFFER_ACCEPTED: [
    "PLACED",
    "CLOSED",
  ],

  PLACED: ["CLOSED"],

  REJECTED: [],
  WITHDRAWN: [],
  CLOSED: [],
};

export default function SubmissionDetailPage() {
  const navigate = useNavigate();
  const { publicId } = useParams<{ publicId: string }>();

  const transitionMutation = useTransitionSubmission();
  const createOfferMutation = useCreateOffer();
  const createPlacementMutation = useCreatePlacement();

  const [targetStatus, setTargetStatus] =
    useState<SubmissionStatus | "">("");
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");
  const [offeredRate, setOfferedRate] = useState("");
  const [offerCurrency, setOfferCurrency] = useState("USD");
  const [offerStartDate, setOfferStartDate] = useState("");
  const [offerExpirationDate, setOfferExpirationDate] =
    useState("");
  const [offerNotes, setOfferNotes] = useState("");
  const [placementStartedOn, setPlacementStartedOn] =
  useState("");
  const [placementEndedOn, setPlacementEndedOn] =
  useState("");
  const [placementBillingRate, setPlacementBillingRate] =
  useState("");
  const [placementPayRate, setPlacementPayRate] =
  useState("");
  const {
    data: submission,
    isLoading,
    error,
    refetch,
  } = useSubmission(publicId);

  const availableTransitions: SubmissionStatus[] =
    submission
      ? allowedTransitions[submission.submission_status] ?? []
      : [];

  function handleTransition() {
    if (!publicId || !targetStatus) {
      return;
    }

    transitionMutation.mutate(
      {
        publicId,
        payload: {
          target_status: targetStatus,
          reason: reason.trim() || null,
          notes: notes.trim() || null,
        },
      },
      {
        onSuccess: () => {
          setTargetStatus("");
          setReason("");
          setNotes("");
        },
      }
    );
  }
  function handleCreateOffer() {
  if (
    !publicId ||
    !offeredRate ||
    !offerStartDate
  ) {
    return;
  }

  createOfferMutation.mutate(
    {
      publicId,
      payload: {
        offered_rate: Number(offeredRate),
        currency: offerCurrency,
        start_date: offerStartDate,
        expiration_date:
          offerExpirationDate || null,
        notes: offerNotes.trim() || null,
      },
    },
    {
      onSuccess: () => {
        setOfferedRate("");
        setOfferCurrency("USD");
        setOfferStartDate("");
        setOfferExpirationDate("");
        setOfferNotes("");
      },
    }
  );
}

function handleCreatePlacement() {
  if (
    !publicId ||
    !placementStartedOn ||
    !placementBillingRate ||
    !placementPayRate
  ) {
    return;
  }

  createPlacementMutation.mutate(
    {
      publicId,
      payload: {
        started_on: placementStartedOn,
        ended_on: placementEndedOn || null,
        billing_rate: Number(placementBillingRate),
        pay_rate: Number(placementPayRate),
      },
    },
    {
      onSuccess: () => {
        setPlacementStartedOn("");
        setPlacementEndedOn("");
        setPlacementBillingRate("");
        setPlacementPayRate("");
      },
    }
  );
}

  if (isLoading) {
    return (
      <div className="p-6">
        Loading submission...
      </div>
    );
  }

  if (error || !submission) {
    return (
      <div className="space-y-4 p-6">
        <Button
          variant="outline"
          onClick={() => navigate("/submissions")}
        >
          Back to Submissions
        </Button>

        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-destructive">
              Failed to load submission.
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
          <Button
            variant="ghost"
            className="mb-2 px-0"
            onClick={() => navigate("/submissions")}
          >
            ← Back to Submissions
          </Button>

          <h1 className="text-2xl font-semibold">
            {submission.job_title}
          </h1>

          <p className="text-sm text-muted-foreground">
            {submission.client_name_snapshot}
          </p>
        </div>

        <span className="inline-flex rounded-full border px-3 py-1.5 text-sm font-medium">
          {formatStatus(submission.submission_status)}
        </span>
      </div>

            {/* Status Transition */}
      {availableTransitions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Update Submission Status</CardTitle>

            <CardDescription>
              Move this submission to the next valid pipeline stage.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              <div>
                <label
                  htmlFor="target-status"
                  className="mb-2 block text-sm font-medium"
                >
                  Target Status
                </label>

                <select
                  id="target-status"
                  onChange={(event) =>
                    setTargetStatus(
                        event.target.value as SubmissionStatus
                       )
                  }
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                  disabled={transitionMutation.isPending}
                >
                  <option value="">
                    Select target status...
                  </option>

                  {availableTransitions.map((status) => (
                    <option key={status} value={status}>
                      {formatStatus(status)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="transition-reason"
                  className="mb-2 block text-sm font-medium"
                >
                  Reason
                </label>

                <input
                  id="transition-reason"
                  type="text"
                  value={reason}
                  onChange={(event) =>
                    setReason(event.target.value)
                  }
                  placeholder="Why is the status changing?"
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                  disabled={transitionMutation.isPending}
                />
              </div>

              <div>
                <label
                  htmlFor="transition-notes"
                  className="mb-2 block text-sm font-medium"
                >
                  Notes
                </label>

                <textarea
                  id="transition-notes"
                  value={notes}
                  onChange={(event) =>
                    setNotes(event.target.value)
                  }
                  placeholder="Additional notes..."
                  rows={3}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                  disabled={transitionMutation.isPending}
                />
              </div>

              {transitionMutation.isError && (
                <p className="text-sm text-destructive">
                  Failed to transition submission status.
                </p>
              )}

              <Button
                onClick={handleTransition}
                disabled={
                  !targetStatus ||
                  transitionMutation.isPending
                }
              >
                {transitionMutation.isPending
                  ? "Transitioning..."
                  : "Transition Status"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Submission Overview</CardTitle>

          <CardDescription>
            Core consultant submission information.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <p className="text-xs text-muted-foreground">
                Job ID
              </p>
              <p className="font-medium">
                {submission.job_id ?? "—"}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Employment
              </p>
              <p className="font-medium">
                {submission.employment_type}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Submission Rate
              </p>
              <p className="font-medium">
                {submission.currency} {submission.rate}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Location
              </p>
              <p className="font-medium">
                {submission.job_location ?? "—"}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Expected Start
              </p>
              <p className="font-medium">
                {formatDate(submission.expected_start_date)}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Submitted
              </p>
              <p className="font-medium">
                {formatDateTime(submission.submitted_at)}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Consultant
              </p>
              <p className="font-medium">
                {submission.consultant
                  ? `${submission.consultant.first_name} ${submission.consultant.last_name}`
                  : "—"}
              </p>
              {submission.consultant?.email && (
                <p className="text-xs text-muted-foreground">
                  {submission.consultant.email}
                </p>
              )}
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Vendor
              </p>
              <p className="font-medium">
                {submission.vendor?.name ??
                  submission.vendor_name_snapshot}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Vendor Contact
              </p>
              <p className="font-medium">
                {submission.vendor_contact?.name ?? "—"}
              </p>
              {submission.vendor_contact && (
                <>
                  {submission.vendor_contact.title && (
                    <p className="text-xs text-muted-foreground">
                      {submission.vendor_contact.title}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {submission.vendor_contact.email}
                  </p>
                </>
              )}
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Client
              </p>
              <p className="font-medium">
                {submission.client?.display_name ??
                  submission.client?.name ??
                  submission.client_name_snapshot}
              </p>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">
                Requirement
              </p>
              <p className="font-medium">
                {submission.requirement_id
                  ? `Requirement #${submission.requirement_id}`
                  : "Not linked"}
              </p>
            </div>
          </div>

          {submission.submission_notes && (
            <div className="mt-6 rounded-lg border p-4">
              <p className="text-xs text-muted-foreground">
                Notes
              </p>

              <p className="mt-1 text-sm">
                {submission.submission_notes}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pipeline History */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline History</CardTitle>

          <CardDescription>
            Complete submission status timeline.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {submission.history.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No pipeline history available.
            </p>
          ) : (
            <div className="space-y-4">
              {submission.history.map((entry) => (
                <div
                  key={entry.id}
                  className="rounded-lg border p-4"
                >
                  <div className="flex items-center justify-between gap-4">
                    <span className="font-medium">
                      {formatStatus(entry.status)}
                    </span>

                    <span className="text-xs text-muted-foreground">
                      {formatDateTime(entry.effective_from)}
                    </span>
                  </div>

                  {entry.reason && (
                    <p className="mt-2 text-sm">
                      {entry.reason}
                    </p>
                  )}

                  {entry.notes && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      {entry.notes}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Interviews */}
      <Card>
        <CardHeader>
          <CardTitle>Interviews</CardTitle>

          <CardDescription>
            Scheduled and completed interview rounds.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {submission.interviews.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No interviews recorded.
            </p>
          ) : (
            <div className="space-y-4">
              {submission.interviews.map((interview) => (
                <div
                  key={interview.public_id}
                  className="rounded-lg border p-4"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">
                        Round {interview.round_number} ·{" "}
                        {formatStatus(interview.interview_type)}
                      </p>

                      <p className="text-sm text-muted-foreground">
                        {interview.interviewer ?? "Interviewer not specified"}
                      </p>
                    </div>

                    <span className="rounded-full border px-2.5 py-1 text-xs font-medium">
                      {formatStatus(interview.status)}
                    </span>
                  </div>

                  <p className="mt-3 text-sm">
                    {formatDateTime(interview.scheduled_at)}
                  </p>

                  <p className="text-xs text-muted-foreground">
                    {interview.timezone}
                  </p>

                  {interview.feedback && (
                    <p className="mt-3 text-sm text-muted-foreground">
                      {interview.feedback}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Client Feedback */}
      <Card>
        <CardHeader>
          <CardTitle>Client Feedback</CardTitle>

          <CardDescription>
            Formal feedback received from the client.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {submission.feedback.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No client feedback recorded.
            </p>
          ) : (
            <div className="space-y-4">
              {submission.feedback.map((feedback) => (
                <div
                  key={feedback.id}
                  className="rounded-lg border p-4"
                >
                  <div className="flex items-center justify-between">
                    <p className="font-medium">
                      {feedback.author}
                    </p>

                    <span className="text-sm">
                      Rating: {feedback.rating}
                    </span>
                  </div>

                  <p className="mt-2 text-sm">
                    {feedback.feedback}
                  </p>

                  <p className="mt-2 text-xs text-muted-foreground">
                    Received {formatDateTime(feedback.received_at)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
            {/* Create Offer */}
      {submission.submission_status === "INTERVIEW_COMPLETED" && (
        <Card>
          <CardHeader>
            <CardTitle>Record Client Offer</CardTitle>

            <CardDescription>
              Record the offer received after the completed interview.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label
                    htmlFor="offered-rate"
                    className="mb-2 block text-sm font-medium"
                  >
                    Offered Rate
                  </label>

                  <input
                    id="offered-rate"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={offeredRate}
                    onChange={(event) =>
                      setOfferedRate(event.target.value)
                    }
                    placeholder="70.00"
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createOfferMutation.isPending}
                  />
                </div>

                <div>
                  <label
                    htmlFor="offer-currency"
                    className="mb-2 block text-sm font-medium"
                  >
                    Currency
                  </label>

                  <select
                    id="offer-currency"
                    value={offerCurrency}
                    onChange={(event) =>
                      setOfferCurrency(event.target.value)
                    }
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createOfferMutation.isPending}
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="CAD">CAD</option>
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="offer-start-date"
                    className="mb-2 block text-sm font-medium"
                  >
                    Start Date
                  </label>

                  <input
                    id="offer-start-date"
                    type="date"
                    value={offerStartDate}
                    onChange={(event) =>
                      setOfferStartDate(event.target.value)
                    }
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createOfferMutation.isPending}
                  />
                </div>

                <div>
                  <label
                    htmlFor="offer-expiration-date"
                    className="mb-2 block text-sm font-medium"
                  >
                    Expiration Date
                  </label>

                  <input
                    id="offer-expiration-date"
                    type="date"
                    value={offerExpirationDate}
                    onChange={(event) =>
                      setOfferExpirationDate(event.target.value)
                    }
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createOfferMutation.isPending}
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="offer-notes"
                  className="mb-2 block text-sm font-medium"
                >
                  Notes
                </label>

                <textarea
                  id="offer-notes"
                  value={offerNotes}
                  onChange={(event) =>
                    setOfferNotes(event.target.value)
                  }
                  placeholder="Offer details or additional notes..."
                  rows={3}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                  disabled={createOfferMutation.isPending}
                />
              </div>

              {createOfferMutation.isError && (
                <p className="text-sm text-destructive">
                  Failed to record the client offer.
                </p>
              )}

              <Button
                onClick={handleCreateOffer}
                disabled={
                  !offeredRate ||
                  !offerStartDate ||
                  createOfferMutation.isPending
                }
              >
                {createOfferMutation.isPending
                  ? "Recording Offer..."
                  : "Record Client Offer"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Offers */}
      <Card>
        <CardHeader>
          <CardTitle>Offers</CardTitle>

          <CardDescription>
            Client offer terms associated with this submission.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {submission.offers.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No offers recorded.
            </p>
          ) : (
            <div className="space-y-4">
              {submission.offers.map((offer) => (
                <div
                  key={offer.public_id}
                  className="rounded-lg border p-4"
                >
                  <div className="flex items-center justify-between">
                    <p className="font-medium">
                      {offer.currency} {offer.offered_rate}
                    </p>

                    <span className="rounded-full border px-2.5 py-1 text-xs font-medium">
                      {formatStatus(offer.offer_status)}
                    </span>
                  </div>

                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div>
                      <p className="text-xs text-muted-foreground">
                        Start Date
                      </p>
                      <p className="text-sm">
                        {formatDate(offer.start_date)}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground">
                        Expiration Date
                      </p>
                      <p className="text-sm">
                        {formatDate(offer.expiration_date)}
                      </p>
                    </div>
                  </div>

                  {offer.notes && (
                    <p className="mt-3 text-sm text-muted-foreground">
                      {offer.notes}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

            {/* Create Placement */}
      {submission.submission_status === "OFFER_ACCEPTED" && (
        <Card>
          <CardHeader>
            <CardTitle>Create Placement</CardTitle>

            <CardDescription>
              Record the final placement and billing information.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label
                    htmlFor="placement-started-on"
                    className="mb-2 block text-sm font-medium"
                  >
                    Started On
                  </label>

                  <input
                    id="placement-started-on"
                    type="date"
                    value={placementStartedOn}
                    onChange={(event) =>
                      setPlacementStartedOn(event.target.value)
                    }
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createPlacementMutation.isPending}
                  />
                </div>

                <div>
                  <label
                    htmlFor="placement-ended-on"
                    className="mb-2 block text-sm font-medium"
                  >
                    Ended On
                  </label>

                  <input
                    id="placement-ended-on"
                    type="date"
                    value={placementEndedOn}
                    onChange={(event) =>
                      setPlacementEndedOn(event.target.value)
                    }
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createPlacementMutation.isPending}
                  />
                </div>

                <div>
                  <label
                    htmlFor="placement-billing-rate"
                    className="mb-2 block text-sm font-medium"
                  >
                    Billing Rate
                  </label>

                  <input
                    id="placement-billing-rate"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={placementBillingRate}
                    onChange={(event) =>
                      setPlacementBillingRate(event.target.value)
                    }
                    placeholder="80.00"
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createPlacementMutation.isPending}
                  />
                </div>

                <div>
                  <label
                    htmlFor="placement-pay-rate"
                    className="mb-2 block text-sm font-medium"
                  >
                    Pay Rate
                  </label>

                  <input
                    id="placement-pay-rate"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={placementPayRate}
                    onChange={(event) =>
                      setPlacementPayRate(event.target.value)
                    }
                    placeholder="65.00"
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2"
                    disabled={createPlacementMutation.isPending}
                  />
                </div>
              </div>

              {createPlacementMutation.isError && (
                <p className="text-sm text-destructive">
                  Failed to create placement.
                </p>
              )}

              <Button
                onClick={handleCreatePlacement}
                disabled={
                  !placementStartedOn ||
                  !placementBillingRate ||
                  !placementPayRate ||
                  createPlacementMutation.isPending
                }
              >
                {createPlacementMutation.isPending
                  ? "Creating Placement..."
                  : "Create Placement"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Placements */}
      <Card>
        <CardHeader>
          <CardTitle>Placements</CardTitle>

          <CardDescription>
            Final placement and billing information.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {submission.placements.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No placements recorded.
            </p>
          ) : (
            <div className="space-y-4">
              {submission.placements.map((placement) => (
                <div
                  key={placement.public_id}
                  className="rounded-lg border p-4"
                >
                  <div className="flex items-center justify-between">
                    <p className="font-medium">
                      Active Client Placement
                    </p>

                    <span className="rounded-full border px-2.5 py-1 text-xs font-medium">
                      {formatStatus(placement.placement_status)}
                    </span>
                  </div>

                  <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    <div>
                      <p className="text-xs text-muted-foreground">
                        Start
                      </p>
                      <p className="text-sm">
                        {formatDate(placement.started_on)}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground">
                        End
                      </p>
                      <p className="text-sm">
                        {formatDate(placement.ended_on)}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground">
                        Billing Rate
                      </p>
                      <p className="text-sm">
                        {placement.billing_rate}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground">
                        Pay Rate
                      </p>
                      <p className="text-sm">
                        {placement.pay_rate}
                      </p>
                    </div>
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