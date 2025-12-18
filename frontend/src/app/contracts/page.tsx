'use client'

import { mockContracts, mockChanges } from '@/utils/mockData'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'
import AddContractModal from '../components/AddContractModal'

export default function ContractsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedVendor, setSelectedVendor] = useState('all')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedContract, setSelectedContract] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)


  const filteredContracts = mockContracts.filter(contract => {
    const matchesSearch = contract.vendor.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesVendor = selectedVendor === 'all' || contract.vendor === selectedVendor
    const matchesType = selectedType === 'all' || contract.contract_type === selectedType
    return matchesSearch && matchesVendor && matchesType
  })

  const vendors = Array.from(new Set(mockContracts.map(c => c.vendor)))
  const types = Array.from(new Set(mockContracts.map(c => c.contract_type)))

  const getRiskBadge = (count: number) => {
    if (count >= 3) return 'bg-rose-50 text-rose-700 border-rose-200'
    if (count >= 1) return 'bg-amber-50 text-amber-700 border-amber-200'
    return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Contracts</h1>
          <p className="mt-2 text-base text-slate-600">Manage and monitor all your SaaS contract agreements</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <svg className="-ml-0.5 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Add Contract
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Total Contracts</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">{mockContracts.length}</p>
            </div>
            <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Active Monitoring</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">{mockContracts.filter(c => c.status === 'active').length}</p>
            </div>
            <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">High Risk Items</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {mockContracts.reduce((acc, c) => acc + c.high_risk_changes, 0)}
              </p>
            </div>
            <div className="w-10 h-10 bg-rose-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Total Versions</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {mockContracts.reduce((acc, c) => acc + c.versions_count, 0)}
              </p>
            </div>
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-slate-700 mb-2">
              Search
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                id="search"
                className="block w-full text-gray-700 pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Search by vendor..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label htmlFor="vendor" className="block text-sm font-medium text-slate-700 mb-2">
              Vendor
            </label>
            <select
              id="vendor"
              className="block w-full text-gray-700 px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              value={selectedVendor}
              onChange={(e) => setSelectedVendor(e.target.value)}
            >
              <option value="all">All Vendors</option>
              {vendors.map(vendor => (
                <option key={vendor} value={vendor}>{vendor}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="type" className="block text-sm font-medium text-slate-700 mb-2">
              Contract Type
            </label>
            <select
              id="type"
              className="block w-full text-gray-700 px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <option value="all">All Types</option>
              {types.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Contracts Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Contract Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Versions
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Risk Changes
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Last Updated
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {filteredContracts.map((contract) => (
                <tr
                  key={contract.id}
                  onClick={() => setSelectedContract(contract.id)}
                  className="hover:bg-slate-50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <span className="text-sm font-semibold text-indigo-700">
                          {contract.vendor.substring(0, 2).toUpperCase()}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-slate-900">{contract.vendor}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-slate-600">{contract.contract_type}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-slate-900 font-medium">{contract.versions_count}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getRiskBadge(contract.high_risk_changes)}`}>
                      {contract.high_risk_changes} high risk
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {formatDistanceToNow(new Date(contract.updated_at), { addSuffix: true })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {contract.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredContracts.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-slate-900">No contracts found</h3>
            <p className="mt-1 text-sm text-slate-500">Try adjusting your search or filter criteria</p>
          </div>
        )}
      </div>

      {/* Contract Detail Modal */}
      {selectedContract && (
        <div className="fixed inset-0 bg-slate-900 bg-opacity-50 overflow-y-auto h-full w-full z-50" onClick={() => setSelectedContract(null)}>
          <div className="relative top-20 mx-auto p-5 w-full max-w-4xl" onClick={(e) => e.stopPropagation()}>
            <div className="bg-white rounded-xl border border-slate-200 shadow-xl">
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200">
                <div>
                  <h3 className="text-2xl font-bold text-slate-900">
                    {mockContracts.find(c => c.id === selectedContract)?.vendor}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    {mockContracts.find(c => c.id === selectedContract)?.contract_type}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedContract(null)}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Modal Body */}
              <div className="px-6 py-5 max-h-[600px] overflow-y-auto">
                <h4 className="text-lg font-semibold text-slate-900 mb-4">Detected Changes</h4>
                <div className="space-y-4">
                  {(mockChanges[selectedContract as keyof typeof mockChanges] || []).map((change) => (
                    <div key={change.id} className="bg-slate-50 rounded-lg border border-slate-200 p-5">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${
                            change.change_type === 'added' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                            change.change_type === 'removed' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                            change.change_type === 'modified' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                            'bg-purple-50 text-purple-700 border-purple-200'
                          }`}>
                            {change.change_type.toUpperCase()}
                          </span>
                          <span className="text-xs font-medium text-slate-600">
                            {change.clause_category.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${
                            change.risk_level === 'critical' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                            change.risk_level === 'high' ? 'bg-orange-50 text-orange-700 border-orange-200' :
                            change.risk_level === 'medium' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                            'bg-emerald-50 text-emerald-700 border-emerald-200'
                          }`}>
                            {change.risk_level.toUpperCase()}
                          </span>
                          <span className="text-sm font-bold text-slate-900">{change.risk_score}/100</span>
                        </div>
                      </div>

                      {change.old_text && (
                        <div className="mb-3">
                          <p className="text-xs font-semibold text-slate-700 mb-1">Before:</p>
                          <p className="text-sm text-slate-600 bg-white rounded-lg p-3 border border-slate-200">{change.old_text}</p>
                        </div>
                      )}

                      {change.new_text && (
                        <div className="mb-3">
                          <p className="text-xs font-semibold text-slate-700 mb-1">After:</p>
                          <p className="text-sm text-slate-600 bg-white rounded-lg p-3 border border-slate-200">{change.new_text}</p>
                        </div>
                      )}

                      <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
                        <p className="text-xs font-semibold text-indigo-900 mb-1">AI Analysis:</p>
                        <p className="text-sm text-indigo-800">{change.explanation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Modal Footer */}
              <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 rounded-b-xl">
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setSelectedContract(null)}
                    className="px-4 py-2 border border-slate-300 text-sm font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 transition-colors"
                  >
                    Close
                  </button>
                  <button className="px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 transition-colors">
                    Export Report
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Contract Modal */}
      <AddContractModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={() => {
          // In a real app, this would refresh the contract list
          console.log('Contract added successfully!')
        }}
      />
    </div>
  )
}
