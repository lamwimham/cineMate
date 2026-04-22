import { useState } from 'react'
import { AssetsIcon, SearchIcon, TypeIcon } from '../icons'
import type { Asset, AssetType } from '../../types/asset'

const demoAssets: Asset[] = [
  {
    id: 'img_1',
    type: 'image',
    name: 'Storyboard Frame 1',
    url: '',
    thumbnail: '',
    status: 'ready',
    projectId: 'proj_1',
    runId: 'run_abc123',
    nodeId: 'storyboard',
    metadata: {
      createdAt: '2026-04-21 14:30',
      cost: 0.5,
      prompt: 'Cyberpunk city street at night, neon signs',
      dimensions: '1024×576',
      format: 'png',
    },
    tags: ['storyboard', 'cyberpunk'],
  },
  {
    id: 'img_2',
    type: 'image',
    name: 'Storyboard Frame 2',
    url: '',
    thumbnail: '',
    status: 'ready',
    projectId: 'proj_1',
    runId: 'run_abc123',
    nodeId: 'storyboard',
    metadata: {
      createdAt: '2026-04-21 14:32',
      cost: 0.5,
      prompt: 'Product close-up on reflective surface',
      dimensions: '1024×576',
      format: 'png',
    },
    tags: ['storyboard', 'product'],
  },
  {
    id: 'vid_1',
    type: 'video',
    name: 'Video Segment A',
    url: '',
    thumbnail: '',
    status: 'generating',
    projectId: 'proj_1',
    runId: 'run_abc123',
    nodeId: 'video',
    metadata: {
      createdAt: '2026-04-21 14:45',
      cost: 8.0,
      prompt: 'Cinematic drone shot through cyberpunk city',
      dimensions: '1920×1080',
      duration: '5s',
      format: 'mp4',
    },
    tags: ['video', 'cyberpunk', 'drone'],
  },
  {
    id: 'aud_1',
    type: 'audio',
    name: 'Voiceover Track',
    url: '',
    thumbnail: '',
    status: 'ready',
    projectId: 'proj_1',
    runId: 'run_abc123',
    nodeId: 'voice',
    metadata: {
      createdAt: '2026-04-21 15:00',
      cost: 2.0,
      duration: '15s',
      format: 'wav',
    },
    tags: ['voice', 'narration'],
  },
  {
    id: 'img_3',
    type: 'image',
    name: 'Reference Image',
    url: '',
    thumbnail: '',
    status: 'used',
    projectId: 'proj_1',
    runId: 'run_v1_0',
    metadata: {
      createdAt: '2026-04-21 12:00',
      cost: 0.3,
      dimensions: '512×512',
      format: 'jpg',
    },
    tags: ['reference'],
  },
]

const typeFilters: { key: AssetType | 'all'; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'image', label: '图片' },
  { key: 'video', label: '视频' },
  { key: 'audio', label: '音频' },
]

const statusColors: Record<string, { bg: string; text: string; dot: string }> = {
  generating: { bg: 'rgba(245,158,11,0.1)', text: '#f59e0b', dot: '#f59e0b' },
  ready: { bg: 'rgba(59,130,246,0.1)', text: '#3b82f6', dot: '#3b82f6' },
  used: { bg: 'rgba(34,197,94,0.1)', text: '#22c55e', dot: '#22c55e' },
  archived: { bg: 'rgba(100,116,139,0.1)', text: '#64748b', dot: '#64748b' },
}

const typeGradients: Record<string, string> = {
  image: 'linear-gradient(135deg, #1e1b4b, #312e81)',
  video: 'linear-gradient(135deg, #1a1a3e, #2d2d5d)',
  audio: 'linear-gradient(135deg, #1a2e1a, #2d5d2d)',
}

