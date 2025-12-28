'use client'

import { useState } from 'react'
import { contractsApi } from '@/utils/api'

interface AddContractModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function AddContractModal({ isOpen, onClose, onSuccess }: AddContractModalProps) {
  const [step, setStep] = useState<'method' | 'manual' | 'upload'>('method')
  const [vendor, setVendor] = useState('')
  const [contractType, setContractType] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const contractTypes = [
    'Terms of Service',
    'Privacy Policy',
    'Service Agreement',
    'Data Processing Agreement',
    'SLA',
    'Master Service Agreement',
  ]

  // Map display names to API codes
  const contractTypeMap: Record<string, string> = {
    'Terms of Service': 'tos',
    'Privacy Policy': 'privacy',
    'Service Agreement': 'sla',
    'Data Processing Agreement': 'dpa',
    'SLA': 'sla',
    'Master Service Agreement': 'msa',
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError(false)
    setErrorMessage('')
    
    try {
      // Map contract type to API code
      const apiContractType = contractTypeMap[contractType] || 'other'
      
      if (step === 'manual') {
        // Manual entry - create contract with URL
        await contractsApi.create({
          vendor,
          contract_type: apiContractType,
          source_url: url,
        })
      } else if (step === 'upload') {
        // File upload
        if (!file) {
          throw new Error('No file selected')
        }
        await contractsApi.upload(file, vendor, apiContractType)
      }
      
      setLoading(false)
      setSuccess(true)
      
      setTimeout(() => {
        setSuccess(false)
        onClose()
        resetForm()
        onSuccess?.()
      }, 2000)
    } catch (err) {
      setError(true)
      setErrorMessage(err instanceof Error ? err.message : 'Failed to add contract')
      setLoading(false)
    }
  }

  const resetForm = () => {
    setStep('method')
    setVendor('')
    setContractType('')
    setFile(null)
    setUrl('')
    setError(false)
    setErrorMessage('')
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-slate-900 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
      <div className="relative bg-white rounded-xl shadow-xl max-w-2xl w-full" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200">
          <div>
            <h3 className="text-2xl font-bold text-slate-900">Add New Contract</h3>
            <p className="mt-1 text-sm text-slate-600">
              {step === 'method' && 'Choose how to add your contract'}
              {step === 'manual' && 'Enter contract details manually'}
              {step === 'upload' && 'Upload contract document'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-6">
          {/* Error Display */}
          {error && (
            <div className="mb-4 bg-rose-50 border border-rose-200 rounded-lg p-4">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-rose-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-rose-900">Error</h3>
                  <p className="text-sm text-rose-800 mt-1">{errorMessage}</p>
                </div>
                <button
                  onClick={() => setError(false)}
                  className="text-rose-400 hover:text-rose-600 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}
          
          {success ? (
            <div className="text-center py-12">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-emerald-100 mb-4">
                <svg className="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Contract Added Successfully!</h3>
              <p className="text-sm text-slate-600">Your contract is being processed and will appear shortly.</p>
            </div>
          ) : (
            <>
              {/* Method Selection */}
              {step === 'method' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => setStep('manual')}
                    className="p-6 border-2 border-slate-200 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left group"
                  >
                    <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-indigo-200 transition-colors">
                      <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </div>
                    <h4 className="text-lg font-semibold text-slate-900 mb-2">Manual Entry</h4>
                    <p className="text-sm text-slate-600">Enter contract details and paste URL for monitoring</p>
                  </button>

                  <button
                    onClick={() => setStep('upload')}
                    className="p-6 border-2 border-slate-200 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left group"
                  >
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
                      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <h4 className="text-lg font-semibold text-slate-900 mb-2">Upload Document</h4>
                    <p className="text-sm text-slate-600">Upload PDF or text file of the contract</p>
                  </button>
                </div>
              )}

              {/* Manual Entry Form */}
              {step === 'manual' && (
                <div className="space-y-5">
                  <div>
                    <label htmlFor="vendor" className="block text-sm font-medium text-slate-700 mb-2">
                      Vendor Name *
                    </label>
                    <input
                      type="text"
                      id="vendor"
                      value={vendor}
                      onChange={(e) => setVendor(e.target.value)}
                      className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="e.g., Stripe, AWS, Google Cloud"
                    />
                  </div>

                  <div>
                    <label htmlFor="contractType" className="block text-sm font-medium text-slate-700 mb-2">
                      Contract Type *
                    </label>
                    <select
                      id="contractType"
                      value={contractType}
                      onChange={(e) => setContractType(e.target.value)}
                      className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="">Select a type</option>
                      {contractTypes.map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="url" className="block text-sm font-medium text-slate-700 mb-2">
                      Contract URL *
                    </label>
                    <input
                      type="url"
                      id="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="https://example.com/terms"
                    />
                    <p className="mt-2 text-xs text-slate-500">We'll monitor this URL for changes</p>
                  </div>
                </div>
              )}

              {/* Upload Form */}
              {step === 'upload' && (
                <div className="space-y-5">
                  <div>
                    <label htmlFor="vendor-upload" className="block text-sm font-medium text-slate-700 mb-2">
                      Vendor Name *
                    </label>
                    <input
                      type="text"
                      id="vendor-upload"
                      value={vendor}
                      onChange={(e) => setVendor(e.target.value)}
                      className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="e.g., Stripe, AWS, Google Cloud"
                    />
                  </div>

                  <div>
                    <label htmlFor="contractType-upload" className="block text-sm font-medium text-slate-700 mb-2">
                      Contract Type *
                    </label>
                    <select
                      id="contractType-upload"
                      value={contractType}
                      onChange={(e) => setContractType(e.target.value)}
                      className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="">Select a type</option>
                      {contractTypes.map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Upload Contract Document *
                    </label>
                    <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-300 border-dashed rounded-lg hover:border-indigo-400 transition-colors">
                      <div className="space-y-1 text-center">
                        <svg className="mx-auto h-12 w-12 text-slate-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        <div className="flex text-sm text-slate-600">
                          <label htmlFor="file-upload" className="relative cursor-pointer rounded-md font-medium text-indigo-600 hover:text-indigo-500">
                            <span>Upload a file</span>
                            <input
                              id="file-upload"
                              name="file-upload"
                              type="file"
                              className="sr-only"
                              accept=".pdf,.txt,.doc,.docx"
                              onChange={handleFileChange}
                            />
                          </label>
                          <p className="pl-1">or drag and drop</p>
                        </div>
                        <p className="text-xs text-slate-500">PDF, TXT, DOC up to 10MB</p>
                        {file && (
                          <p className="text-sm text-indigo-600 font-medium mt-2">
                            Selected: {file.name}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        {!success && (
          <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 rounded-b-xl flex justify-between">
            {step !== 'method' ? (
              <button
                onClick={() => setStep('method')}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors"
              >
                ← Back
              </button>
            ) : (
              <div></div>
            )}
            
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-slate-300 text-sm font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              {step !== 'method' && (
                <button
                  onClick={handleSubmit}
                  disabled={loading || !vendor || !contractType || (step === 'manual' && !url) || (step === 'upload' && !file)}
                  className="px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    'Add Contract'
                  )}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
