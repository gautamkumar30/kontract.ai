'use client'

import { mockComplianceData, mockContracts } from '@/utils/mockData'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts'

const COLORS = {
  compliant: '#10b981',
  non_compliant: '#ef4444',
  pending: '#f59e0b',
}

export default function CompliancePage() {
  const totalContracts = mockContracts.length

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Compliance Dashboard</h1>
          <p className="mt-2 text-base text-slate-600">Track compliance status across regulatory frameworks</p>
        </div>
        <div className="flex space-x-3">
          <button className="inline-flex items-center px-5 py-2.5 border border-slate-300 text-sm font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 transition-colors">
            <svg className="-ml-0.5 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export Report
          </button>
          <button className="inline-flex items-center px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
            <svg className="-ml-0.5 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Run Audit
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Compliant</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockComplianceData.reduce((acc, f) => acc + f.compliant, 0)}
              </p>
            </div>
            <div className="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Non-Compliant</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockComplianceData.reduce((acc, f) => acc + f.non_compliant, 0)}
              </p>
            </div>
            <div className="w-12 h-12 bg-rose-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Pending Review</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {mockComplianceData.reduce((acc, f) => acc + f.pending, 0)}
              </p>
            </div>
            <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Compliance Rate</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {Math.round((mockComplianceData.reduce((acc, f) => acc + f.compliant, 0) / (mockComplianceData.length * totalContracts)) * 100)}%
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Framework Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {mockComplianceData.map((framework) => {
          const total = framework.compliant + framework.non_compliant + framework.pending
          const pieData = [
            { name: 'Compliant', value: framework.compliant },
            { name: 'Non-Compliant', value: framework.non_compliant },
            { name: 'Pending', value: framework.pending },
          ]

          return (
            <div key={framework.framework} className="bg-white rounded-xl border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-6">{framework.framework}</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        <Cell fill={COLORS.compliant} />
                        <Cell fill={COLORS.non_compliant} />
                        <Cell fill={COLORS.pending} />
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'white', 
                          border: '1px solid #e2e8f0',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-col justify-center space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-emerald-500 mr-2"></div>
                      <span className="text-sm text-slate-600">Compliant</span>
                    </div>
                    <span className="text-sm font-semibold text-slate-900">{framework.compliant}/{total}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-rose-500 mr-2"></div>
                      <span className="text-sm text-slate-600">Non-Compliant</span>
                    </div>
                    <span className="text-sm font-semibold text-slate-900">{framework.non_compliant}/{total}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-amber-500 mr-2"></div>
                      <span className="text-sm text-slate-600">Pending</span>
                    </div>
                    <span className="text-sm font-semibold text-slate-900">{framework.pending}/{total}</span>
                  </div>
                  <div className="pt-3 border-t border-slate-200">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-600 font-medium">Compliance Rate</span>
                      <span className="font-bold text-slate-900">
                        {Math.round((framework.compliant / total) * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-emerald-500 h-2 rounded-full transition-all"
                        style={{ width: `${(framework.compliant / total) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Comparison Chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Framework Comparison</h3>
          <p className="mt-1 text-sm text-slate-600">Compliance status across all frameworks</p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={mockComplianceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="framework" stroke="#64748b" style={{ fontSize: '12px' }} />
            <YAxis stroke="#64748b" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            <Legend wrapperStyle={{ fontSize: '14px' }} />
            <Bar dataKey="compliant" fill={COLORS.compliant} name="Compliant" radius={[8, 8, 0, 0]} />
            <Bar dataKey="non_compliant" fill={COLORS.non_compliant} name="Non-Compliant" radius={[8, 8, 0, 0]} />
            <Bar dataKey="pending" fill={COLORS.pending} name="Pending" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Action Items */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-6">Action Items</h3>
        <div className="space-y-4">
          <div className="flex items-start p-5 bg-rose-50 rounded-xl border border-rose-200">
            <svg className="h-6 w-6 text-rose-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-4 flex-1">
              <h4 className="text-sm font-semibold text-rose-900">7 Non-Compliant Contracts</h4>
              <p className="text-sm text-rose-700 mt-1">Review and update contracts to meet compliance requirements</p>
            </div>
            <button className="ml-4 px-4 py-2 bg-rose-600 text-white text-sm font-medium rounded-lg hover:bg-rose-700 transition-colors flex-shrink-0">
              Review
            </button>
          </div>

          <div className="flex items-start p-5 bg-amber-50 rounded-xl border border-amber-200">
            <svg className="h-6 w-6 text-amber-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            <div className="ml-4 flex-1">
              <h4 className="text-sm font-semibold text-amber-900">4 Pending Reviews</h4>
              <p className="text-sm text-amber-700 mt-1">Complete compliance assessments for pending contracts</p>
            </div>
            <button className="ml-4 px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 transition-colors flex-shrink-0">
              Start Review
            </button>
          </div>

          <div className="flex items-start p-5 bg-emerald-50 rounded-xl border border-emerald-200">
            <svg className="h-6 w-6 text-emerald-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div className="ml-4 flex-1">
              <h4 className="text-sm font-semibold text-emerald-900">29 Contracts Compliant</h4>
              <p className="text-sm text-emerald-700 mt-1">Maintain compliance through regular monitoring</p>
            </div>
            <button className="ml-4 px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 transition-colors flex-shrink-0">
              View
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
