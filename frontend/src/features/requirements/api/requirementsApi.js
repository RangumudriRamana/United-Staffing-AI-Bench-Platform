import * as ApiServices from "@/api/generated";
export const requirementsApi = {
    list: (params) => ApiServices.YourServiceName.getRequirements({ query: params }),
    getById: (id) => ApiServices.YourServiceName.getRequirementById({ path: { id } }),
    create: (data) => ApiServices.YourServiceName.createRequirement({ body: data }),
    update: (id, data) => ApiServices.YourServiceName.updateRequirement({ path: { id }, body: data }),
    delete: (id) => ApiServices.YourServiceName.deleteRequirement({ path: { id } }),
};
