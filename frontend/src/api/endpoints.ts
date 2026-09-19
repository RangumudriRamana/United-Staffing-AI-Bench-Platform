export const ENDPOINTS = {
  AUTH: {
  LOGIN: "/auth/login",
  REGISTER: "/auth/register",
  ME: "/auth/me",
  },

  CONSULTANTS: "/consultants",

  REQUIREMENTS: "/requirements",

  VENDORS: "/vendors",

  SUBMISSIONS: "/submissions",

  AI: {
    MATCH: "/ai/match",
    HISTORY: "/ai/history",
    BATCH: "/ai/batch-match",
  },

  ANALYTICS: {
    EXECUTIVE_DASHBOARD: "/dashboard/executive",
    RECRUITER_DASHBOARD: "/dashboard/recruiter",
    VENDOR_ANALYTICS: "/dashboard/analytics/vendors",
  },
} as const;