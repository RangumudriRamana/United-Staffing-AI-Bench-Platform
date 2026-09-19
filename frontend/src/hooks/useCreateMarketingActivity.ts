import { useMutation, useQueryClient } from "@tanstack/react-query";
import consultantService from "@/services/consultant.service";

export interface CreateMarketingActivityPayload {
  consultant_public_id: string;
  vendor_public_id: string;
  vendor_contact_public_id?: string | null;
  client_public_id?: string | null;
  activity_type: string;
  channel: string;
  outcome: string;
  subject?: string | null;
  notes?: string | null;
  follow_up_required?: boolean;
  occurred_at?: string | null;
}

export function useCreateMarketingActivity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateMarketingActivityPayload) =>
      consultantService.createMarketingActivity(payload),

    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({
        queryKey: ["marketing-activities", variables.consultant_public_id],
      });
    },
  });
}