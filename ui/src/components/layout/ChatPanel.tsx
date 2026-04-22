import { useState, useRef, useEffect, useCallback } from 'react'
import MessageRenderer from '../chat/MessageRenderer'
import {
  DirectorIcon, SendIcon,
  CloseupIcon, SceneIcon, HybridIcon,
  NeonIcon, RainIcon, FogIcon, FlyingIcon, HologramIcon,
  AttachmentIcon, MicIcon, StopIcon, XIcon, ImageIcon, FileTextIcon,
} from '../icons'
import type { ChatMessage } from '../../types/chat'

const demoMessages: ChatMessage[] = [
  {
    id: '1',
    role: 'ai',
    type: 'text',
    content: '你好！我是 Director Agent。你想创建什么样的视频？可以描述场景、风格、时长等。',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    id: '2',
    role: 'user',
    type: 'text',
    content: '帮我做一个赛博朋克风格的 15 秒产品广告',
    timestamp: new Date(Date.now() - 1000 * 60 * 25),
  },
  {
    id: '3',
    role: 'ai',
    type: 'single_choice',
    content: '为了更好地为你生成视频，请选择你想要的产品展示方式：',
    options: [
      { id: 'closeup', label: '产品特写', description: '聚焦产品细节，突出质感', icon: <CloseupIcon size={16} /> },
      { id: 'scene', label: '场景展示', description: '产品在真实环境中使用', icon: <SceneIcon size={16} /> },
      { id: 'hybrid', label: '混合模式', description: '特写 + 场景交替', icon: <HybridIcon size={16} /> },
    ],
    timestamp: new Date(Date.now() - 1000 * 60 * 20),
  },
  {
    id: '4',
    role: 'user',
    type: 'text',
    content: '选择：混合模式',
    timestamp: new Date(Date.now() - 1000 * 60 * 18),
  },
  {
    id: '5',
    role: 'ai',
    type: 'multi_choice',
    content: '请选择视频中需要出现的元素（最多选 3 项）：',
    options: [
      { id: 'neon', label: '霓虹灯牌', icon: <NeonIcon size={16} /> },
      { id: 'rain', label: '雨夜效果', icon: <RainIcon size={16} /> },
      { id: 'fog', label: '烟雾/雾气', icon: <FogIcon size={16} /> },
      { id: 'flying', label: '飞行器', icon: <FlyingIcon size={16} /> },
      { id: 'hologram', label: '全息投影', icon: <HologramIcon size={16} /> },
    ],
    maxSelect: 3,
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
  },
  {
    id: '6',
    role: 'ai',
    type: 'image_select',
    content: '已生成 4 种风格参考图，请选择你最喜欢的视觉风格：',
    images: [
      { id: 'style1', url: '', label: '青橙高对比' },
      { id: 'style2', url: '', label: '粉紫霓虹' },
      { id: 'style3', url: '', label: '冷蓝科技' },
      { id: 'style4', url: '', label: '暖金复古' },
    ],
    timestamp: new Date(Date.now() - 1000 * 60 * 10),
  },
  {
    id: '7',
    role: 'ai',
    type: 'asset_gallery',
    content: 'Storyboard 已生成，以下是分镜预览：',
    assets: [
      {
        id: 'sb1', type: 'image', name: '开场全景', url: '', thumbnail: '',
        metadata: { createdAt: '14:30', cost: '¥0.5', dimensions: '1024×576' }
      },
      {
        id: 'sb2', type: 'image', name: '产品特写', url: '', thumbnail: '',
        metadata: { createdAt: '14:32', cost: '¥0.5', dimensions: '1024×576' }
      },
      {
        id: 'sb3', type: 'image', name: '场景过渡', url: '', thumbnail: '',
        metadata: { createdAt: '14:35', cost: '¥0.5', dimensions: '1024×576' }
      },
    ],
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
  {
    id: '8',
    role: 'ai',
    type: 'clarification',
    content: '正在生成视频片段... 预计耗时 12 秒。\n\n当前进度：\n• 脚本 ✅\n• 分镜 ✅\n• 视频生成 🔄 (75%)\n• 配音 ⏳\n• 合成 ⏳',
    timestamp: new Date(Date.now() - 1000 * 60 * 2),
  },
]

// 文件附件类型
interface Attachment {
  id: string
  file: File
  type: 'image' | 'text'
  preview?: string
}

// 检查浏览器是否支持 SpeechRecognition
const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>(demoMessages)
  const [input, setInput] = useState('')
  const [attachments, setAttachments] = useState<Attachment[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [isDragOver, setIsDragOver] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const recordingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const recognitionRef = useRef<any>(null)
  const inputAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const handleSend = useCallback(() => {
    if (!input.trim() && attachments.length === 0) return

    const content = input.trim() || `[${attachments.map(a => a.file.name).join(', ')}]`
    setMessages(prev => [...prev, {
      id: String(Date.now()),
      role: 'user',
      type: 'text',
      content,
      timestamp: new Date(),
    }])
    setInput('')
    setAttachments([])
  }, [input, attachments])

  const handleInteract = (messageId: string, data: unknown) => {
    const interaction = data as { type: string; selectedIds?: string[]; assetId?: string }
    setMessages(prev => prev.map(m => {
      if (m.id !== messageId) return m
      return {
        ...m,
        submitted: true,
        selectedIds: interaction.selectedIds || m.selectedIds,
      }
    }))

    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: String(Date.now()),
        role: 'ai',
        type: 'text',
        content: `收到！已记录你的选择：${interaction.selectedIds?.join(', ') || interaction.assetId}`,
        timestamp: new Date(),
      }])
    }, 600)
  }

  // ===== 文件上传 =====
  const processFiles = (files: FileList | null) => {
    if (!files) return
    const newAttachments: Attachment[] = []

    Array.from(files).forEach(file => {
      const type = file.type.startsWith('image/') ? 'image' : 'text'
      const attachment: Attachment = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        file,
        type,
      }

      if (type === 'image') {
        const reader = new FileReader()
        reader.onload = (e) => {
          attachment.preview = e.target?.result as string
          setAttachments(prev => [...prev])
        }
        reader.readAsDataURL(file)
      }

      newAttachments.push(attachment)
    })

    setAttachments(prev => [...prev, ...newAttachments])
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    processFiles(e.target.files)
    e.target.value = '' // 允许重复选择同一文件
  }

  const removeAttachment = (id: string) => {
    setAttachments(prev => prev.filter(a => a.id !== id))
  }

  // 拖拽上传
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    processFiles(e.dataTransfer.files)
  }

  // ===== 语音输入 =====
  const startRecording = () => {
    setIsRecording(true)
    setRecordingTime(0)

    // 计时器
    recordingTimerRef.current = setInterval(() => {
      setRecordingTime(t => t + 1)
    }, 1000)

    // 尝试使用 Web Speech API
    if (SpeechRecognitionAPI) {
      const recognition = new SpeechRecognitionAPI()
      recognition.lang = 'zh-CN'
      recognition.continuous = true
      recognition.interimResults = true

      recognition.onresult = (event: unknown) => {
        const e = event as SpeechRecognitionEvent
        const transcript = Array.from(e.results)
          .map(r => r[0].transcript)
          .join('')
        setInput(transcript)
      }

      recognition.onerror = () => {
        stopRecording()
      }

      recognition.onend = () => {
        stopRecording()
      }

      recognition.start()
      recognitionRef.current = recognition
    }
  }

  const stopRecording = () => {
    setIsRecording(false)

    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current)
      recordingTimerRef.current = null
    }

    if (recognitionRef.current) {
      recognitionRef.current.stop()
      recognitionRef.current = null
    }
  }

  // 格式化录音时间
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0')
    const s = (seconds % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  }

  const canSend = input.trim().length > 0 || attachments.length > 0

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 shrink-0 flex items-center justify-between"
        style={{ borderBottom: `1px solid var(--film-edge)` }}
      >
        <div className="flex items-center gap-2">
          <DirectorIcon size={18} color="var(--text-primary)" />
          <span className="text-sm-b text-text-primary">Director</span>
        </div>
        <span className="text-xs text-text-tertiary">Agent</span>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto custom-scroll p-4 space-y-4">
        {messages.map(msg => (
          <MessageRenderer
            key={msg.id}
            message={msg}
            onInteract={handleInteract}
          />
        ))}
      </div>

      {/* Input Area */}
      <div
        ref={inputAreaRef}
        className="p-3 shrink-0 relative"
        style={{
          borderTop: `1px solid var(--film-edge)`,
          background: isDragOver ? 'rgba(245,197,66,0.04)' : undefined,
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* 拖拽提示 */}
        {isDragOver && (
          <div className="absolute inset-0 z-50 flex items-center justify-center rounded-md m-2"
            style={{ border: `2px dashed var(--cine-gold)`, background: 'rgba(245,197,66,0.06)', borderRadius: 'var(--radius-slate)' }}
          >
            <span className="text-sm font-medium" style={{ color: 'var(--cine-gold)' }}>
              释放以上传文件
            </span>
          </div>
        )}

        {/* 附件预览 */}
        {attachments.length > 0 && (
          <div className="flex gap-2 overflow-x-auto pb-2 mb-2 custom-scroll">
            {attachments.map(att => (
              <div
                key={att.id}
                className="relative shrink-0 rounded-lg overflow-hidden group"
                style={{
                  width: att.type === 'image' ? 80 : 120,
                  height: 48,
                  border: `1px solid var(--slate-mark)`,
                  borderRadius: 'var(--radius-slate)',
                  background: 'var(--bg-base)',
                }}
              >
                {att.type === 'image' && att.preview ? (
                  <img src={att.preview} alt={att.file.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center gap-1.5 px-2">
                    {att.type === 'image' ? (
                      <ImageIcon size={14} color="var(--text-muted)" />
                    ) : (
                      <FileTextIcon size={14} color="var(--text-muted)" />
                    )}
                    <span className="text-[10px] text-text-secondary truncate">{att.file.name}</span>
                  </div>
                )}
                {/* 删除按钮 */}
                <button
                  onClick={() => removeAttachment(att.id)}
                  className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{ background: 'rgba(0,0,0,0.6)' }}
                >
                  <XIcon size={8} color="white" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* 录音状态条 */}
        {isRecording && (
          <div className="flex items-center gap-3 px-3 py-2 mb-2 rounded-lg"
            style={{ background: 'rgba(239,68,68,0.08)', border: `1px solid rgba(239,68,68,0.2)`, borderRadius: 'var(--radius-slate)' }}
          >
            <div className="w-3 h-3 rounded-full bg-error animate-pulse" />
            <span className="text-xs font-mono text-error">录音中</span>
            <span className="text-xs font-mono text-text-secondary">{formatTime(recordingTime)}</span>
            <div className="flex-1" />
            <button
              onClick={stopRecording}
              className="text-[11px] px-2 py-0.5 rounded text-white bg-error hover:opacity-90 transition-opacity"
            >
              停止
            </button>
          </div>
        )}

        {/* 输入行 */}
        <div className="flex items-end gap-2">
          {/* 附件按钮 */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors hover:bg-white/5"
            style={{ color: 'var(--text-tertiary)' }}
            title="上传文件"
          >
            <AttachmentIcon size={18} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept="image/*,.txt,.md,.json"
            multiple
            onChange={handleFileSelect}
          />

          {/* 文本输入 */}
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder={isRecording ? '正在聆听...' : '描述你的视频需求...'}
            disabled={isRecording}
            className="flex-1 min-h-[40px] max-h-[120px] px-3 py-2 text-sm resize-none outline-none transition-colors disabled:opacity-50"
            style={{
              background: 'var(--bg-base)',
              border: `1px solid var(--slate-mark)`,
              borderRadius: 'var(--radius-slate)',
              color: 'var(--text-primary)',
            }}
            onFocus={e => e.target.style.borderColor = 'var(--cine-gold)'}
            onBlur={e => e.target.style.borderColor = 'var(--slate-mark)'}
          />

          {/* 语音 / 发送按钮 */}
          {isRecording ? (
            <button
              onClick={stopRecording}
              className="w-10 h-10 rounded-lg flex items-center justify-center text-white transition-all hover:scale-105 active:scale-95 shrink-0"
              style={{ background: '#ef4444' }}
              title="停止录音"
            >
              <StopIcon size={16} color="white" />
            </button>
          ) : (
            <>
              <button
                onClick={startRecording}
                className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors hover:bg-white/5"
                style={{ color: 'var(--text-tertiary)' }}
                title="语音输入"
              >
                <MicIcon size={18} />
              </button>
              <button
                onClick={handleSend}
                disabled={!canSend}
                className="w-10 h-10 rounded-lg flex items-center justify-center text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed hover:scale-105 active:scale-95 shrink-0"
                style={{ background: 'var(--brand)' }}
              >
                <SendIcon size={16} color="white" />
              </button>
            </>
          )}
        </div>

        {/* 提示文字 */}
        <p className="text-[10px] text-text-muted mt-1.5 px-1">
          {isRecording
            ? '点击红色按钮停止录音'
            : '支持拖拽上传图片、文本文件 · 按 Enter 发送'}
        </p>
      </div>
    </div>
  )
}
