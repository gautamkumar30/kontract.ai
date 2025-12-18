'use client'

import { mockVendorRiskScores, mockContracts } from '@/utils/mockData'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts'

export default function VendorComparisonPage() {
  const radarData = mockVendorRiskScores.slice(0, 6).map(v => ({
    vendor: v.vendor,
    risk: v.score,
    changes: v.changes * 10,
  }))

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') {
      return (
        <svg className="h-5 w-5 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
        </svg>
      )
    } else if (trend === 'down') {
      return (
        <svg className="h-5 w-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      )
    }
    return (
      <svg className="h-5 w-5 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M4 10a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1z" clipRule="evenodd" />
      </svg>
    )
  }

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'bg-rose-500'
    if (score >= 60) return 'bg-orange-500'
    if (score >= 40) return 'bg-amber-500'
    return 'bg-emerald-500'
  }

  const getRiskBorderColor = (score: number) => {
    if (score >= 80) return 'border-rose-300'
    if (score >= 60) return 'border-orange-300'
    if (score >= 40) return 'border-amber-300'
    return 'border-emerald-300'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Vendor Comparison</h1>
          <p className="mt-2 text-base text-slate-600">Compare risk scores and changes across all vendors</p>
        </div>
        <button className="inline-flex items-center px-5 py-2.5 border border-slate-300 text-sm font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 transition-colors">
          <svg className="-ml-0.5 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Filter Vendors
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-slate-900">
              {Math.round(mockVendorRiskScores.reduce((acc, v) => acc + v.score, 0) / mockVendorRiskScores.length)}
            </p>
            <p className="text-sm text-slate-600 mt-2">Average Risk Score</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-rose-600">
              {mockVendorRiskScores.filter(v => v.score >= 70).length}
            </p>
            <p className="text-sm text-slate-600 mt-2">High Risk Vendors</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-amber-600">
              {mockVendorRiskScores.filter(v => v.trend === 'up').length}
            </p>
            <p className="text-sm text-slate-600 mt-2">Increasing Risk</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-emerald-600">
              {mockVendorRiskScores.filter(v => v.trend === 'down').length}
            </p>
            <p className="text-sm text-slate-600 mt-2">Decreasing Risk</p>
          </div>
        </div>
      </div>

      {/* Risk Score Comparison Chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Vendor Risk Scores</h3>
          <p className="mt-1 text-sm text-slate-600">Comparative risk analysis across all vendors</p>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={mockVendorRiskScores} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis type="number" domain={[0, 100]} stroke="#64748b" style={{ fontSize: '12px' }} />
            <YAxis dataKey="vendor" type="category" width={120} stroke="#64748b" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            <Bar dataKey="score" name="Risk Score" radius={[0, 8, 8, 0]}>
              {mockVendorRiskScores.map((entry, index) => (
                <rect
                  key={`cell-${index}`}
                  fill={entry.score >= 80 ? '#dc2626' : entry.score >= 60 ? '#ea580c' : entry.score >= 40 ? '#f59e0b' : '#10b981'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Radar Chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Top 6 Vendors - Multi-Dimensional View</h3>
          <p className="mt-1 text-sm text-slate-600">Risk score vs change frequency analysis</p>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="vendor" stroke="#64748b" style={{ fontSize: '12px' }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#64748b" style={{ fontSize: '12px' }} />
            <Radar name="Risk Score" dataKey="risk" stroke="#dc2626" fill="#dc2626" fillOpacity={0.5} />
            <Radar name="Changes (x10)" dataKey="changes" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.5} />
            <Legend wrapperStyle={{ fontSize: '14px' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Vendor Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockVendorRiskScores.map((vendor) => {
          const contract = mockContracts.find(c => c.vendor === vendor.vendor)
          return (
            <div key={vendor.vendor} className={`bg-white rounded-xl border-2 ${getRiskBorderColor(vendor.score)} hover:shadow-lg transition-all duration-200`}>
              <div className={`h-2 ${getRiskColor(vendor.score)} rounded-t-xl`}></div>
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-900">{vendor.vendor}</h3>
                  {getTrendIcon(vendor.trend)}
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-600 font-medium">Risk Score</span>
                      <span className="font-bold text-slate-900">{vendor.score}/100</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2.5">
                      <div
                        className={`h-2.5 rounded-full ${getRiskColor(vendor.score)} transition-all`}
                        style={{ width: `${vendor.score}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200">
                    <div>
                      <p className="text-xs text-slate-500 font-medium">Changes</p>
                      <p className="text-xl font-bold text-slate-900 mt-1">{vendor.changes}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 font-medium">Versions</p>
                      <p className="text-xl font-bold text-slate-900 mt-1">{contract?.versions_count || 0}</p>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-slate-200">
                    <p className="text-xs text-slate-500 font-medium mb-1">Contract Type</p>
                    <p className="text-sm text-slate-900">{contract?.contract_type || 'N/A'}</p>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${
                      vendor.trend === 'up' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                      vendor.trend === 'down' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      'bg-slate-50 text-slate-700 border-slate-200'
                    }`}>
                      {vendor.trend === 'up' ? 'Risk Increasing' : vendor.trend === 'down' ? 'Risk Decreasing' : 'Stable'}
                    </span>
                  </div>
                </div>

                <div className="mt-6 flex space-x-2">
                  <button className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 transition-colors">
                    View Details
                  </button>
                  <button className="flex-1 px-3 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors">
                    Compare
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
