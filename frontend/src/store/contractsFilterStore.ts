import { create } from 'zustand'

interface ContractsFilterState {
  searchTerm: string
  contractType: string
  setSearchTerm: (term: string) => void
  setContractType: (type: string) => void
  resetFilters: () => void
}

export const useContractsFilter = create<ContractsFilterState>((set) => ({
  searchTerm: '',
  contractType: 'all',
  setSearchTerm: (term) => set({ searchTerm: term }),
  setContractType: (type) => set({ contractType: type }),
  resetFilters: () => set({ searchTerm: '', contractType: 'all' }),
}))
