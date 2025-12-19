'use client'

import { useQuery } from '@tanstack/react-query'
import { useState, useMemo } from 'react'
import { analyticsApi, statsApi } from '@/utils/api'
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts'
import { format, parseISO } from 'date-fns'

const RISK_COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#f59e0b',
  low: '#10b981',
}

const CHANGE_TYPE_COLORS = {
  added: '#10b981',
  removed: '#ef4444',
  modified: '#f59e0b',
  rewritten: '#8b5cf6',
}

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState('30')
  
  // Fetch data
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsApi.get()
  })
  
  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['analytics-trends', dateRange],
    queryFn: () => analyticsApi.getTrends(dateRange === 'all' ? 0 : parseInt(dateRange))
  })
  
  const { data: riskDistribution, isLoading: riskLoading } = useQuery({
    queryKey: ['analytics-risk'],
    queryFn: () => analyticsApi.getRiskDistribution()
  })
  
  const { data: changeTypes, isLoading: typesLoading } = useQuery({
    queryKey: ['analytics-types'],
    queryFn: () => analyticsApi.getChangeTypes()
  })
  
  const { data: vendorStats, isLoading: vendorsLoading } = useQuery({
    queryKey: ['analytics-vendors'],
    queryFn: () => analyticsApi.getVendorStats(10)
  })
  
  const isLoading = statsLoading || trendsLoading || riskLoading || typesLoading || vendorsLoading
  
  // Process data for charts
  const trendsData = useMemo(() => {
    if (!trends) return []
    return trends.map(item => ({
      date: format(parseISO(item.date), 'MMM dd'),
      changes: item.count
    }))
  }, [trends])
  
  const riskData = useMemo(() => {
    if (!riskDistribution) return []
    return [
      { name: 'Critical', value: riskDistribution.critical, color: RISK_COLORS.critical },
      { name: 'High', value: riskDistribution.high, color: RISK_COLORS.high },
      { name: 'Medium', value: riskDistribution.medium, color: RISK_COLORS.medium },
      { name: 'Low', value: riskDistribution.low, color: RISK_COLORS.low },
    ].filter(item => item.value > 0)
  }, [riskDistribution])
  
  const typesData = useMemo(() => {
    if (!changeTypes) return []
    return [
      { type: 'Added', count: changeTypes.added, color: CHANGE_TYPE_COLORS.added },
      { type: 'Removed', count: changeTypes.removed, color: CHANGE_TYPE_COLORS.removed },
      { type: 'Modified', count: changeTypes.modified, color: CHANGE_TYPE_COLORS.modified },
      { type: 'Rewritten', count: changeTypes.rewritten, color: CHANGE_TYPE_COLORS.rewritten },
    ]
  }, [changeTypes])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Analytics Dashboard</h1>
          <p className="mt-2 text-base text-slate-600">Contract insights and change trends</p>
        </div>
        
        {/* Date Range Filter */}
        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value)}
          className="px-4 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        >
          <option value="7">Last 7 Days</option>
          <option value="30">Last 30 Days</option>
          <option value="90">Last 90 Days</option>
          <option value="365">Last Year</option>
          <option value="all">All Time</option>
        </select>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Total Contracts</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.total_contracts || 0}
              </p>
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
              <p className="text-sm font-medium text-slate-600">High Risk Changes</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.high_risk_changes || 0}
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
              <p className="text-sm font-medium text-slate-600">Monitored Vendors</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.monitored_vendors || 0}
              </p>
            </div>
            <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Pending Alerts</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {isLoading ? '...' : stats?.pending_alerts || 0}
              </p>
            </div>
            <div className="w-10 h-10 bg-yellow-50 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Change Trends Chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Change Trends Over Time</h3>
          <p className="mt-1 text-sm text-slate-600">Number of changes detected per day</p>
        </div>
        {trendsLoading ? (
          <div className="h-80 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : trendsData.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={trendsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" stroke="#64748b" style={{ fontSize: '12px' }} />
              <YAxis stroke="#64748b" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="changes" stroke="#6366f1" strokeWidth={2.5} dot={{ r: 4 }} name="Changes" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-80 flex items-center justify-center text-slate-500">
            <p>No change data available for this period</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution Pie Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-slate-900">Risk Distribution</h3>
            <p className="mt-1 text-sm text-slate-600">Changes by risk level</p>
          </div>
          {riskLoading ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : riskData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-slate-500">
              <p>No risk data available</p>
            </div>
          )}
        </div>

        {/* Change Types Bar Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-slate-900">Changes by Type</h3>
            <p className="mt-1 text-sm text-slate-600">Distribution of change types</p>
          </div>
          {typesLoading ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={typesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="type" stroke="#64748b" style={{ fontSize: '12px' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                  }}
                />
                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                  {typesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Vendor Comparison */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Top Vendors by Changes</h3>
          <p className="mt-1 text-sm text-slate-600">Vendors with the most contract changes</p>
        </div>
        {vendorsLoading ? (
          <div className="h-80 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : vendorStats && vendorStats.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={vendorStats} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" stroke="#64748b" style={{ fontSize: '12px' }} />
              <YAxis dataKey="vendor" type="category" width={150} stroke="#64748b" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Legend />
              <Bar dataKey="changes" fill="#6366f1" name="Changes" radius={[0, 8, 8, 0]} />
              <Bar dataKey="contracts" fill="#10b981" name="Contracts" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-80 flex items-center justify-center text-slate-500">
            <p>No vendor data available</p>
          </div>
        )}
      </div>
    </div>
  )
}
