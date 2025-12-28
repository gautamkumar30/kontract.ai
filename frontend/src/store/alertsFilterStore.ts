import { create } from 'zustand'
import type { AlertStatus } from '@/types/api'

interface AlertsFilterState {
  status: AlertStatus | 'all'
  alertType: 'all' | 'email' | 'slack' | 'dashboard'
  setStatus: (status: AlertStatus | 'all') => void
  setAlertType: (type: 'all' | 'email' | 'slack' | 'dashboard') => void
  resetFilters: () => void
}

export const useAlertsFilter = create<AlertsFilterState>((set) => ({
  status: 'all',
  alertType: 'all',
  setStatus: (status) => set({ status }),
  setAlertType: (alertType) => set({ alertType }),
  resetFilters: () => set({ status: 'all', alertType: 'all' }),
}))
