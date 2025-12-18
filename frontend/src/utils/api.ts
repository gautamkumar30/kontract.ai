import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Contract {
  id: string;
  vendor: string;
  contract_type: string;
  created_at: string;
  updated_at: string;
}

export interface Version {
  id: string;
  contract_id: string;
  version_number: number;
  source_type: string;
  source_url?: string;
  created_at: string;
}

export interface Change {
  id: string;
  contract_id: string;
  change_type: string;
  similarity_score?: number;
  risk_level?: string;
  risk_score?: number;
  explanation?: string;
  detected_at: string;
}

// API Functions
export const api = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Contracts
  getContracts: async (): Promise<Contract[]> => {
    const response = await apiClient.get('/api/contracts');
    return response.data;
  },

  getContract: async (id: string): Promise<Contract> => {
    const response = await apiClient.get(`/api/contracts/${id}`);
    return response.data;
  },

  createContract: async (data: {
    vendor: string;
    contract_type: string;
  }): Promise<Contract> => {
    const response = await apiClient.post('/api/contracts', data);
    return response.data;
  },

  // Versions
  getVersions: async (contractId: string): Promise<Version[]> => {
    const response = await apiClient.get(`/api/contracts/${contractId}/versions`);
    return response.data;
  },

  // Changes
  getChanges: async (contractId: string): Promise<Change[]> => {
    const response = await apiClient.get(`/api/contracts/${contractId}/changes`);
    return response.data;
  },

  // Upload
  uploadContract: async (formData: FormData) => {
    const response = await apiClient.post('/api/contracts/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default apiClient;
