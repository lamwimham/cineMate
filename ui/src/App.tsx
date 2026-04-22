import { useState, useRef, useCallback, useEffect } from 'react'
import TopBar from './components/layout/TopBar'
import ChatPanel from './components/layout/ChatPanel'
import VideoCanvas from './components/layout/VideoCanvas'
import GitPanel from './components/layout/GitPanel'
import AssetPanel from './components/layout/AssetPanel'
import DagGraph from './components/dag/DagGraph'
import { DagGraphIcon } from './components/icons'
import type { DagNodeData } from './components/dag/DagNode'
import type { DagEdgeData } from './components/dag/DagEdge'

const demoNodes: DagNodeData[] = [
  { id: 'script', name: 'Script', status: 'succeeded', duration: '0.3s', cost: '¥0.1' },
  { id: 'storyboard', name: 'Storyboard', status: 'succeeded', duration: '1.2s', cost: '¥0.5' },
  { id: 'video', name: 'Video Gen', status: 'executing', progress: 75, duration: '12s', cost: '¥8.0' },
  { id: 'voice', name: 'Voiceover', status: 'queued', cost: '¥2.0' },
  { id: 'compose', name: 'Compose', status: 'pending', cost: '¥1.5' },
]

const demoEdges: DagEdgeData[] = [
  { id: 'e1', from: 'script', to: 'storyboard', status: 'active' },
  { id: 'e2', from: 'storyboard', to: 'video', status: 'active' },
  { id: 'e3', from: 'video', to: 'compose', status: 'idle' },
  { id: 'e4', from: 'storyboard', to: 'voice', status: 'idle' },
  { id: 'e5', from: 'voice', to: 'compose', status: 'idle' },
]

type RightTab = 'git' | 'assets' | null

const MIN_CHAT_WIDTH = 25
const MAX_CHAT_WIDTH = 60
const DEFAULT_CHAT_WIDTH = 40

