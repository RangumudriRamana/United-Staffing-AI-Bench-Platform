import { z } from "zod";

export const consultantSchema = z.object({
  first_name: z.string().min(2),

  last_name: z.string().min(2),

  email: z.string().email(),

  phone: z.string().min(10),

  current_title: z.string().min(2),

  total_experience_years: z.number().min(0),

  current_location: z.string().min(2),

  preferred_location: z.string().min(2),

  relocation_available: z.boolean(),

  remote_preference: z.string(),

  visa_status: z.string(),

  visa_expiration: z.string(),

  work_authorized: z.boolean(),

  availability_date: z.string(),

  marketing_status: z.string(),

  rate_type: z.string(),

  expected_rate: z.number().min(0),
});

export type ConsultantFormData =
  z.infer<typeof consultantSchema>;