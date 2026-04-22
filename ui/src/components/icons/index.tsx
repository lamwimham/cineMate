import React from 'react'

export interface IconProps {
  size?: number
  className?: string
  color?: string
}

// ============================================================
// Brand Logo - 放映机光束（晕染效果）
// 与 favicon-large.svg 完全一致
// ============================================================

export const LogoIcon: React.FC<IconProps> = ({ size = 24, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 512 512" fill="none" className={className}>
    <defs>
      <radialGradient id="bg" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#1a1a2e" />
        <stop offset="100%" stopColor="#050508" />
      </radialGradient>
      <radialGradient id="beamCore" cx="50%" cy="80%" r="60%">
        <stop offset="0%" stopColor="#f5c542" stopOpacity="0.9" />
        <stop offset="30%" stopColor="#f5a623" stopOpacity="0.6" />
        <stop offset="70%" stopColor="#f59e0b" stopOpacity="0.15" />
        <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
      </radialGradient>
      <linearGradient id="beamRise" x1="50%" y1="100%" x2="50%" y2="20%">
        <stop offset="0%" stopColor="#f5c542" stopOpacity="0.8" />
        <stop offset="50%" stopColor="#f5a623" stopOpacity="0.35" />
        <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
      </linearGradient>
      <radialGradient id="coldHaze" cx="50%" cy="75%" r="50%">
        <stop offset="0%" stopColor="#e8e4d9" stopOpacity="0.4" />
        <stop offset="60%" stopColor="#d4d0c4" stopOpacity="0.1" />
        <stop offset="100%" stopColor="#f5f0e8" stopOpacity="0" />
      </radialGradient>
      <radialGradient id="lensHaze" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#f5c542" stopOpacity="0.7" />
        <stop offset="35%" stopColor="#f5a623" stopOpacity="0.3" />
        <stop offset="70%" stopColor="#e8e4d9" stopOpacity="0.08" />
        <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
      </radialGradient>
      <radialGradient id="letterHaze" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#f5c542" stopOpacity="0.5" />
        <stop offset="60%" stopColor="#f5a623" stopOpacity="0.15" />
        <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
      </radialGradient>
      <radialGradient id="outerHaze" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#f5c542" stopOpacity="0.12" />
        <stop offset="50%" stopColor="#f5a623" stopOpacity="0.04" />
        <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
      </radialGradient>
      <filter id="heavyBlur" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="24" />
      </filter>
      <filter id="mediumBlur" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="12" />
      </filter>
      <filter id="lightBlur" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="6" />
      </filter>
      <clipPath id="beamClip">
        <polygon points="220,420 292,420 320,100 192,100" />
      </clipPath>
    </defs>

    {/* 背景 */}
    <rect width="512" height="512" rx="96" fill="url(#bg)" />

    {/* 外圈光晕 */}
    <circle cx="256" cy="256" r="180" fill="url(#outerHaze)" filter="url(#heavyBlur)" />

    {/* 光束 */}
    <g clipPath="url(#beamClip)">
      <rect x="160" y="80" width="192" height="360" fill="url(#beamRise)" filter="url(#heavyBlur)" opacity="0.7" />
      <rect x="200" y="80" width="112" height="360" fill="url(#beamRise)" filter="url(#mediumBlur)" opacity="0.5" />
      <rect x="220" y="80" width="72" height="360" fill="url(#coldHaze)" filter="url(#lightBlur)" opacity="0.4" />
      <rect x="244" y="80" width="24" height="360" fill="#fff8e7" opacity="0.35" filter="url(#mediumBlur)" />
      <circle cx="248" cy="220" r="4" fill="#f5f0e8" opacity="0.6" filter="url(#lightBlur)" />
      <circle cx="268" cy="250" r="3" fill="#f5f0e8" opacity="0.4" filter="url(#lightBlur)" />
      <circle cx="240" cy="290" r="3.5" fill="#f5f0e8" opacity="0.5" filter="url(#lightBlur)" />
      <circle cx="276" cy="190" r="2.5" fill="#f5f0e8" opacity="0.35" filter="url(#lightBlur)" />
      <circle cx="244" cy="160" r="3" fill="#f5f0e8" opacity="0.45" filter="url(#lightBlur)" />
      <circle cx="260" cy="340" r="4" fill="#f5f0e8" opacity="0.55" filter="url(#lightBlur)" />
      <circle cx="284" cy="280" r="2.5" fill="#f5f0e8" opacity="0.4" filter="url(#lightBlur)" />
    </g>

    {/* 镜头 */}
    <circle cx="256" cy="340" r="100" fill="none" stroke="#3a3a5e" strokeWidth="40" opacity="0.15" filter="url(#heavyBlur)" />
    <circle cx="256" cy="340" r="75" fill="url(#lensHaze)" filter="url(#heavyBlur)" opacity="0.8" />
    <circle cx="256" cy="340" r="40" fill="#f5c542" opacity="0.5" filter="url(#mediumBlur)" />
    <circle cx="256" cy="340" r="18" fill="#fff8e7" opacity="0.7" filter="url(#lightBlur)" />
    <circle cx="256" cy="340" r="6" fill="#fff8e7" opacity="0.9" />
    <ellipse cx="242" cy="328" rx="12" ry="6" fill="white" opacity="0.25" transform="rotate(-20 242 328)" filter="url(#lightBlur)" />

    {/* C 字母光晕 */}
    <circle cx="256" cy="340" r="45" fill="url(#letterHaze)" filter="url(#mediumBlur)" opacity="0.4" />

    {/* 胶片齿孔 */}
    <circle cx="208" cy="445" r="6" fill="#4a4a6e" opacity="0.2" filter="url(#lightBlur)" />
    <circle cx="256" cy="445" r="6" fill="#4a4a6e" opacity="0.2" filter="url(#lightBlur)" />
    <circle cx="304" cy="445" r="6" fill="#4a4a6e" opacity="0.2" filter="url(#lightBlur)" />
  </svg>
)

// ============================================================
// DAG Node Icons - 电影制作风格
// ============================================================

export const ScriptIcon: React.FC<IconProps> = ({ size = 20, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 剧本页 - 带场记板元素 */}
    <rect x="4" y="3" width="16" height="18" rx="2" stroke={color} strokeWidth="1.5" />
    {/* 场记板条纹 */}
    <path d="M4 7h16M4 7l2-4M9 7l2-4M14 7l2-4M19 7l1-2" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    {/* 文字行 */}
    <path d="M7 11h10M7 14h8M7 17h6" stroke={color} strokeWidth="1.2" strokeLinecap="round" opacity="0.6" />
  </svg>
)

export const StoryboardIcon: React.FC<IconProps> = ({ size = 20, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 分镜板 - 三格画面 */}
    <rect x="2" y="4" width="20" height="16" rx="2" stroke={color} strokeWidth="1.5" />
    <path d="M2 9h20M8 4v16M16 4v16" stroke={color} strokeWidth="1.2" />
    {/* 第一格：山/场景 */}
    <path d="M4 12l2-2 2 2" stroke={color} strokeWidth="1" strokeLinecap="round" opacity="0.5" />
    {/* 第二格：人物 */}
    <circle cx="12" cy="12" r="1.5" stroke={color} strokeWidth="1" opacity="0.5" />
    <path d="M12 13.5v2" stroke={color} strokeWidth="1" opacity="0.5" />
    {/* 第三格：产品 */}
    <rect x="17.5" y="11" width="3" height="4" rx="0.5" stroke={color} strokeWidth="1" opacity="0.5" />
  </svg>
)

export const VideoGenIcon: React.FC<IconProps> = ({ size = 20, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 摄像机机身 */}
    <rect x="3" y="7" width="14" height="10" rx="2" stroke={color} strokeWidth="1.5" />
    {/* 镜头 */}
    <circle cx="10" cy="12" r="3" stroke={color} strokeWidth="1.5" />
    <circle cx="10" cy="12" r="1.5" stroke={color} strokeWidth="1" opacity="0.6" />
    {/* 取景器 */}
    <path d="M17 10l4-2v8l-4-2" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
    {/* 录制红点 */}
    <circle cx="6" cy="9.5" r="1" fill="#ef4444" />
  </svg>
)

export const VoiceoverIcon: React.FC<IconProps> = ({ size = 20, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 麦克风 */}
    <rect x="9" y="3" width="6" height="10" rx="3" stroke={color} strokeWidth="1.5" />
    <path d="M6 11v1a6 6 0 0012 0v-1" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    <path d="M12 17v3M9 20h6" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    {/* 声波 */}
    <path d="M4 10c0-1 .5-2 1-2M19 10c0-1-.5-2-1-2" stroke={color} strokeWidth="1.2" opacity="0.4" />
    <path d="M2 9c0-2 1-3 1.5-3M21 9c0-2-1-3-1.5-3" stroke={color} strokeWidth="1.2" opacity="0.4" />
  </svg>
)

export const ComposeIcon: React.FC<IconProps> = ({ size = 20, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 合成 = 层叠 + 魔法星星 */}
    {/* 底层 */}
    <rect x="4" y="10" width="16" height="10" rx="1.5" stroke={color} strokeWidth="1.5" opacity="0.4" />
    {/* 中层 */}
    <rect x="6" y="7" width="12" height="8" rx="1.5" stroke={color} strokeWidth="1.5" opacity="0.7" />
    {/* 顶层 */}
    <rect x="8" y="4" width="8" height="6" rx="1.5" stroke={color} strokeWidth="1.5" />
    {/* 星星 */}
    <path d="M18 4l.5 1.5L20 6l-1.5.5L18 8l-.5-1.5L16 6l1.5-.5z" fill={color} opacity="0.9" />
  </svg>
)

// ============================================================
// Status Icons
// ============================================================

export const SuccessIcon: React.FC<IconProps> = ({ size = 16, className = '', color = '#22c55e' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 场记板闭合 = 完成 */}
    <rect x="3" y="10" width="18" height="10" rx="2" stroke={color} strokeWidth="1.5" />
    <path d="M3 10l2-4h14l2 4" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M6 6l1.5-3h9l1.5 3" stroke={color} strokeWidth="1.5" strokeLinejoin="round" opacity="0.5" />
    <path d="M8 14l3 3 5-5" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

export const FailedIcon: React.FC<IconProps> = ({ size = 16, className = '', color = '#ef4444' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 断裂的胶片 */}
    <rect x="3" y="6" width="8" height="12" rx="1" stroke={color} strokeWidth="1.5" />
    <rect x="13" y="6" width="8" height="12" rx="1" stroke={color} strokeWidth="1.5" />
    {/* 齿孔 */}
    <circle cx="5.5" cy="9" r="0.8" fill={color} opacity="0.6" />
    <circle cx="5.5" cy="15" r="0.8" fill={color} opacity="0.6" />
    <circle cx="18.5" cy="9" r="0.8" fill={color} opacity="0.6" />
    <circle cx="18.5" cy="15" r="0.8" fill={color} opacity="0.6" />
    {/* 断裂标记 */}
    <path d="M10 12h4M11 10l-1 4M13 10l1 4" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

export const ExecutingIcon: React.FC<IconProps> = ({ size = 16, className = '', color = '#f59e0b' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 旋转的胶片盘 */}
    <circle cx="12" cy="12" r="9" stroke={color} strokeWidth="1.5" opacity="0.3" />
    <circle cx="12" cy="12" r="3" stroke={color} strokeWidth="1.5" />
    {/* 齿孔旋转 */}
    <circle cx="12" cy="5" r="1" fill={color} />
    <circle cx="17" cy="8.5" r="1" fill={color} opacity="0.7" />
    <circle cx="17" cy="15.5" r="1" fill={color} opacity="0.5" />
    <circle cx="12" cy="19" r="1" fill={color} opacity="0.3" />
    <circle cx="7" cy="15.5" r="1" fill={color} opacity="0.5" />
    <circle cx="7" cy="8.5" r="1" fill={color} opacity="0.7" />
    {/* 录制红点 */}
    <circle cx="12" cy="12" r="1.2" fill={color} />
  </svg>
)

export const QueuedIcon: React.FC<IconProps> = ({ size = 16, className = '', color = '#3b82f6' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 队列 = 堆叠的胶片帧 */}
    <rect x="6" y="14" width="12" height="6" rx="1" stroke={color} strokeWidth="1.5" opacity="0.3" />
    <rect x="5" y="11" width="12" height="6" rx="1" stroke={color} strokeWidth="1.5" opacity="0.6" />
    <rect x="4" y="8" width="12" height="6" rx="1" stroke={color} strokeWidth="1.5" />
    {/* 齿孔 */}
    <circle cx="6" cy="11" r="0.6" fill={color} opacity="0.5" />
    <circle cx="6" cy="14" r="0.6" fill={color} opacity="0.5" />
  </svg>
)

export const PendingIcon: React.FC<IconProps> = ({ size = 16, className = '', color = '#475569' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 等待 = 空白胶片帧 */}
    <rect x="5" y="5" width="14" height="14" rx="2" stroke={color} strokeWidth="1.5" opacity="0.5" />
    {/* 齿孔 */}
    <circle cx="7" cy="9" r="0.8" fill={color} opacity="0.3" />
    <circle cx="7" cy="15" r="0.8" fill={color} opacity="0.3" />
    <circle cx="17" cy="9" r="0.8" fill={color} opacity="0.3" />
    <circle cx="17" cy="15" r="0.8" fill={color} opacity="0.3" />
    {/* 倒计时点 */}
    <circle cx="12" cy="12" r="2" stroke={color} strokeWidth="1.2" opacity="0.5" />
  </svg>
)

export const SkippedIcon: React.FC<IconProps> = ({ size = 16, className = '', color = '#6366f1' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 跳过 = 循环箭头 + 胶片 */}
    <path d="M18 8c0-3-2.5-5-5.5-5S7 5 7 8v2" stroke={color} strokeWidth="1.5" strokeLinecap="round" fill="none" />
    <path d="M6 8l3 2.5L6 13" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <rect x="10" y="12" width="8" height="6" rx="1" stroke={color} strokeWidth="1.5" />
    <path d="M10 15h8" stroke={color} strokeWidth="1" opacity="0.4" />
  </svg>
)

// ============================================================
// Navigation Icons
// ============================================================

export const GitIcon: React.FC<IconProps> = ({ size = 18, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* Git + 胶片齿孔元素 */}
    <circle cx="6" cy="6" r="2" stroke={color} strokeWidth="1.5" />
    <circle cx="18" cy="6" r="2" stroke={color} strokeWidth="1.5" />
    <circle cx="6" cy="18" r="2" stroke={color} strokeWidth="1.5" />
    <path d="M6 8v8M6 12h6a3 3 0 003-3V8" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    {/* 胶片齿孔装饰 */}
    <circle cx="22" cy="6" r="0.8" fill={color} opacity="0.4" />
    <circle cx="22" cy="12" r="0.8" fill={color} opacity="0.4" />
    <circle cx="22" cy="18" r="0.8" fill={color} opacity="0.4" />
  </svg>
)

export const AssetsIcon: React.FC<IconProps> = ({ size = 18, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 胶片盒/资产库 */}
    <rect x="3" y="5" width="18" height="14" rx="2" stroke={color} strokeWidth="1.5" />
    <path d="M3 9h18" stroke={color} strokeWidth="1.5" />
    {/* 胶片轴 */}
    <circle cx="8" cy="14" r="2.5" stroke={color} strokeWidth="1.2" />
    <circle cx="16" cy="14" r="2.5" stroke={color} strokeWidth="1.2" />
    {/* 齿孔 */}
    <circle cx="6" cy="7.5" r="0.5" fill={color} opacity="0.5" />
    <circle cx="9" cy="7.5" r="0.5" fill={color} opacity="0.5" />
    <circle cx="12" cy="7.5" r="0.5" fill={color} opacity="0.5" />
  </svg>
)

export const DirectorIcon: React.FC<IconProps> = ({ size = 18, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* 导演 = 场记板 */}
    <rect x="4" y="6" width="16" height="12" rx="1.5" stroke={color} strokeWidth="1.5" />
    <path d="M4 10h16" stroke={color} strokeWidth="1.5" />
    {/* 条纹 */}
    <path d="M4 10l1.5-4M8 10l1.5-4M12 10l1.5-4M16 10l1.5-4" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    {/* 导演星 */}
    <path d="M12 13l.8 1.6 1.7.2-1.2 1.2.3 1.7-1.5-.8-1.5.8.3-1.7-1.2-1.2 1.7-.2z" fill={color} opacity="0.8" />
  </svg>
)

export const SearchIcon: React.FC<IconProps> = ({ size = 14, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2" strokeLinecap="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
)

export const SendIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9" />
  </svg>
)

export const PlayIcon: React.FC<IconProps> = ({ size = 18, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} className={className}>
    <path d="M8 5v14l11-7z" />
  </svg>
)

export const PauseIcon: React.FC<IconProps> = ({ size = 18, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} className={className}>
    <rect x="6" y="4" width="4" height="16" rx="1" />
    <rect x="14" y="4" width="4" height="16" rx="1" />
  </svg>
)

export const DagGraphIcon: React.FC<IconProps> = ({ size = 14, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="5" r="3" />
    <circle cx="5" cy="19" r="3" />
    <circle cx="19" cy="19" r="3" />
    <line x1="12" y1="8" x2="5" y2="16" />
    <line x1="12" y1="8" x2="19" y2="16" />
  </svg>
)

export const ChevronRightIcon: React.FC<IconProps> = ({ size = 14, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="9 18 15 12 9 6" />
  </svg>
)

export const TypeIcon: React.FC<{ type: 'image' | 'video' | 'audio'; size?: number }> = ({ type, size = 14 }) => {
  const colors = {
    image: '#818cf8',
    video: '#60a5fa',
    audio: '#4ade80',
  }
  const color = colors[type]

  if (type === 'image') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <path d="M21 15l-5-5L5 21" />
      </svg>
    )
  }
  if (type === 'video') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <rect x="2" y="6" width="16" height="12" rx="2" />
        <path d="M18 10l4-2v8l-4-2" />
        <circle cx="8" cy="10" r="1" fill={color} />
      </svg>
    )
  }
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
      <path d="M12 2a3 3 0 00-3 3v14a3 3 0 003 3 3 3 0 003-3V5a3 3 0 00-3-3z" />
      <path d="M19 10v4M22 8v8" strokeLinecap="round" />
    </svg>
  )
}

