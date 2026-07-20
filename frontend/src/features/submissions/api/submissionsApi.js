import * as ApiServices from "@/api/generated";
export const submissionsApi = {
    list: (params) => ApiServices.YourServiceName.getSubmissions({ query: params }),
    getById: (id) => ApiServices.YourServiceName.getSubmissionById({ path: { id } }),
    create: (data) => ApiServices.YourServiceName.createSubmission({ body: data }),
    update: (id, data) => ApiServices.YourServiceName.updateSubmission({ path: { id }, body: data }),
    delete: (id) => ApiServices.YourServiceName.deleteSubmission({ path: { id } }),
};
