'use client'

import { mockAlerts } from '@/utils/mockData'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'

export default function AlertsPage() {
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all')

  const filteredAlerts = mockAlerts.filter(alert => {
    if (filter === 'all') return true
    return alert.status === filter
  })

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-rose-50 text-rose-700 border-rose-200'
      case 'high': return 'bg-orange-50 text-orange-700 border-orange-200'
      case 'medium': return 'bg-amber-50 text-amber-700 border-amber-200'
      default: return 'bg-slate-50 text-slate-700 border-slate-200'
    }
  }

  const getRiskIcon = (level: string) => {
    if (level === 'critical') {
      return (
        <svg className="h-6 w-6 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      )
    }
    return (
      <svg className="h-6 w-6 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Alert Center</h1>
          <p className="mt-2 text-base text-slate-600">Stay informed about critical contract changes</p>
        </div>
        <button className="inline-flex items-center px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
          <svg className="-ml-0.5 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          Mark All as Read
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Total Alerts</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">{mockAlerts.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Unread</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockAlerts.filter(a => a.status === 'unread').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-indigo-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Critical</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockAlerts.filter(a => a.risk_level === 'critical').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-rose-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs & Alerts */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="border-b border-slate-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            <button
              onClick={() => setFilter('all')}
              className={`${
                filter === 'all'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
            >
              All Alerts
              <span className={`${filter === 'all' ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-600'} ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium`}>
                {mockAlerts.length}
              </span>
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`${
                filter === 'unread'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
            >
              Unread
              <span className={`${filter === 'unread' ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-600'} ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium`}>
                {mockAlerts.filter(a => a.status === 'unread').length}
              </span>
            </button>
            <button
              onClick={() => setFilter('read')}
              className={`${
                filter === 'read'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
            >
              Read
              <span className={`${filter === 'read' ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-600'} ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium`}>
                {mockAlerts.filter(a => a.status === 'read').length}
              </span>
            </button>
          </nav>
        </div>

        {/* Alerts List */}
        <div className="divide-y divide-slate-200">
          {filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-6 hover:bg-slate-50 transition-colors ${alert.status === 'unread' ? 'bg-blue-50/30' : ''}`}
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  {getRiskIcon(alert.risk_level)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-base font-semibold text-slate-900">{alert.title}</h3>
                      {alert.status === 'unread' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-indigo-100 text-indigo-700 border border-indigo-200">
                          New
                        </span>
                      )}
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getRiskColor(alert.risk_level)}`}>
                      {alert.risk_level.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mb-3">{alert.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-slate-500 mb-4">
                    <span className="flex items-center">
                      <svg className="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      {alert.vendor}
                    </span>
                    <span className="flex items-center">
                      <svg className="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                    </span>
                  </div>
                  <div className="flex space-x-3">
                    <button className="inline-flex items-center px-3 py-1.5 border border-slate-300 text-xs font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 transition-colors">
                      View Contract
                    </button>
                    <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-lg text-indigo-700 bg-indigo-100 hover:bg-indigo-200 transition-colors">
                      View Changes
                    </button>
                    {alert.status === 'unread' && (
                      <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-lg text-slate-700 hover:bg-slate-100 transition-colors">
                        Mark as Read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredAlerts.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-slate-900">No alerts</h3>
            <p className="mt-1 text-sm text-slate-500">You're all caught up!</p>
          </div>
        )}
      </div>
    </div>
  )
}
