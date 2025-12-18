// API Types and Interfaces

// Contract types
export interface Contract {
  id: string
  vendor: string
  contract_type: 'tos' | 'privacy' | 'sla' | 'msa' | 'dpa' | 'other'
  created_at: string
  updated_at: string
}

export interface ContractCreate {
  vendor: string
  contract_type: string
  source_url?: string
}

export interface ContractListParams {
  vendor?: string
  contract_type?: string
  limit?: number
  offset?: number
}

// Version types
export interface Version {
  id: string
  contract_id: string
  version_number: number
  source_type: 'pdf' | 'url' | 'text'
  source_url?: string
  raw_text: string
  created_at: string
}

export interface VersionSummary {
  id: string
  version_number: number
  created_at: string
}

export interface VersionComparison {
  contract_id: string
  from_version: VersionSummary
  to_version: VersionSummary
  changes: Change[]
  statistics: ComparisonStats
}

export interface ComparisonStats {
  total_changes: number
  high_risk_count: number
  changes_by_type: {
    added: number
    removed: number
    modified: number
    rewritten: number
  }
}

// Clause types
export interface Clause {
  id: string
  version_id: string
  clause_number: number
  category?: string
  heading?: string
  text: string
  position_start?: number
  position_end?: number
  created_at: string
}

export interface ClauseDetail extends Clause {
  fingerprint?: Fingerprint
}

export interface Fingerprint {
  id: string
  text_hash: string
  simhash: string
  keywords: Record<string, number>
  created_at: string
}

// Change types
export interface Change {
  id: string
  contract_id: string
  from_version_id: string
  to_version_id: string
  clause_id: string
  change_type: 'added' | 'removed' | 'modified' | 'rewritten'
  similarity_score?: number
  risk_level?: 'low' | 'medium' | 'high' | 'critical'
  risk_score?: number
  explanation?: string
  detected_at: string
}

export interface ChangeListParams {
  contract_id?: string
  risk_level?: string
  limit?: number
  sort?: string
}

// Alert types
export interface Alert {
  id: string
  change_id: string
  alert_type: 'email' | 'slack' | 'dashboard'
  status: 'pending' | 'sent' | 'acknowledged' | 'resolved'
  created_at: string
  sent_at?: string
}

export type AlertStatus = Alert['status']

export interface AlertListParams {
  status?: AlertStatus
  limit?: number
}

// Stats types
export interface DashboardStats {
  total_contracts: number
  high_risk_changes: number
  monitored_vendors: number
  pending_alerts: number
}

// API Error type
export interface ApiError {
  detail: string
  status?: number
}