// ============================================================
// Option / Content Icons - 电影制作语义
// ============================================================

export const CloseupIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 特写镜头 - 取景框 + 中心聚焦 */}
    <rect x="4" y="4" width="16" height="16" rx="2" />
    <circle cx="12" cy="12" r="3" />
    <path d="M12 8V6M12 18v-2M8 12H6M18 12h-2" />
  </svg>
)

export const SceneIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 场景展示 - 城市天际线 */}
    <path d="M3 20h18" />
    <path d="M5 20v-8h4v8" />
    <path d="M11 20V6h6v14" />
    <path d="M9 14h2M14 10h2" />
  </svg>
)

export const HybridIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 混合模式 - 叠加图层 */}
    <rect x="5" y="5" width="10" height="10" rx="1" opacity="0.5" />
    <rect x="9" y="9" width="10" height="10" rx="1" />
    <path d="M11 9V5M19 13h-2M15 17v2" />
  </svg>
)

export const NeonIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 霓虹灯 - 发光管 */}
    <path d="M4 8h16" />
    <path d="M6 12h12" />
    <path d="M8 16h8" />
    <circle cx="3" cy="8" r="1" fill={color} />
    <circle cx="21" cy="8" r="1" fill={color} />
    <circle cx="5" cy="12" r="1" fill={color} />
    <circle cx="19" cy="12" r="1" fill={color} />
    <circle cx="7" cy="16" r="1" fill={color} />
    <circle cx="17" cy="16" r="1" fill={color} />
  </svg>
)

