import { create } from 'zustand'

interface AlertsFilterState {
  status: string  // 'all' | 'pending' | 'sent' | 'failed'
  alertType: string  // 'all' | 'email' | 'slack' | 'dashboard'
  setStatus: (status: string) => void
  setAlertType: (type: string) => void
  resetFilters: () => void
}

export const useAlertsFilter = create<AlertsFilterState>((set) => ({
  status: 'all',
  alertType: 'all',
  setStatus: (status) => set({ status }),
  setAlertType: (alertType) => set({ alertType }),
  resetFilters: () => set({ status: 'all', alertType: 'all' }),
}))
