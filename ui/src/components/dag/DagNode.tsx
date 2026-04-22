import { useState } from 'react'
import {
  ScriptIcon, StoryboardIcon, VideoGenIcon, VoiceoverIcon,
  ComposeIcon, SuccessIcon, FailedIcon, ExecutingIcon,
  QueuedIcon, PendingIcon, SkippedIcon,
} from '../icons'

export type NodeStatus = 'pending' | 'queued' | 'executing' | 'succeeded' | 'failed' | 'skipped'

export interface DagNodeData {
  id: string
  name: string
  status: NodeStatus
  progress?: number
  duration?: string
  cost?: string
  error?: string
}

const statusColors: Record<NodeStatus, string> = {
  pending: '#475569',
  queued: '#3b82f6',
  executing: '#f59e0b',
  succeeded: '#22c55e',
  failed: '#ef4444',
  skipped: '#6366f1',
}

const statusGlows: Record<NodeStatus, string> = {
  pending: 'transparent',
  queued: 'rgba(59,130,246,0.2)',
  executing: 'rgba(245,158,11,0.3)',
  succeeded: 'rgba(34,197,94,0.2)',
  failed: 'rgba(239,68,68,0.2)',
  skipped: 'rgba(99,102,241,0.12)',
}

const statusLabels: Record<NodeStatus, string> = {
  pending: 'PENDING',
  queued: 'QUEUED',
  executing: 'EXECUTING',
  succeeded: 'DONE',
  failed: 'FAILED',
  skipped: 'REUSED',
}

const nodeIcons: Record<string, React.FC<{ size?: number; color?: string }>> = {
  Script: ScriptIcon,
  Storyboard: StoryboardIcon,
  'Video Gen': VideoGenIcon,
  Voiceover: VoiceoverIcon,
  Compose: ComposeIcon,
}

const statusIconComponents: Record<NodeStatus, React.FC<{ size?: number }>> = {
  pending: PendingIcon,
  queued: QueuedIcon,
  executing: ExecutingIcon,
  succeeded: SuccessIcon,
  failed: FailedIcon,
  skipped: SkippedIcon,
}

interface DagNodeProps {
  data: DagNodeData
  isSelected?: boolean
  onClick?: () => void
}

export default function DagNode({ data, isSelected, onClick }: DagNodeProps) {
  const [hovered, setHovered] = useState(false)
  const color = statusColors[data.status]
  const glow = statusGlows[data.status]
  const isExec = data.status === 'executing'
  const isFail = data.status === 'failed'
  const isSuccess = data.status === 'succeeded'
  const isSkipped = data.status === 'skipped'

  const NodeIcon = nodeIcons[data.name] || ScriptIcon
  const StatusIcon = statusIconComponents[data.status] || PendingIcon

  return (
    <div
      className="relative select-none"
      style={{ width: 160, height: 96 }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onClick}
    >
      {/* 外部光晕（executing） */}
      {isExec && (
        <div
          className="absolute -inset-3 rounded-2xl pointer-events-none"
          style={{
            background: `radial-gradient(circle, ${glow} 0%, transparent 65%)`,
            animation: 'pulseGlow 2.5s ease-in-out infinite',
          }}
        />
      )}

      {/* 主卡片 */}
      <div
        className="absolute inset-0 rounded-xl overflow-hidden cursor-pointer transition-all duration-200"
        style={{
          background: isSuccess
            ? 'linear-gradient(180deg, rgba(34,197,94,0.05) 0%, var(--bg-elevated) 50%)'
            : isFail
            ? 'linear-gradient(180deg, rgba(239,68,68,0.05) 0%, var(--bg-elevated) 50%)'
            : 'linear-gradient(180deg, rgba(255,255,255,0.02) 0%, var(--bg-elevated) 30%)',
          border: isSkipped
            ? `1px dashed ${color}40`
            : isSelected
            ? `1px solid ${color}`
            : `1px solid ${hovered ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.05)'}`,
          boxShadow: hovered
            ? `0 8px 28px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06), 0 0 20px ${glow}`
            : isExec
            ? `0 0 16px ${glow}, inset 0 1px 0 rgba(255,255,255,0.06)`
            : `0 2px 10px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)`,
          transform: hovered ? 'translateY(-2px) scale(1.02)' : 'translateY(0) scale(1)',
        }}
      >
        {/* 顶部状态条 */}
        <div
          className="h-[2px] w-full"
          style={{
            background: isExec
              ? `linear-gradient(90deg, ${color}, #fbbf24, ${color})`
              : color,
            backgroundSize: isExec ? '200% 100%' : undefined,
            animation: isExec ? 'progressFlow 2s linear infinite' : undefined,
          }}
        />

        <div className="p-3 pt-2">
          {/* 图标 + 名称 */}
          <div className="flex items-center gap-2 mb-1.5">
            <NodeIcon size={18} color={color} />
            <span className="text-[13px] font-semibold text-text-primary truncate">{data.name}</span>
          </div>

          {/* 进度条 */}
          {isExec && data.progress !== undefined && (
            <div className="mb-2">
              <div className="h-[3px] rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${data.progress}%`,
                    background: `linear-gradient(90deg, ${color}, #fbbf24)`,
                    transition: 'width 0.5s ease',
                  }}
                />
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-[10px] font-mono font-medium" style={{ color }}>{data.progress}%</span>
                <span className="text-[10px] font-mono text-text-muted">{data.duration}</span>
              </div>
            </div>
          )}

          {/* 成功/失败状态标记 */}
          {(isSuccess || isFail) && (
            <div className="flex items-center gap-1.5 mb-1">
              <StatusIcon size={14} />
              <span className="text-[10px] font-mono font-semibold" style={{ color }}>{statusLabels[data.status]}</span>
            </div>
          )}

          {/* 元数据 */}
          {!isExec && (
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono text-text-muted">{data.duration || '--'}</span>
              <span className="text-[10px] font-mono" style={{ color: 'var(--text-tertiary)' }}>{data.cost || '--'}</span>
            </div>
          )}
        </div>
      </div>

      {/* Tooltip */}
      {hovered && (
        <div
          className="absolute -top-9 left-1/2 -translate-x-1/2 px-2.5 py-1 rounded-lg whitespace-nowrap z-50 pointer-events-none"
          style={{
            background: 'var(--bg-hover)',
            border: '1px solid var(--slate-mark)',
            borderRadius: 'var(--radius-lens)',
            boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
          }}
        >
          <span className="text-[11px] font-mono font-medium" style={{ color }}>●</span>
          <span className="text-[11px] text-text-secondary ml-1">{statusLabels[data.status]}</span>
          {data.cost && <span className="text-[11px] text-text-muted ml-2">{data.cost}</span>}
        </div>
      )}
    </div>
  )
}
