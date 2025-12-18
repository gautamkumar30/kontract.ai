'use client'

import { mockTimelineEvents, mockRecentActivity } from '@/utils/mockData'
import { formatDistanceToNow } from 'date-fns'

export default function TimelinePage() {
  const getEventColor = (type: string) => {
    switch (type) {
      case 'critical': return 'bg-rose-500'
      case 'high': return 'bg-orange-500'
      case 'medium': return 'bg-amber-500'
      case 'low': return 'bg-emerald-500'
      default: return 'bg-slate-500'
    }
  }

  const getEventBgColor = (type: string) => {
    switch (type) {
      case 'critical': return 'bg-rose-50'
      case 'high': return 'bg-orange-50'
      case 'medium': return 'bg-amber-50'
      case 'low': return 'bg-emerald-50'
      default: return 'bg-slate-50'
    }
  }

  const getEventBorderColor = (type: string) => {
    switch (type) {
      case 'critical': return 'border-rose-200'
      case 'high': return 'border-orange-200'
      case 'medium': return 'border-amber-200'
      case 'low': return 'border-emerald-200'
      default: return 'border-slate-200'
    }
  }

  const getEventIcon = (type: string) => {
    if (type === 'critical') {
      return (
        <svg className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      )
    } else if (type === 'high') {
      return (
        <svg className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      )
    }
    return (
      <svg className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Change Timeline</h1>
          <p className="mt-2 text-base text-slate-600">Chronological view of all contract changes and events</p>
        </div>
        <div className="flex space-x-3">
          <select className="px-4 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors">
            <option>All Events</option>
            <option>Critical Only</option>
            <option>High Risk</option>
            <option>Last 30 Days</option>
            <option>Last 90 Days</option>
          </select>
          <button className="inline-flex items-center px-5 py-2.5 border border-slate-300 text-sm font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 transition-colors">
            <svg className="-ml-0.5 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export Timeline
          </button>
        </div>
      </div>

      {/* Timeline Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Critical Events</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockTimelineEvents.filter(e => e.type === 'critical').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-rose-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">High Risk</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockTimelineEvents.filter(e => e.type === 'high').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Medium Risk</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockTimelineEvents.filter(e => e.type === 'medium').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Total Events</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">{mockTimelineEvents.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Timeline */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Event Timeline</h3>
          <p className="mt-1 text-sm text-slate-600">Recent contract changes and updates</p>
        </div>
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-slate-200"></div>

          {/* Timeline events */}
          <div className="space-y-6">
            {mockTimelineEvents.map((event, index) => (
              <div key={index} className="relative flex items-start">
                {/* Timeline dot */}
                <div className={`absolute left-8 -ml-4 flex items-center justify-center w-8 h-8 rounded-full ${getEventColor(event.type)} ring-4 ring-white`}>
                  {getEventIcon(event.type)}
                </div>

                {/* Event card */}
                <div className="ml-20 flex-1">
                  <div className={`rounded-xl border p-5 hover:shadow-md transition-all cursor-pointer ${getEventBgColor(event.type)} ${getEventBorderColor(event.type)}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="text-sm font-semibold text-slate-900">{event.vendor}</h4>
                          <span className={`px-2.5 py-0.5 text-xs font-medium rounded-md border ${
                            event.type === 'critical' ? 'bg-rose-100 text-rose-800 border-rose-300' :
                            event.type === 'high' ? 'bg-orange-100 text-orange-800 border-orange-300' :
                            event.type === 'medium' ? 'bg-amber-100 text-amber-800 border-amber-300' :
                            'bg-emerald-100 text-emerald-800 border-emerald-300'
                          }`}>
                            {event.type.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-slate-700">{event.event}</p>
                        <p className="text-xs text-slate-500 mt-2">{event.date}</p>
                      </div>
                      <button className="ml-4 text-indigo-600 hover:text-indigo-700 text-sm font-medium">
                        View Details →
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity Feed */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Recent Activity</h3>
          <p className="mt-1 text-sm text-slate-600">Latest updates and changes</p>
        </div>
        <div className="flow-root">
          <ul className="-mb-8">
            {mockRecentActivity.map((activity, activityIdx) => (
              <li key={activity.id}>
                <div className="relative pb-8">
                  {activityIdx !== mockRecentActivity.length - 1 ? (
                    <span className="absolute top-5 left-5 -ml-px h-full w-0.5 bg-slate-200" aria-hidden="true" />
                  ) : null}
                  <div className="relative flex items-start space-x-3">
                    <div>
                      <span className={`h-10 w-10 rounded-full flex items-center justify-center ring-4 ring-white ${
                        activity.type === 'high_risk_change' ? 'bg-rose-100' : 
                        activity.type === 'new_version' ? 'bg-blue-100' :
                        'bg-emerald-100'
                      }`}>
                        {activity.type === 'high_risk_change' ? (
                          <svg className="h-5 w-5 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        ) : activity.type === 'new_version' ? (
                          <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg className="h-5 w-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div>
                        <p className="text-sm font-medium text-slate-900">{activity.vendor}</p>
                        <p className="mt-0.5 text-sm text-slate-600">{activity.message}</p>
                      </div>
                      <div className="mt-2 text-xs text-slate-500">
                        {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
