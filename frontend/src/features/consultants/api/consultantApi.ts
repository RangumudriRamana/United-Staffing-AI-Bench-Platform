import * as ApiServices from "@/api/generated";
const API_PREFIX = "/api/v1";

if ((ApiServices as any).OpenAPI) {
  (ApiServices as any).OpenAPI.BASE = window.location.origin;
  
  // Attach auth token if available
  const token = localStorage.getItem("auth_token");
  if (token) {
    (ApiServices as any).OpenAPI.TOKEN = token;
  }
}

const getService = () => {
  const keys = Object.keys(ApiServices);
  for (const key of keys) {
    if (['CancelablePromise', 'ApiError', 'OpenAPI'].includes(key)) continue;
    const val = (ApiServices as any)[key];
    if (val && typeof val === "object" && (val.getConsultants || val.createConsultant || val.list)) {
      return val;
    }
    if (typeof val === "function" && val.prototype) {
      try {
        const instance = new val();
        if (instance.getConsultants || instance.createConsultant || instance.list) {
          return instance;
        }
      } catch {}
    }
  }
  return null;
};

const s = getService() as any;

export const consultantApi = {
  list: async (params?: any) => {
    try {
      let res;
      if (s && typeof s.getConsultants === "function") {
        res = await s.getConsultants({ query: params });
      } else if (s && typeof s.list === "function") {
        res = await s.list(params);
      }

      if (res !== undefined && res !== null) {
        if (Array.isArray(res)) return { data: res, total: res.length };
        return {
          data: res?.data ?? res ?? [],
          total: res?.total ?? res?.data?.length ?? (Array.isArray(res) ? res.length : 0),
        };
      }

      const response = await fetch(`${API_PREFIX}/consultants`);
      if (!response.ok) throw new Error('Direct fetch failed');
      const directRes = await response.json();

      const items = Array.isArray(directRes) ? directRes : (directRes?.data ?? []);
      return { data: items, total: items.length };
    } catch (err) {
      console.error("Error fetching consultants:", err);
      return { data: [], total: 0 };
    }
  },

  getById: async (id: string) => {
    try {
      if (!id) return null;
      if (s && typeof s.getConsultantById === "function") {
        return await s.getConsultantById({ path: { id } });
      }
      const response = await fetch(`${API_PREFIX}/consultants/${id}`);
      return response.ok ? await response.json() : null;
    } catch (err) {
      return null;
    }
  },

  create: async (data: any) => {
    try {
      if (s && typeof s.createConsultant === "function") {
        return await s.createConsultant({ body: data });
      }
      const response = await fetch(`${API_PREFIX}/consultants`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem("auth_token") || ''}`
        },
        body: JSON.stringify(data),
      });
      return response.ok ? await response.json() : {};
    } catch (err) {
      throw err;
    }
  },

  update: async (id: string, data: any) => {
    try {
      if (s && typeof s.updateConsultant === "function") {
        return await s.updateConsultant({ path: { id }, body: data });
      }
      const response = await fetch(`${API_PREFIX}/consultants/${id}`, {
        method: 'PATCH', // Fixed: Backend expects PATCH, not PUT
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem("auth_token") || ''}`
        },
        body: JSON.stringify(data),
      });
      return response.ok ? await response.json() : {};
    } catch (err) {
      throw err;
    }
  },

  delete: async (id: string) => {
    try {
      if (s && typeof s.deleteConsultant === "function") {
        return await s.deleteConsultant({ path: { id } });
      }
      const response = await fetch(`${API_PREFIX}/consultants/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem("auth_token") || ''}`
        }
      });
      if (!response.ok) throw new Error('Delete failed');
      // Handle 204 No Content properly without calling .json()
      return response.status === 204 ? undefined : await response.json();
    } catch (err) {
      throw err;
    }
  },
};