function App() {
  const [rightTab, setRightTab] = useState<RightTab>(null)
  const [chatWidth, setChatWidth] = useState(DEFAULT_CHAT_WIDTH)
  const [isResizing, setIsResizing] = useState(false)
  const [isDagExpanded, setIsDagExpanded] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const resizeState = useRef({ startX: 0, startWidth: 0 })

  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsResizing(true)
    resizeState.current = { startX: e.clientX, startWidth: chatWidth }

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const container = containerRef.current
      if (!container) return
      const containerWidth = container.getBoundingClientRect().width
      const deltaX = moveEvent.clientX - resizeState.current.startX
      const deltaPercent = (deltaX / containerWidth) * 100
      const newWidth = Math.max(MIN_CHAT_WIDTH, Math.min(MAX_CHAT_WIDTH, resizeState.current.startWidth + deltaPercent))
      setChatWidth(newWidth)
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }, [chatWidth])

  // 拖拽时改变光标
  useEffect(() => {
    if (isResizing) {
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
    } else {
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
    return () => {
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isResizing])

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden" style={{ background: 'var(--bg-dark)' }}>
      <TopBar />

      <main className="flex flex-1 overflow-hidden">
        {/* 左侧大区域：Chat + Video + DAG */}
        <div className="flex flex-col flex-1 min-w-0" ref={containerRef}>
          {/* 上排：Chat + Video */}
          <div className="flex flex-1 overflow-hidden min-h-0">
            {/* ChatPanel — 宽度可拖拽 */}
            <div
              className="shrink-0"
              style={{ width: `${chatWidth}%`, borderRight: `1px solid var(--frame-line)` }}
            >
              <ChatPanel />
            </div>

            {/* 拖拽手柄 */}
            <div
              className="w-1.5 shrink-0 relative group"
              style={{
                cursor: 'col-resize',
                background: isResizing ? 'var(--brand)' : 'transparent',
              }}
              onMouseDown={handleResizeStart}
            >
              <div
                className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-[3px] rounded-full transition-colors"
                style={{
                  background: isResizing ? 'var(--brand)' : 'var(--divider)',
                }}
              />
              {/* 悬停时显示拖拽提示 */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-8 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ background: 'var(--bg-elevated)', border: `1px solid var(--slate-mark)`, borderRadius: 'var(--radius-slate)' }}
              >
                <div className="flex gap-[3px]">
                  <div className="w-[1px] h-3 rounded-full" style={{ background: 'var(--text-muted)' }} />
                  <div className="w-[1px] h-3 rounded-full" style={{ background: 'var(--text-muted)' }} />
                </div>
              </div>
            </div>

            {/* VideoCanvas */}
            <div className="flex-1 min-w-0 min-h-0">
              <VideoCanvas />
            </div>
          </div>

          {/* 底部 DAG：横跨 Chat + Video */}
          <div
            className="shrink-0 relative overflow-hidden transition-all duration-300 ease-out"
            style={{
              borderTop: `1px solid var(--frame-line-dim)`,
              background: 'var(--bg-darkest)',
              height: isDagExpanded ? 300 : 36,
              borderRadius: `0 0 var(--radius-frame) var(--radius-frame)`,
            }}
          >
            {/* 点阵网格背景（仅展开时显示） */}
            {isDagExpanded && (
              <div className="absolute inset-0 pointer-events-none opacity-[0.055]"
                style={{
                  backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.9) 1px, transparent 1px)',
                  backgroundSize: '20px 20px',
                }}
              />
            )}
            {/* 扫描线（仅展开时显示） */}
            {isDagExpanded && (
              <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.03]">
                <div className="w-full h-[1px]"
                  style={{
                    background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.6), transparent)',
                    animation: 'scanlineMove 5s linear infinite',
                  }}
                />
              </div>
            )}
            {/* 底部渐变遮罩（仅展开时显示） */}
            {isDagExpanded && (
              <div className="absolute bottom-0 left-0 right-0 h-8 pointer-events-none"
                style={{ background: 'linear-gradient(to top, var(--bg-darkest), transparent)' }}
              />
            )}

            {/* DAG Header — 可点击展开/折叠 */}
            <div
              className="h-9 px-4 flex items-center justify-between shrink-0 relative z-10 cursor-pointer select-none hover:bg-white/[0.02] transition-colors"
              style={{ borderBottom: isDagExpanded ? `1px solid var(--film-edge)` : 'none' }}
              onClick={() => setIsDagExpanded(!isDagExpanded)}
            >
              <div className="flex items-center gap-2">
                <DagGraphIcon size={14} color="var(--text-tertiary)" />
                <span className="text-[11px] font-mono font-semibold uppercase tracking-[0.15em]" style={{ color: 'var(--text-tertiary)' }}>
                  Pipeline DAG
                </span>
                {/* 展开/折叠指示器 */}
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="var(--text-muted)"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="transition-transform duration-300"
                  style={{ transform: isDagExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[11px] font-mono flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-warning animate-pulse" />
                  <span style={{ color: 'var(--warning)' }}>EXECUTING</span>
                </span>
                <span className="text-[11px] font-mono" style={{ color: 'var(--text-muted)' }}>3/5 nodes</span>
              </div>
            </div>

            {/* DAG Graph — 展开时显示 */}
            {isDagExpanded && (
              <div className="h-[calc(100%-36px)] overflow-auto custom-scroll relative z-10">
                <DagGraph nodes={demoNodes} edges={demoEdges} />
              </div>
            )}
          </div>
        </div>

        {/* 右侧 Icon 栏 + Tab 面板 */}
        <div className="flex shrink-0" style={{ borderLeft: `1px solid var(--frame-line)` }}>
          {/* Icon 导航栏 */}
          <div className="w-12 shrink-0 flex flex-col" style={{ background: 'var(--bg-dark)', borderRight: rightTab ? `1px solid var(--film-edge)` : 'none' }}>
            {/* Git 图标按钮 */}
            <button
              onClick={() => setRightTab(rightTab === 'git' ? null : 'git')}
              className="w-12 h-12 flex items-center justify-center transition-all relative"
              style={{
                background: rightTab === 'git' ? 'var(--bg-hover)' : 'transparent',
              }}
              title="Video Git"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={rightTab === 'git' ? 'var(--brand)' : 'var(--text-tertiary)'} strokeWidth="1.5" strokeLinecap="round">
                <circle cx="6" cy="6" r="2" />
                <circle cx="18" cy="6" r="2" />
                <circle cx="6" cy="18" r="2" />
                <path d="M6 8v8M6 12h6a3 3 0 003-3V8" />
              </svg>
              {rightTab === 'git' && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[2px] h-6 rounded-full" style={{ background: 'var(--brand)' }} />
              )}
            </button>

            {/* Assets 图标按钮 */}
            <button
              onClick={() => setRightTab(rightTab === 'assets' ? null : 'assets')}
              className="w-12 h-12 flex items-center justify-center transition-all relative"
              style={{
                background: rightTab === 'assets' ? 'var(--bg-hover)' : 'transparent',
              }}
              title="Assets"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={rightTab === 'assets' ? 'var(--brand)' : 'var(--text-tertiary)'} strokeWidth="1.5">
                <rect x="3" y="5" width="18" height="14" rx="2" />
                <path d="M3 9h18" />
                <circle cx="8" cy="14" r="2.5" />
                <circle cx="16" cy="14" r="2.5" />
              </svg>
              {rightTab === 'assets' && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[2px] h-6 rounded-full" style={{ background: 'var(--brand)' }} />
              )}
            </button>
          </div>

          {/* Tab 内容面板 */}
          {rightTab && (
            <div className="w-[280px] shrink-0 flex flex-col" style={{ background: 'var(--bg-base)' }}>
              <div className="flex-1 overflow-hidden">
                {rightTab === 'git' ? <GitPanel /> : <AssetPanel />}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
