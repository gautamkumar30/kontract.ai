'use client'

import { useQuery } from '@tanstack/react-query'
import { statsApi, changesApi } from '@/utils/api'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'
import AddContractModal from './components/AddContractModal'

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  
  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => statsApi.get()
  })
  
  // Fetch recent changes
  const { data: recentChanges, isLoading: changesLoading } = useQuery({
    queryKey: ['recent-changes'],
    queryFn: () => changesApi.list({ limit: 10, sort: 'detected_at:desc' })
  })
  
  const isLoading = statsLoading || changesLoading

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Dashboard</h1>
          <p className="mt-2 text-base text-slate-600">Monitor contract changes and track risk across your SaaS vendors</p>
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

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Contracts */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 hover:border-indigo-300 transition-all duration-200">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-600">Total Contracts</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.total_contracts || 0}
              </p>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-slate-500">Active tracking</span>
              </div>
            </div>
            <div className="shrink-0">
              <div className="w-12 h-12 bg-indigo-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* High Risk Changes */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 hover:border-rose-300 transition-all duration-200">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-600">High Risk Changes</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.high_risk_changes || 0}
              </p>
              <div className="mt-2">
                {stats && stats.high_risk_changes > 0 ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
                    Needs Review
                  </span>
                ) : (
                  <span className="text-slate-500 text-sm">All clear</span>
                )}
              </div>
            </div>
            <div className="shrink-0">
              <div className="w-12 h-12 bg-rose-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Monitored Vendors */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-300 transition-all duration-200">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-600">Monitored Vendors</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.monitored_vendors || 0}
              </p>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-slate-500">Active tracking</span>
              </div>
            </div>
            <div className="shrink-0">
              <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Pending Alerts */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 hover:border-amber-300 transition-all duration-200">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-600">Pending Alerts</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.pending_alerts || 0}
              </p>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-slate-500">Awaiting action</span>
              </div>
            </div>
            <div className="shrink-0">
              <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-xl font-semibold text-slate-900">Recent Activity</h2>
          <p className="mt-1 text-sm text-slate-500">Latest contract changes and updates</p>
        </div>
        <div className="divide-y divide-slate-200">
          {isLoading ? (
            <div className="p-8 text-center text-slate-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <p className="mt-2">Loading recent activity...</p>
            </div>
          ) : recentChanges && recentChanges.length > 0 ? (
            recentChanges.map((change, idx) => (
              <div key={change.id} className="p-6 hover:bg-slate-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${
                        change.risk_level === 'critical' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                        change.risk_level === 'high' ? 'bg-orange-100 text-orange-800 border border-orange-200' :
                        change.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                        'bg-slate-100 text-slate-800 border border-slate-200'
                      }`}>
                        {change.risk_level?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${
                        change.change_type === 'added' ? 'bg-emerald-100 text-emerald-800' :
                        change.change_type === 'removed' ? 'bg-rose-100 text-rose-800' :
                        change.change_type === 'modified' ? 'bg-blue-100 text-blue-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {change.change_type.toUpperCase()}
                      </span>
                    </div>
                    <p className="mt-2 text-sm font-medium text-slate-900">
                      {change.explanation || `Contract clause was ${change.change_type}`}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {formatDistanceToNow(new Date(change.detected_at), { addSuffix: true })}
                    </p>
                  </div>
                  {change.similarity_score !== undefined && change.similarity_score !== null && (
                    <div className="ml-4 text-right">
                      <p className="text-xs text-slate-500">Similarity</p>
                      <p className="text-sm font-semibold text-slate-900">
                        {(change.similarity_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center">
              <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-slate-900">No recent activity</h3>
              <p className="mt-1 text-sm text-slate-500">Upload a contract to start monitoring changes</p>
            </div>
          )}
        </div>
      </div>

      <AddContractModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  )
}
