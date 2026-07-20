import * as ApiServices from "@/api/generated";

export const requirementsApi = {
  list: (params?: any) => (ApiServices as any).YourServiceName.getRequirements({ query: params }),
  getById: (id: string) => (ApiServices as any).YourServiceName.getRequirementById({ path: { id } }),
  create: (data: any) => (ApiServices as any).YourServiceName.createRequirement({ body: data }),
  update: (id: string, data: any) => (ApiServices as any).YourServiceName.updateRequirement({ path: { id }, body: data }),
  delete: (id: string) => (ApiServices as any).YourServiceName.deleteRequirement({ path: { id } }),
};