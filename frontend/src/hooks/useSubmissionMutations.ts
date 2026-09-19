import { useMutation, useQueryClient } from "@tanstack/react-query";

import submissionService from "@/services/submission.service";

import type {
  CreateSubmissionRequest,
  InterviewCreateRequest,
  OfferCreateRequest,
  PlacementCreateRequest,
  SubmissionTransitionRequest,
} from "@/features/submissions/types";

export function useCreateSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateSubmissionRequest) =>
      submissionService.create(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["submissions"],
      });
    },
  });
}


export function useTransitionSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      publicId,
      payload,
    }: {
      publicId: string;
      payload: SubmissionTransitionRequest;
    }) =>
      submissionService.transition(
        publicId,
        payload
      ),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["submissions"],
      });

      queryClient.invalidateQueries({
        queryKey: ["submission", variables.publicId],
      });
    },
  });
}


export function useScheduleInterview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      publicId,
      payload,
    }: {
      publicId: string;
      payload: InterviewCreateRequest;
    }) =>
      submissionService.scheduleInterview(
        publicId,
        payload
      ),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["submissions"],
      });

      queryClient.invalidateQueries({
        queryKey: ["submission", variables.publicId],
      });
    },
  });
}


export function useCreateOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      publicId,
      payload,
    }: {
      publicId: string;
      payload: OfferCreateRequest;
    }) =>
      submissionService.createOffer(
        publicId,
        payload
      ),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["submissions"],
      });

      queryClient.invalidateQueries({
        queryKey: ["submission", variables.publicId],
      });
    },
  });
}


export function useCreatePlacement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      publicId,
      payload,
    }: {
      publicId: string;
      payload: PlacementCreateRequest;
    }) =>
      submissionService.createPlacement(
        publicId,
        payload
      ),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["submissions"],
      });

      queryClient.invalidateQueries({
        queryKey: ["submission", variables.publicId],
      });
    },
  });
}