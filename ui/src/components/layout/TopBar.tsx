import { invoke } from '@tauri-apps/api/core'
import { useState, useEffect } from 'react'
import { LogoIcon } from '../icons'

export default function TopBar() {
  const [serviceStatus, setServiceStatus] = useState<string>('checking')

  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const checkStatus = async () => {
    try {
      const status = await invoke<string>('get_service_status')
      setServiceStatus(status)
    } catch {
      setServiceStatus('unknown')
    }
  }

  const restartService = async () => {
    try {
      await invoke('restart_python_service')
      setServiceStatus('starting')
    } catch (e) {
      setServiceStatus('error')
    }
  }

  const statusColors: Record<string, string> = {
    running: 'bg-success',
    starting: 'bg-warning animate-pulse',
    not_started: 'bg-text-muted',
    error: 'bg-error',
    checking: 'bg-info animate-pulse',
    unknown: 'bg-text-muted',
  }

  return (
    <header className="h-[52px] flex items-center px-5 justify-between shrink-0 z-20"
      style={{ borderBottom: `1px solid var(--frame-line)`, background: 'var(--bg-dark)' }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center">
          <LogoIcon size={22} />
        </div>
        <div>
          <h1 className="text-base-b text-text-primary leading-tight">CineMate</h1>
          <p className="text-xs text-text-tertiary leading-tight">AI Video Production OS</p>
        </div>
      </div>

      {/* Center: Project Name */}
      <div className="flex items-center gap-2 px-4 py-1.5 rounded-md"
        style={{ background: 'var(--bg-base)', border: `1px solid var(--frame-line-dim)`, borderRadius: 'var(--radius-frame)' }}
      >
        <span className="text-xs text-text-tertiary">Project:</span>
        <span className="text-sm-b text-text-primary">Cyberpunk Ad</span>
        <span className="text-xs px-1.5 py-0.5 rounded ml-1"
          style={{ background: 'var(--brand-subtle)', color: 'var(--brand)' }}
        >
          v1.2
        </span>
      </div>

      {/* Right: Service Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${statusColors[serviceStatus] || 'bg-text-muted'}`} />
          <span className="text-xs text-text-secondary capitalize">{serviceStatus.replace('_', ' ')}</span>
          {serviceStatus !== 'running' && (
            <button
              onClick={restartService}
              className="text-xs px-2 py-1 rounded bg-brand text-white hover:opacity-90 transition-opacity"
            >
              Restart
            </button>
          )}
        </div>
        <div className="w-px h-5" style={{ background: 'var(--divider)' }} />
        <div className="text-xs font-mono text-text-tertiary">
          ¥ 245.50
        </div>
      </div>
    </header>
  )
}
