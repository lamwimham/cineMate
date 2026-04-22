import { useState } from 'react'
import { PlayIcon, TypeIcon } from '../icons'
import type { AssetRef } from '../../types/chat'

interface AssetGalleryMessageProps {
  title: string
  assets: AssetRef[]
  onSelect?: (assetId: string) => void
  onViewAll?: () => void
}

const typeLabels: Record<string, string> = {
  image: '图片',
  video: '视频',
  audio: '音频',
}

export default function AssetGalleryMessage({ title, assets, onSelect, onViewAll }: AssetGalleryMessageProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-primary">{title}</p>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-[11px] font-mono text-brand hover:text-brand-dim transition-colors"
          >
            查看全部 →
          </button>
        )}
      </div>
      <div className="flex gap-2.5 overflow-x-auto custom-scroll pb-1">
        {assets.map(asset => {
          const isHovered = hoveredId === asset.id
          return (
            <button
              key={asset.id}
              onMouseEnter={() => setHoveredId(asset.id)}
              onMouseLeave={() => setHoveredId(null)}
              onClick={() => onSelect?.(asset.id)}
              className="shrink-0 text-left rounded-xl overflow-hidden transition-all duration-200"
              style={{
                width: 140,
                border: isHovered
                  ? `1px solid var(--cine-gold-glow)`
                  : `1px solid var(--slate-mark)`,
                borderRadius: 'var(--radius-lens)',
                boxShadow: isHovered
                  ? '0 4px 16px rgba(0,0,0,0.4), 0 0 12px rgba(245,197,66,0.1)'
                  : '0 1px 4px rgba(0,0,0,0.2)',
                transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
              }}
            >
              {/* 缩略图 */}
              <div
                className="h-[80px] flex items-center justify-center relative"
                style={{
                  background: asset.type === 'video'
                    ? 'linear-gradient(135deg, #1a1a3e, #2d2d5d)'
                    : asset.type === 'audio'
                    ? 'linear-gradient(135deg, #1a2e1a, #2d5d2d)'
                    : 'linear-gradient(135deg, #1e1b4b, #312e81)',
                }}
              >
                <div className="opacity-40">
                  <TypeIcon type={asset.type} size={24} />
                </div>
                {asset.type === 'video' && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center"
                      style={{ background: 'rgba(0,0,0,0.5)' }}
                    >
                      <PlayIcon size={12} color="white" />
                    </div>
                  </div>
                )}
                {/* 类型标签 */}
                <span className="absolute top-1.5 left-1.5 text-[9px] font-mono px-1.5 py-0.5 rounded"
                  style={{
                    background: 'rgba(0,0,0,0.6)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  {typeLabels[asset.type]}
                </span>
              </div>

              {/* 信息 */}
              <div className="p-2">
                <p className="text-[11px] text-text-primary truncate font-medium">{asset.name}</p>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[9px] font-mono text-text-muted">{asset.metadata.createdAt}</span>
                  <span className="text-[9px] font-mono" style={{ color: 'var(--text-tertiary)' }}>{asset.metadata.cost}</span>
                </div>
                {asset.metadata.dimensions && (
                  <span className="text-[9px] font-mono text-text-muted">{asset.metadata.dimensions}</span>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