export default function AssetPanel() {
  const [activeFilter, setActiveFilter] = useState<AssetType | 'all'>('all')
  const [search, setSearch] = useState('')

  const filtered = demoAssets.filter(a => {
    if (activeFilter !== 'all' && a.type !== activeFilter) return false
    if (search && !a.name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  // 按 runId 分组
  const groups: Record<string, Asset[]> = {}
  filtered.forEach(a => {
    const key = a.runId || '未分类'
    if (!groups[key]) groups[key] = []
    groups[key].push(a)
  })

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 shrink-0 flex items-center justify-between"
        style={{ borderBottom: `1px solid var(--film-edge)` }}
      >
        <div className="flex items-center gap-2">
          <AssetsIcon size={18} color="var(--text-primary)" />
          <span className="text-sm-b text-text-primary">Assets</span>
        </div>
        <span className="text-xs text-text-tertiary font-mono">{filtered.length} items</span>
      </div>

      {/* Search */}
      <div className="px-3 py-2 shrink-0" style={{ borderBottom: `1px solid var(--film-edge)` }}>
        <div className="relative">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="搜索资产..."
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg outline-none transition-colors"
            style={{
              background: 'var(--bg-base)',
              border: `1px solid var(--slate-mark)`,
              borderRadius: 'var(--radius-slate)',
              color: 'var(--text-primary)',
            }}
          />
          <div className="absolute left-2.5 top-1/2 -translate-y-1/2">
            <SearchIcon size={12} color="var(--text-muted)" />
          </div>
        </div>
      </div>

      {/* Type Filters */}
      <div className="px-3 py-2 shrink-0 flex gap-1" style={{ borderBottom: `1px solid var(--film-edge)` }}>
        {typeFilters.map(f => (
          <button
            key={f.key}
            onClick={() => setActiveFilter(f.key)}
            className="flex-1 flex items-center justify-center gap-1 py-1.5 text-[11px] transition-all"
            style={{
              background: activeFilter === f.key ? 'var(--cine-glow)' : 'transparent',
              color: activeFilter === f.key ? 'var(--cine-gold)' : 'var(--text-tertiary)',
              border: activeFilter === f.key ? `1px solid var(--cine-gold-glow)` : '1px solid transparent',
              borderRadius: 'var(--radius-slate)',
            }}
          >
            <TypeIcon type={f.key === 'all' ? 'image' : f.key} size={12} />
            <span className="font-medium">{f.label}</span>
          </button>
        ))}
      </div>

      {/* Asset Grid */}
      <div className="flex-1 overflow-y-auto custom-scroll p-3 space-y-4">
        {Object.entries(groups).map(([runId, assets]) => (
          <div key={runId}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">
                {runId === '未分类' ? '未分类' : runId}
              </span>
              <div className="flex-1 h-px" style={{ background: 'var(--film-edge)' }} />
              <span className="text-[10px] font-mono text-text-muted">{assets.length}</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {assets.map(asset => {
                const status = statusColors[asset.status]
                return (
                  <div
                    key={asset.id}
                    className="rounded-xl overflow-hidden transition-all duration-200 group cursor-pointer"
                    style={{
                      border: `1px solid var(--slate-mark)`,
              borderRadius: 'var(--radius-slate)',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.borderColor = 'var(--cine-gold-glow)'
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)'
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.borderColor = 'var(--slate-mark)'
                      e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)'
                    }}
                  >
                    {/* 缩略图 */}
                    <div
                      className="h-[72px] flex items-center justify-center relative"
                      style={{ background: typeGradients[asset.type] }}
                    >
                      <div className="opacity-40">
                        <TypeIcon type={asset.type} size={24} />
                      </div>
                      {asset.type === 'video' && asset.status === 'generating' && (
                        <div className="absolute inset-0 flex items-center justify-center"
                          style={{ background: 'rgba(0,0,0,0.4)' }}
                        >
                          <div className="w-6 h-6 rounded-full border-2 border-warning border-t-transparent animate-spin" />
                        </div>
                      )}
                      {/* 状态角标 */}
                      <span
                        className="absolute top-1.5 right-1.5 text-[9px] font-mono px-1 py-0.5 rounded"
                        style={{ background: status.bg, color: status.text }}
                      >
                        {asset.status}
                      </span>
                    </div>

                    {/* 信息 */}
                    <div className="p-2">
                      <p className="text-[11px] text-text-primary truncate font-medium">{asset.name}</p>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-[9px] font-mono text-text-muted">
                          {asset.metadata.dimensions || asset.metadata.duration || '--'}
                        </span>
                        <span className="text-[9px] font-mono" style={{ color: 'var(--text-tertiary)' }}>
                          ¥{asset.metadata.cost}
                        </span>
                      </div>
                      {/* Tags */}
                      <div className="flex flex-wrap gap-1 mt-1.5">
                        {asset.tags.slice(0, 2).map(tag => (
                          <span key={tag}
                            className="text-[9px] px-1 py-0.5 rounded"
                            style={{
                              background: 'var(--bg-hover)',
                              color: 'var(--text-muted)',
                            }}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer stats */}
      <div className="px-4 py-2 shrink-0" style={{ borderTop: `1px solid var(--film-edge)` }}>
        <div className="flex items-center justify-between text-[10px] font-mono text-text-muted">
          <span>Total: ¥{demoAssets.reduce((s, a) => s + a.metadata.cost, 0).toFixed(1)}</span>
          <span>{demoAssets.filter(a => a.status === 'generating').length} generating</span>
        </div>
      </div>
    </div>
  )
}
