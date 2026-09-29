import React, { useState } from 'react'

export default function App() {
  const [healthStatus, setHealthStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const checkHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:8000/api/health/')
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      const data = await res.json()
      setHealthStatus(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="max-w-2xl w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-2xl text-white shadow-lg shadow-indigo-500/30">
            P
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Placement Portal</h1>
            <p className="text-sm text-slate-400">Phase 1 & 2 Environment Verification</p>
          </div>
        </div>

        {/* Tech Stack Badges */}
        <div className="flex flex-wrap gap-2 pt-2">
          {['React.js', 'Vite', 'Tailwind CSS', 'Django REST Framework', 'MySQL'].map((tech) => (
            <span
              key={tech}
              className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-indigo-400 border border-slate-700/60"
            >
              {tech}
            </span>
          ))}
        </div>

        {/* Status Box */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-5 space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">Environment Check</h2>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-300">Frontend Environment (Vite + Tailwind)</span>
            <span className="flex items-center text-emerald-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
              Operational
            </span>
          </div>

          <div className="border-t border-slate-800/80 pt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <span className="text-slate-300 text-sm">Backend Health Endpoint (`/api/health/`)</span>
            <button
              onClick={checkHealth}
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide transition shadow hover:shadow-indigo-500/20 disabled:opacity-50"
            >
              {loading ? 'Testing...' : 'Test Backend Connection'}
            </button>
          </div>

          {/* Result Display */}
          {healthStatus && (
            <div className="mt-3 p-3 bg-emerald-950/40 border border-emerald-800/50 rounded-lg text-emerald-300 text-xs font-mono">
              <p className="font-semibold">Backend Response:</p>
              <pre>{JSON.stringify(healthStatus, null, 2)}</pre>
            </div>
          )}

          {error && (
            <div className="mt-3 p-3 bg-rose-950/40 border border-rose-800/50 rounded-lg text-rose-300 text-xs font-mono">
              <p className="font-semibold">Connection Error:</p>
              <p>{error}</p>
              <p className="text-slate-400 text-[11px] mt-1">Make sure the Django server is running at http://localhost:8000</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
