'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { contractsApi, versionsApi, clausesApi } from '@/utils/api'
import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'

export default function ContractDetailPage() {
  const params = useParams()
  const router = useRouter()
  const contractId = params.id as string
  
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null)
  const [compareMode, setCompareMode] = useState(false)
  const [compareVersionId, setCompareVersionId] = useState<string | null>(null)
  
  // Fetch contract
  const { data: contract, isLoading: contractLoading } = useQuery({
    queryKey: ['contract', contractId],
    queryFn: () => contractsApi.get(contractId),
    enabled: !!contractId
  })
  
  // Fetch versions
  const { data: versions, isLoading: versionsLoading } = useQuery({
    queryKey: ['versions', contractId],
    queryFn: () => versionsApi.list(contractId),
    enabled: !!contractId
  })
  
  // Auto-select latest version
  const latestVersion = versions?.[0]
  const effectiveVersionId = selectedVersionId || latestVersion?.id
  
  // Fetch clauses for selected version
  const { data: clauses, isLoading: clausesLoading } = useQuery({
    queryKey: ['clauses', effectiveVersionId],
    queryFn: () => clausesApi.listForVersion(effectiveVersionId!),
    enabled: !!effectiveVersionId
  })
  
  // Fetch version comparison if in compare mode
  const { data: comparison, isLoading: comparisonLoading } = useQuery({
    queryKey: ['comparison', compareVersionId, effectiveVersionId],
    queryFn: () => versionsApi.compare(compareVersionId!, effectiveVersionId!),
    enabled: compareMode && !!compareVersionId && !!effectiveVersionId && compareVersionId !== effectiveVersionId
  })
  
  const isLoading = contractLoading || versionsLoading
  
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-32 bg-slate-200 rounded-xl animate-pulse" />
        <div className="h-64 bg-slate-200 rounded-xl animate-pulse" />
        <div className="h-96 bg-slate-200 rounded-xl animate-pulse" />
      </div>
    )
  }
  
  if (!contract) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-slate-900">Contract not found</h2>
        <button
          onClick={() => router.push('/contracts')}
          className="mt-4 text-indigo-600 hover:text-indigo-700"
        >
          ← Back to contracts
        </button>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <button
              onClick={() => router.push('/contracts')}
              className="text-sm text-slate-600 hover:text-slate-900 mb-2 inline-flex items-center"
            >
              <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to contracts
            </button>
            <h1 className="text-3xl font-bold text-slate-900">{contract.vendor}</h1>
            <div className="mt-2 flex items-center gap-3">
              <span className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-indigo-100 text-indigo-800 border border-indigo-200">
                {contract.contract_type.toUpperCase()}
              </span>
              <span className="text-sm text-slate-500">
                Created {formatDistanceToNow(new Date(contract.created_at), { addSuffix: true })}
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCompareMode(!compareMode)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                compareMode
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {compareMode ? 'Exit Compare' : 'Compare Versions'}
            </button>
          </div>
        </div>
      </div>

      {/* Version Timeline */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-4">Version History</h2>
        {versionsLoading ? (
          <div className="text-center py-8 text-slate-500">Loading versions...</div>
        ) : versions && versions.length > 0 ? (
          <div className="space-y-3">
            {versions.map((version, idx) => (
              <div
                key={version.id}
                onClick={() => {
                  if (compareMode) {
                    setCompareVersionId(version.id)
                  } else {
                    setSelectedVersionId(version.id)
                  }
                }}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  compareMode && compareVersionId === version.id
                    ? 'border-purple-500 bg-purple-50'
                    : effectiveVersionId === version.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900">
                        Version {version.version_number}
                      </span>
                      {idx === 0 && (
                        <span className="px-2 py-0.5 text-xs font-medium bg-emerald-100 text-emerald-800 rounded">
                          Latest
                        </span>
                      )}
                      {compareMode && compareVersionId === version.id && (
                        <span className="px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                          Comparing
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-600 mt-1">
                      {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-500">{version.source_type.toUpperCase()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-center py-8">No versions found</p>
        )}
      </div>

      {/* Version Comparison Results */}
      {compareMode && comparison && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Comparison Results</h2>
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-50 rounded-lg p-4">
              <p className="text-sm text-slate-600">Total Changes</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {comparison.statistics.total_changes}
              </p>
            </div>
            <div className="bg-rose-50 rounded-lg p-4">
              <p className="text-sm text-rose-600">High Risk</p>
              <p className="text-2xl font-bold text-rose-900 mt-1">
                {comparison.statistics.high_risk_count}
              </p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600">Modified</p>
              <p className="text-2xl font-bold text-blue-900 mt-1">
                {comparison.statistics.changes_by_type.modified}
              </p>
            </div>
            <div className="bg-emerald-50 rounded-lg p-4">
              <p className="text-sm text-emerald-600">Added</p>
              <p className="text-2xl font-bold text-emerald-900 mt-1">
                {comparison.statistics.changes_by_type.added}
              </p>
            </div>
          </div>
          
          <div className="space-y-3">
            {comparison.changes.map((change) => (
              <div key={change.id} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      change.risk_level === 'critical' ? 'bg-rose-100 text-rose-800' :
                      change.risk_level === 'high' ? 'bg-orange-100 text-orange-800' :
                      change.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-slate-100 text-slate-800'
                    }`}>
                      {change.risk_level?.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      change.change_type === 'added' ? 'bg-emerald-100 text-emerald-800' :
                      change.change_type === 'removed' ? 'bg-rose-100 text-rose-800' :
                      change.change_type === 'modified' ? 'bg-blue-100 text-blue-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {change.change_type.toUpperCase()}
                    </span>
                  </div>
                  {change.similarity_score !== undefined && (
                    <span className="text-sm text-slate-600">
                      {(change.similarity_score * 100).toFixed(0)}% similar
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-900 mb-2">{change.explanation}</p>
                {change.clause && (
                  <div className="mt-3 p-3 bg-slate-50 rounded text-sm">
                    <p className="font-medium text-slate-700 mb-1">
                      Clause {change.clause.clause_number}: {change.clause.heading || change.clause.category}
                    </p>
                    <p className="text-slate-600 line-clamp-2">{change.clause.text}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clauses View */}
      {!compareMode && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">
            Clauses {effectiveVersionId && `(Version ${versions?.find(v => v.id === effectiveVersionId)?.version_number})`}
          </h2>
          {clausesLoading ? (
            <div className="text-center py-8 text-slate-500">Loading clauses...</div>
          ) : clauses && clauses.length > 0 ? (
            <div className="space-y-4">
              {clauses.map((clause) => (
                <div key={clause.id} className="border border-slate-200 rounded-lg p-4 hover:border-indigo-300 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900">
                        Clause {clause.clause_number}
                      </span>
                      {clause.category && (
                        <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                          {clause.category}
                        </span>
                      )}
                    </div>
                  </div>
                  {clause.heading && (
                    <h3 className="font-medium text-slate-900 mb-2">{clause.heading}</h3>
                  )}
                  <p className="text-sm text-slate-700 leading-relaxed">{clause.text}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">No clauses found for this version</p>
          )}
        </div>
      )}
    </div>
  )
}
