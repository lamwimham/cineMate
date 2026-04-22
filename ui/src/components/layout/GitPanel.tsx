import { useState } from 'react'
import { GitIcon } from '../icons'

interface GitCommit {
  id: string
  message: string
  branch: string
  isHead: boolean
  timestamp: string
  cost: string
  status: 'success' | 'fail' | 'merge'
  children: string[]
}

const demoCommits: GitCommit[] = [
  { id: 'v1.0', message: 'Initial cyberpunk scene', branch: 'main', isHead: false, timestamp: '2h ago', cost: '¥12.5', status: 'success', children: ['v1.1'] },
  { id: 'v1.1', message: 'Add product close-up', branch: 'main', isHead: false, timestamp: '1h ago', cost: '¥8.3', status: 'success', children: ['v1.2', 'feature/music'] },
  { id: 'v1.2', message: 'Enhance neon lighting', branch: 'main', isHead: true, timestamp: '30m ago', cost: '¥5.2', status: 'success', children: [] },
  { id: 'feature/music', message: 'Try electronic BGM', branch: 'feature', isHead: true, timestamp: '45m ago', cost: '¥3.1', status: 'success', children: [] },
]

export default function GitPanel() {
  const [selectedCommit, setSelectedCommit] = useState<string>('v1.2')

  const getBranchColor = (branch: string) => {
    const colors: Record<string, string> = {
      main: '#6366f1',
      feature: '#22c55e',
      hotfix: '#ef4444',
    }
    return colors[branch] || '#94a3b8'
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 shrink-0 flex items-center justify-between"
        style={{ borderBottom: `1px solid var(--film-edge)` }}
      >
        <div className="flex items-center gap-2">
          <GitIcon size={18} color="var(--text-primary)" />
          <span className="text-sm-b text-text-primary">Video Git</span>
        </div>
        <span className="text-xs text-text-tertiary font-mono">4 commits</span>
      </div>

      {/* Branch list */}
      <div className="px-4 py-2 shrink-0 flex gap-2"
        style={{ borderBottom: `1px solid var(--film-edge)` }}
      >
        {['main', 'feature'].map(branch => (
          <span key={branch}
            className="text-xs px-2 py-0.5 rounded-full font-mono"
            style={{
              background: `${getBranchColor(branch)}20`,
              color: getBranchColor(branch),
              border: `1px solid ${getBranchColor(branch)}30`,
            }}
          >
            {branch}
          </span>
        ))}
      </div>

      {/* Commit tree */}
      <div className="flex-1 overflow-y-auto custom-scroll p-4">
        <div className="space-y-0">
          {demoCommits.map((commit, index) => {
            const isSelected = selectedCommit === commit.id
            const branchColor = getBranchColor(commit.branch)
            const isLast = index === demoCommits.length - 1

            return (
              <div key={commit.id} className="relative flex gap-3">
                {/* 树线 */}
                <div className="flex flex-col items-center shrink-0 w-5">
                  <div className="w-2.5 h-2.5 rounded-full shrink-0 z-10"
                    style={{
                      background: isSelected ? branchColor : 'var(--bg-dark)',
                      border: `2px solid ${branchColor}`,
                      boxShadow: isSelected ? `0 0 8px ${branchColor}60` : 'none',
                    }}
                  />
                  {!isLast && (
                    <div className="w-px flex-1 min-h-[32px]"
                      style={{ background: 'var(--film-edge)' }}
                    />
                  )}
                </div>

                {/* Commit 卡片 */}
                <div
                  className={`flex-1 p-2.5 rounded-lg mb-2 cursor-pointer transition-all duration-200 ${isSelected ? 'ring-1' : ''}`}
                  style={{
                    background: isSelected ? 'var(--bg-hover)' : 'transparent',
                    border: isSelected ? `1px solid ${branchColor}30` : '1px solid transparent',
                  }}
                  onClick={() => setSelectedCommit(commit.id)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono font-semibold"
                      style={{ color: branchColor }}
                    >
                      {commit.id}
                    </span>
                    {commit.isHead && (
                      <span className="text-xs px-1.5 py-0.5 rounded"
                        style={{ background: 'var(--brand-subtle)', color: 'var(--brand)' }}
                      >
                        HEAD
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-text-primary leading-snug mb-1">{commit.message}</p>
                  <div className="flex items-center gap-3 text-xs font-mono text-text-tertiary">
                    <span>{commit.timestamp}</span>
                    <span>{commit.cost}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Run info */}
      <div className="p-4 shrink-0" style={{ borderTop: `1px solid var(--film-edge)` }}>
        <div className="text-xs text-text-tertiary mb-2 font-mono uppercase tracking-wider">Current Run</div>
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Run ID</span>
            <span className="text-text-primary font-mono">run_abc123</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Status</span>
            <span className="text-success">● Completed</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Total Cost</span>
            <span className="text-text-primary font-mono">¥ 25.8</span>
          </div>
        </div>
      </div>

      {/* Skills */}
      <div className="p-4 shrink-0" style={{ borderTop: `1px solid var(--film-edge)` }}>
        <div className="text-xs text-text-tertiary mb-2 font-mono uppercase tracking-wider">Active Skills</div>
        <div className="flex flex-wrap gap-1.5">
          {['cyberpunk', 'short-ad', 'neon-light'].map(skill => (
            <span key={skill}
              className="text-xs px-2 py-1 rounded-md"
              style={{
                background: 'var(--bg-hover)',
                border: `1px solid var(--slate-mark)`,
                borderRadius: 'var(--radius-slate)',
                color: 'var(--text-secondary)',
              }}
            >
              {skill}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
