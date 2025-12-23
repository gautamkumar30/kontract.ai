'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { alertsApi } from '@/utils/api'
import { formatDistanceToNow } from 'date-fns'
import { useMemo } from 'react'
import { useAlertsFilter } from '@/store/alertsFilterStore'
import type { Alert } from '@/types/api'

export default function AlertsPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  
  // Zustand state
  const { status, alertType, setStatus, setAlertType } = useAlertsFilter()
  
  // Fetch alerts from backend
  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ['alerts', status],
    queryFn: () => alertsApi.list({
      status: status === 'all' ? undefined : status,
      limit: 100
    })
  })
  
  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, newStatus }: { id: string, newStatus: string }) =>
      alertsApi.updateStatus(id, newStatus as any),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    }
  })
  
  // Client-side filter for alert type (backend doesn't support this filter yet)
  const filteredAlerts = useMemo(() => {
    if (!alerts) return []
    if (alertType === 'all') return alerts
    return alerts.filter(a => a.alert_type === alertType)
  }, [alerts, alertType])
  
  // Calculate stats
  const stats = useMemo(() => ({
    total: alerts?.length || 0,
    pending: alerts?.filter(a => a.status === 'pending').length || 0,
    sent: alerts?.filter(a => a.status === 'sent').length || 0,
    failed: alerts?.filter(a => a.status === 'failed').length || 0,
  }), [alerts])
  
  const handleStatusUpdate = (id: string, newStatus: string) => {
    updateStatusMutation.mutate({ id, newStatus })
  }
  
  const handleViewContract = (changeId: string) => {
    // For now, we'll need to fetch the change to get the contract_id
    // In a real app, we'd populate the change relationship in the API
    router.push(`/contracts`) // Fallback to contracts list
  }
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'sent':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200'
      case 'failed':
        return 'bg-rose-100 text-rose-800 border-rose-200'
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200'
    }
  }
  
  const getAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'email':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        )
      case 'slack':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        )
      case 'dashboard':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Alerts</h1>
        <p className="mt-2 text-base text-slate-600">Manage contract change notifications and alerts</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Total Alerts</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats.total}
              </p>
            </div>
            <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Pending</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats.pending}
              </p>
            </div>
            <div className="w-10 h-10 bg-yellow-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Sent</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats.sent}
              </p>
            </div>
            <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Failed</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats.failed}
              </p>
            </div>
            <div className="w-10 h-10 bg-rose-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-slate-700 mb-2">
              Status
            </label>
            <select
              id="status"
              className="block w-full text-gray-700 px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="sent">Sent</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <div>
            <label htmlFor="type" className="block text-sm font-medium text-slate-700 mb-2">
              Alert Type
            </label>
            <select
              id="type"
              className="block w-full text-gray-700 px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              value={alertType}
              onChange={(e) => setAlertType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="email">Email</option>
              <option value="slack">Slack</option>
              <option value="dashboard">Dashboard</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-rose-600 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p className="text-sm text-rose-800">Failed to load alerts. Please try again.</p>
          </div>
        </div>
      )}

      {/* Alerts List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p className="mt-4 text-slate-600">Loading alerts...</p>
          </div>
        ) : filteredAlerts.length > 0 ? (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  {/* Icon */}
                  <div className="shrink-0 w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                    {getAlertTypeIcon(alert.alert_type)}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-semibold text-slate-900 capitalize">
                        {alert.alert_type} Alert
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getStatusBadge(alert.status)}`}>
                        {alert.status}
                      </span>
                    </div>
                    
                    <p className="text-sm text-slate-600 mb-2">
                      Change ID: {alert.change_id.substring(0, 8)}...
                    </p>
                    
                    {alert.recipient && (
                      <p className="text-xs text-slate-500 mb-2">
                        Recipient: {alert.recipient}
                      </p>
                    )}
                    
                    <p className="text-xs text-slate-500">
                      Created {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                      {alert.sent_at && ` • Sent ${formatDistanceToNow(new Date(alert.sent_at), { addSuffix: true })}`}
                    </p>
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4">
                  {alert.status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleStatusUpdate(alert.id, 'sent')}
                        disabled={updateStatusMutation.isPending}
                        className="px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors disabled:opacity-50"
                      >
                        Mark as Sent
                      </button>
                      <button
                        onClick={() => handleStatusUpdate(alert.id, 'failed')}
                        disabled={updateStatusMutation.isPending}
                        className="px-3 py-1.5 text-xs font-medium text-rose-700 bg-rose-50 border border-rose-200 rounded-lg hover:bg-rose-100 transition-colors disabled:opacity-50"
                      >
                        Mark as Failed
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => handleViewContract(alert.change_id)}
                    className="px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-slate-900">No alerts found</h3>
            <p className="mt-1 text-sm text-slate-500">
              {status !== 'all' || alertType !== 'all'
                ? 'Try adjusting your filter criteria'
                : 'No alerts have been created yet'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
