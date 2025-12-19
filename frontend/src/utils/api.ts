import type {
  Contract,
  ContractCreate,
  ContractListParams,
  Version,
  VersionComparison,
  Clause,
  ClauseDetail,
  Change,
  ChangeListParams,
  Alert,
  AlertStatus,
  AlertListParams,
  DashboardStats,
  ApiError,
} from '@/types/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Base fetch wrapper with error handling
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit & { params?: Record<string, any> }
): Promise<T> {
  const { params, ...fetchOptions} = options || {}
  
  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`
  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions?.headers,
    },
    ...fetchOptions,
  })
  
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      detail: response.statusText,
      status: response.status,
    }))
    throw new Error(error.detail || 'API request failed')
  }
  
  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T
  }
  
  return response.json()
}

// Contracts API
export const contractsApi = {
  list: (params?: ContractListParams) =>
    apiFetch<Contract[]>('/api/contracts', { params }),
  
  get: (id: string) =>
    apiFetch<Contract>(`/api/contracts/${id}`),
  
  create: (data: ContractCreate) =>
    apiFetch<Contract>('/api/contracts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  upload: async (file: File, vendor: string, contractType: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('vendor', vendor)
    formData.append('contract_type', contractType)
    
    const response = await fetch(`${API_BASE_URL}/api/contracts/upload`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(error.detail)
    }
    
    return response.json()
  },
  
  delete: (id: string) =>
    apiFetch<void>(`/api/contracts/${id}`, { method: 'DELETE' }),
}

// Versions API
export const versionsApi = {
  list: (contractId: string) =>
    apiFetch<Version[]>(`/api/contracts/${contractId}/versions`),
  
  get: (versionId: string) =>
    apiFetch<Version>(`/api/contracts/versions/${versionId}`),
  
  compare: (versionId: string, otherVersionId: string) =>
    apiFetch<VersionComparison>(
      `/api/contracts/versions/${versionId}/compare/${otherVersionId}`
    ),
}

// Clauses API
export const clausesApi = {
  listForVersion: (versionId: string) =>
    apiFetch<Clause[]>(`/api/contracts/versions/${versionId}/clauses`),
  
  get: (clauseId: string) =>
    apiFetch<ClauseDetail>(`/api/contracts/clauses/${clauseId}`),
}

// Changes API
export const changesApi = {
  list: (params?: ChangeListParams) =>
    apiFetch<Change[]>('/api/contracts/changes', { params }),
  
  get: (changeId: string) =>
    apiFetch<Change>(`/api/contracts/changes/${changeId}`),
}

// Alerts API
export const alertsApi = {
  list: (params?: AlertListParams) =>
    apiFetch<Alert[]>('/api/alerts', { params }),
  
  updateStatus: (id: string, status: AlertStatus) =>
    apiFetch<Alert>(`/api/alerts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
}

// Stats API
export const statsApi = {
  get: () =>
    apiFetch<DashboardStats>('/api/stats'),
}

// Analytics API
export const analyticsApi = {
  getTrends: (days?: number) =>
    apiFetch<Array<{ date: string; count: number }>>('/api/analytics/trends', {
      params: days ? { days } : undefined
    }),
  
  getRiskDistribution: () =>
    apiFetch<{ critical: number; high: number; medium: number; low: number }>(
      '/api/analytics/risk-distribution'
    ),
  
  getChangeTypes: () =>
    apiFetch<{ added: number; removed: number; modified: number; rewritten: number }>(
      '/api/analytics/change-types'
    ),
  
  getVendorStats: (limit?: number) =>
    apiFetch<Array<{ vendor: string; changes: number; contracts: number }>>(
      '/api/analytics/vendor-stats',
      { params: limit ? { limit } : undefined }
    ),
}