export const RainIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 雨夜 - 云 + 雨滴 */}
    <path d="M6 10a4 4 0 118 0 3 3 0 013 3" />
    <path d="M8 14v2M12 14v3M16 14v2" strokeDasharray="2 2" />
  </svg>
)

export const FogIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 雾气 - 波浪线 */}
    <path d="M3 8h6M13 8h8" opacity="0.4" />
    <path d="M3 12h4M10 12h11" opacity="0.7" />
    <path d="M3 16h8M14 16h7" opacity="0.4" />
  </svg>
)

export const FlyingIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 飞行器 - 航拍无人机 */}
    <path d="M4 10h16M4 10l-1-3M20 10l1-3" />
    <rect x="9" y="10" width="6" height="4" rx="1" />
    <path d="M12 14v4M10 18h4" />
  </svg>
)

export const HologramIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 全息投影 - 金字塔/棱镜 */}
    <path d="M12 3l9 16H3z" opacity="0.3" />
    <path d="M12 3v16" />
    <path d="M8 11l4-2 4 2" />
    <circle cx="12" cy="12" r="1" fill={color} />
  </svg>
)

export const CheckIcon: React.FC<IconProps> = ({ size = 14, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2.5" strokeLinecap="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
)

export const FramePlaceholderIcon: React.FC<IconProps> = ({ size = 24, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    {/* 画框占位 - 带齿孔的胶片帧 */}
    <rect x="3" y="5" width="18" height="14" rx="1" />
    <circle cx="5" cy="9" r="0.6" fill={color} opacity="0.4" />
    <circle cx="5" cy="15" r="0.6" fill={color} opacity="0.4" />
    <circle cx="19" cy="9" r="0.6" fill={color} opacity="0.4" />
    <circle cx="19" cy="15" r="0.6" fill={color} opacity="0.4" />
    <circle cx="12" cy="12" r="3" opacity="0.3" />
    <path d="M10 12l1.5-1.5L14 12" />
  </svg>
)

// ============================================================
// Input / Action Icons
// ============================================================

export const AttachmentIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2" strokeLinecap="round">
    <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
  </svg>
)

export const MicIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2" strokeLinecap="round">
    <path d="M12 2a3 3 0 00-3 3v7a3 3 0 006 0V5a3 3 0 00-3-3z" />
    <path d="M19 10v2a7 7 0 01-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="22" />
  </svg>
)

export const StopIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} className={className}>
    <rect x="6" y="6" width="12" height="12" rx="2" />
  </svg>
)

export const XIcon: React.FC<IconProps> = ({ size = 14, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="2.5" strokeLinecap="round">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

export const ImageIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    <rect x="3" y="3" width="18" height="18" rx="2" />
    <circle cx="8.5" cy="8.5" r="1.5" />
    <path d="M21 15l-5-5L5 21" />
  </svg>
)

export const FileTextIcon: React.FC<IconProps> = ({ size = 16, className = '', color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} stroke={color} strokeWidth="1.5" strokeLinecap="round">
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <polyline points="10 9 9 9 8 9" />
  </svg>
)
