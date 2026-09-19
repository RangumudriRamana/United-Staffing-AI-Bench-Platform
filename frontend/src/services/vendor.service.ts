import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";
import type {
  Client,
  Vendor,
  VendorsResponse,
} from "@/features/vendors/types";

export interface CreateVendorPayload {
  name: string;
  vendor_type?: Vendor["vendor_type"];
  tier?: Vendor["tier"];
  status?: Vendor["status"];
  website?: string | null;
  preferred?: boolean;
  notes?: string | null;
  contacts?: Array<{
    name: string;
    title?: string | null;
    email: string;
    phone?: string | null;
    linkedin?: string | null;
    timezone?: string;
    preferred_contact?: boolean;
    is_active?: boolean;
  }>;
}

export interface UpdateVendorPayload {
  name?: string;
  vendor_type?: Vendor["vendor_type"];
  tier?: Vendor["tier"];
  status?: Vendor["status"];
  website?: string | null;
  preferred?: boolean;
  notes?: string | null;
}

export interface CreateClientPayload {
  vendor_public_id: string;
  name: string;
  display_name?: string | null;
  industry?: string | null;
  website?: string | null;
  primary_location?: string | null;
  timezone?: string;
  notes?: string | null;
  status?: Client["status"];
  preferred?: boolean;
}

export interface UpdateClientPayload {
  name?: string;
  display_name?: string | null;
  industry?: string | null;
  website?: string | null;
  primary_location?: string | null;
  timezone?: string;
  notes?: string | null;
  status?: Client["status"];
  preferred?: boolean;
}

class VendorService {
  async getAll(): Promise<VendorsResponse> {
    const response = await api.get(ENDPOINTS.VENDORS);
    return response.data;
  }

  async getById(publicId: string): Promise<Vendor> {
    const response = await api.get(
      `${ENDPOINTS.VENDORS}/${publicId}`
    );

    return response.data;
  }

  async create(payload: CreateVendorPayload): Promise<Vendor> {
    const response = await api.post(
      ENDPOINTS.VENDORS,
      payload
    );

    return response.data;
  }

  async update(
    publicId: string,
    payload: UpdateVendorPayload
  ): Promise<Vendor> {
    const response = await api.patch(
      `${ENDPOINTS.VENDORS}/${publicId}`,
      payload
    );

    return response.data;
  }

  async archive(publicId: string): Promise<void> {
    await api.delete(
      `${ENDPOINTS.VENDORS}/${publicId}`
    );
  }

  async getClients(
    vendorPublicId: string
  ): Promise<Client[]> {
    const response = await api.get(
      `${ENDPOINTS.VENDORS}/clients`,
      {
        params: {
          vendor_public_id: vendorPublicId,
        },
      }
    );

    return response.data.data;
  }

  async getClientById(publicId: string): Promise<Client> {
    const response = await api.get(
      `${ENDPOINTS.VENDORS}/clients/${publicId}`
    );

    return response.data;
  }

  async createClient(
    payload: CreateClientPayload
  ): Promise<Client> {
    const response = await api.post(
      `${ENDPOINTS.VENDORS}/clients`,
      payload
    );

    return response.data;
  }

  async updateClient(
    publicId: string,
    payload: UpdateClientPayload
  ): Promise<Client> {
    const response = await api.patch(
      `${ENDPOINTS.VENDORS}/clients/${publicId}`,
      payload
    );

    return response.data;
  }

  async archiveClient(publicId: string): Promise<void> {
    await api.delete(
      `${ENDPOINTS.VENDORS}/clients/${publicId}`
    );
  }
}

export default new VendorService();