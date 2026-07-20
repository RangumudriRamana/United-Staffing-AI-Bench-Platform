import * as ApiServices from "@/api/generated";

export const submissionsApi = {
  list: (params?: any) => (ApiServices as any).YourServiceName.getSubmissions({ query: params }),
  getById: (id: string) => (ApiServices as any).YourServiceName.getSubmissionById({ path: { id } }),
  create: (data: any) => (ApiServices as any).YourServiceName.createSubmission({ body: data }),
  update: (id: string, data: any) => (ApiServices as any).YourServiceName.updateSubmission({ path: { id }, body: data }),
  delete: (id: string) => (ApiServices as any).YourServiceName.deleteSubmission({ path: { id } }),
};