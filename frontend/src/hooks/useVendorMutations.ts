import { useMutation, useQueryClient } from "@tanstack/react-query";

import vendorService, {
  type CreateClientPayload,
  type CreateVendorPayload,
  type UpdateClientPayload,
  type UpdateVendorPayload,
} from "@/services/vendor.service";

export function useCreateVendor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateVendorPayload) =>
      vendorService.create(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["vendors"],
      });
    },
  });
}

export function useUpdateVendor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      publicId,
      payload,
    }: {
      publicId: string;
      payload: UpdateVendorPayload;
    }) => vendorService.update(publicId, payload),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["vendors"],
      });

      queryClient.invalidateQueries({
        queryKey: ["vendor", variables.publicId],
      });
    },
  });
}

export function useArchiveVendor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (publicId: string) =>
      vendorService.archive(publicId),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["vendors"],
      });
    },
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateClientPayload) =>
      vendorService.createClient(payload),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["clients", variables.vendor_public_id],
      });

      queryClient.invalidateQueries({
        queryKey: ["vendors"],
      });
    },
  });
}

export function useUpdateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      publicId,
      payload,
    }: {
      publicId: string;
      payload: UpdateClientPayload;
    }) => vendorService.updateClient(publicId, payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["clients"],
      });

      queryClient.invalidateQueries({
        queryKey: ["vendors"],
      });
    },
  });
}

export function useArchiveClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (publicId: string) =>
      vendorService.archiveClient(publicId),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["clients"],
      });

      queryClient.invalidateQueries({
        queryKey: ["vendors"],
      });
    },
  });
}