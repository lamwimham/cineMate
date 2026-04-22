import { useMemo } from 'react'

export interface DagEdgeData {
  id: string
  from: string
  to: string
  status?: 'idle' | 'active' | 'error'
}

interface DagEdgeProps {
  data: DagEdgeData
  fromX: number
  fromY: number
  toX: number
  toY: number
}

export default function DagEdge({ data, fromX, fromY, toX, toY }: DagEdgeProps) {
  const pathD = useMemo(() => {
    const dx = toX - fromX
    const controlOffset = Math.min(Math.abs(dx) * 0.45, 70)
    return `M ${fromX} ${fromY} C ${fromX + controlOffset} ${fromY}, ${toX - controlOffset} ${toY}, ${toX} ${toY}`
  }, [fromX, fromY, toX, toY])

  const color = data.status === 'active' ? '#6366f1' : data.status === 'error' ? '#ef4444' : '#334155'
  const isActive = data.status === 'active'

  return (
    <svg className="absolute inset-0 pointer-events-none overflow-visible" style={{ width: '100%', height: '100%' }}>
      <defs>
        <marker id={`arrow-${data.id}`} markerWidth="7" markerHeight="7" refX="6.5" refY="3.5" orient="auto">
          <path d="M0,1 L0,6 L5,3.5 z" fill={color} />
        </marker>
        {isActive && (
          <filter id={`glow-${data.id}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        )}
      </defs>

      {/* 底层发光线（active） */}
      {isActive && (
        <path
          d={pathD}
          fill="none"
          stroke={color}
          strokeWidth="4"
          opacity="0.15"
          filter={`url(#glow-${data.id})`}
        />
      )}

      {/* 背景线 */}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeDasharray={isActive ? undefined : '5 4'}
        opacity={isActive ? 0.5 : 0.25}
        markerEnd={`url(#arrow-${data.id})`}
      />

      {/* 流动光点（active） */}
      {isActive && (
        <>
          <path
            d={pathD}
            fill="none"
            stroke={color}
            strokeWidth="2"
            opacity="0.6"
            markerEnd={`url(#arrow-${data.id})`}
            style={{
              strokeDasharray: '12 48',
              animation: 'dashFlow 2.5s linear infinite',
            }}
          />
          {/* 主光点 */}
          <circle r="3" fill={color} opacity="0.9">
            <animateMotion dur="2.5s" repeatCount="indefinite" path={pathD} />
          </circle>
          {/* 尾迹光点 */}
          <circle r="1.5" fill="white" opacity="0.8">
            <animateMotion dur="2.5s" repeatCount="indefinite" path={pathD} />
          </circle>
        </>
      )}
    </svg>
  )
}
