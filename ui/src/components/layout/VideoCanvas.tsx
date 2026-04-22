import { useState, useRef, useEffect, useCallback } from 'react'
import { PlayIcon, PauseIcon } from '../icons'

interface AspectPreset {
  label: string
  ratio: number
  ratioCss: string
  resolution: string
}

const aspectPresets: AspectPreset[] = [
  { label: '16:9', ratio: 16 / 9, ratioCss: '16/9', resolution: '1920 × 1080' },
  { label: '9:16', ratio: 9 / 16, ratioCss: '9/16', resolution: '1080 × 1920' },
  { label: '1:1', ratio: 1, ratioCss: '1/1', resolution: '1080 × 1080' },
  { label: '4:3', ratio: 4 / 3, ratioCss: '4/3', resolution: '1440 × 1080' },
  { label: '21:9', ratio: 21 / 9, ratioCss: '21/9', resolution: '2560 × 1080' },
]

export default function VideoCanvas() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [aspectIndex, setAspectIndex] = useState(0)
  const [showAspectMenu, setShowAspectMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  const currentAspect = aspectPresets[aspectIndex]

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowAspectMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  // 模拟播放进度
  const togglePlay = () => {
    setIsPlaying(!isPlaying)
    if (!isPlaying) {
      const interval = setInterval(() => {
        setProgress(p => {
          if (p >= 100) {
            clearInterval(interval)
            setIsPlaying(false)
            return 0
          }
          return p + 1
        })
      }, 150)
    }
  }

  const handleAspectChange = (index: number) => {
    setAspectIndex(index)
    setShowAspectMenu(false)
  }

  // ===== 响应式视频容器尺寸计算 =====
  const wrapperRef = useRef<HTMLDivElement>(null)
  const [videoSize, setVideoSize] = useState({ width: 0, height: 0 })

  const computeSize = useCallback(() => {
    const el = wrapperRef.current
    if (!el) return
    const parent = el.parentElement
    if (!parent) return

    const pw = parent.clientWidth
    const ph = parent.clientHeight
    const r = currentAspect.ratio

    let w: number, h: number
    if (pw / ph > r) {
      // 父容器更宽 → 以高度为基准
      h = ph
      w = h * r
    } else {
      // 父容器更高或正合适 → 以宽度为基准
      w = pw
      h = w / r
    }

    // 留一点边距，避免贴边
    const margin = 16
    w = Math.min(w, pw - margin)
    h = Math.min(h, ph - margin)

    // 确保不为负
    w = Math.max(0, w)
    h = Math.max(0, h)

    setVideoSize({ width: w, height: h })
  }, [currentAspect.ratio])

  useEffect(() => {
    computeSize()
    const ro = new ResizeObserver(computeSize)
    const el = wrapperRef.current?.parentElement
    if (el) ro.observe(el)
    return () => ro.disconnect()
  }, [computeSize])

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* 视频预览区 */}
      <div className="flex-1 relative flex items-center justify-center overflow-hidden min-h-0"
        style={{ background: '#000' }}
      >
        {/* 网格背景 */}
        <div className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />

        {/* 核心视频容器 — 严格根据父容器尺寸计算，永不溢出 */}
        <div
          ref={wrapperRef}
          className="relative z-10"
          style={{
            width: videoSize.width,
            height: videoSize.height,
            minWidth: 0,
            minHeight: 0,
          }}
        >
          {/* 视频外框 + 安全框 + 内容 — 共用同一尺寸 */}
          <div
            className="relative w-full h-full overflow-hidden"
            style={{
              background: 'var(--bg-elevated)',
              border: `1px solid var(--film-edge)`,
            }}
          >
            {/* 安全框参考线 */}
            <div className="absolute inset-0 pointer-events-none">
              {/* 中心十字 */}
              <div className="absolute inset-0 flex items-center justify-center opacity-[0.08]">
                <div className="w-full h-px bg-white" />
              </div>
              <div className="absolute inset-0 flex items-center justify-center opacity-[0.08]">
                <div className="h-full w-px bg-white" />
              </div>
              {/* 三分线 */}
              <div className="absolute left-1/3 top-0 bottom-0 w-px bg-white/[0.05]" />
              <div className="absolute right-1/3 top-0 bottom-0 w-px bg-white/[0.05]" />
              <div className="absolute top-1/3 left-0 right-0 h-px bg-white/[0.05]" />
              <div className="absolute bottom-1/3 left-0 right-0 h-px bg-white/[0.05]" />
            </div>

            {/* 中心占位 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="w-14 h-14 rounded-xl mx-auto mb-2 flex items-center justify-center"
                  style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid var(--film-edge)`, borderRadius: 'var(--radius-lens)' }}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="1.5">
                    <rect x="2" y="2" width="20" height="20" rx="4" />
                    <path d="M10 8l6 4-6 4V8z" />
                  </svg>
                </div>
                <p className="text-text-tertiary text-[11px]">视频预览区域</p>
                <p className="text-text-muted text-[10px] mt-0.5 font-mono">{currentAspect.resolution} · 15s</p>
              </div>
            </div>

            {/* 播放按钮覆盖 */}
            <button
              onClick={togglePlay}
              className="absolute inset-0 flex items-center justify-center z-20 group"
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${isPlaying ? 'opacity-0 group-hover:opacity-100' : 'opacity-100'}`}
                style={{
                  background: 'rgba(0,0,0,0.6)',
                  backdropFilter: 'blur(4px)',
                }}
              >
                {isPlaying ? (
                  <PauseIcon size={18} color="white" />
                ) : (
                  <PlayIcon size={18} color="white" />
                )}
              </div>
            </button>
          </div>
        </div>

        {/* 时间码 */}
        <div className="absolute top-3 left-3 px-2 py-1 rounded text-xs font-mono z-20"
          style={{ background: 'rgba(0,0,0,0.6)', color: 'var(--text-secondary)' }}
        >
          {String(Math.floor(progress * 0.15)).padStart(2, '0')}:{String(Math.floor((progress * 0.15 % 1) * 60)).padStart(2, '0')} / 00:15
        </div>

        {/* 尺寸切换器 */}
        <div className="absolute top-3 right-3 z-20" ref={menuRef}>
          <button
            onClick={() => setShowAspectMenu(!showAspectMenu)}
            className="px-2 py-1 rounded text-[11px] font-mono font-medium transition-colors hover:bg-white/10"
            style={{ background: 'rgba(0,0,0,0.6)', color: 'var(--text-secondary)' }}
          >
            {currentAspect.label}
          </button>

          {showAspectMenu && (
            <div className="absolute top-full right-0 mt-1.5 rounded-lg overflow-hidden py-1 min-w-[120px]"
              style={{
                background: 'var(--bg-elevated)',
                border: `1px solid var(--slate-mark)`,
                borderRadius: 'var(--radius-slate)',
                boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
              }}
            >
              {aspectPresets.map((preset, index) => (
                <button
                  key={preset.label}
                  onClick={() => handleAspectChange(index)}
                  className="w-full px-3 py-1.5 text-left text-xs transition-colors hover:bg-white/5 flex items-center justify-between"
                  style={{
                    color: index === aspectIndex ? 'var(--brand)' : 'var(--text-secondary)',
                  }}
                >
                  <span className="font-mono font-medium">{preset.label}</span>
                  <span className="text-[10px] font-mono opacity-50">{preset.resolution}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 播放控制栏 */}
      <div className="h-12 flex items-center gap-3 px-4 shrink-0"
        style={{ background: 'var(--bg-base)', borderTop: `1px solid var(--film-edge)` }}
      >
        <button onClick={togglePlay} className="text-text-secondary hover:text-text-primary transition-colors">
          {isPlaying ? (
            <PauseIcon size={18} color="currentColor" />
          ) : (
            <PlayIcon size={18} color="currentColor" />
          )}
        </button>

        <div className="flex-1 h-1 rounded-full overflow-hidden cursor-pointer"
          style={{ background: 'rgba(255,255,255,0.08)' }}
          onClick={e => {
            const rect = e.currentTarget.getBoundingClientRect()
            setProgress(((e.clientX - rect.left) / rect.width) * 100)
          }}
        >
          <div className="h-full rounded-full transition-all duration-100"
            style={{
              width: `${progress}%`,
              background: 'var(--brand)',
            }}
          />
        </div>

        <span className="text-xs font-mono text-text-tertiary w-10 text-right">
          {Math.round(progress)}%
        </span>

        {/* 当前比例标识 */}
        <div className="px-1.5 py-0.5 rounded text-[10px] font-mono"
          style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)' }}
        >
          {currentAspect.label}
        </div>
      </div>
    </div>
  )
}
