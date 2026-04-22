import type { ChatMessage } from '../../types/chat'
import SingleChoice from './SingleChoice'
import MultiChoice from './MultiChoice'
import ImageSelect from './ImageSelect'
import AssetGalleryMessage from './AssetGalleryMessage'

interface MessageRendererProps {
  message: ChatMessage
  onInteract?: (messageId: string, data: unknown) => void
}

export default function MessageRenderer({ message, onInteract }: MessageRendererProps) {
  const isUser = message.role === 'user'

  // 用户消息始终渲染为文本
  if (isUser) {
    return (
      <div className="flex justify-end">
        <div
          className="max-w-[85%] px-3.5 py-2.5 chat-bubble-user"
          style={{ borderRadius: 'var(--radius-lens) var(--radius-lens) var(--radius-slate) var(--radius-lens)' }}
        >
          <p className="text-sm text-text-primary whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>
        </div>
      </div>
    )
  }

  // AI 消息根据类型渲染
  const renderContent = () => {
    switch (message.type) {
      case 'single_choice':
        return (
          <SingleChoice
            question={message.content}
            options={message.options || []}
            selectedId={message.selectedIds?.[0]}
            submitted={message.submitted}
            onSubmit={(id) => onInteract?.(message.id, { type: 'single_choice', selectedIds: [id] })}
          />
        )

      case 'multi_choice':
        return (
          <MultiChoice
            question={message.content}
            options={message.options || []}
            maxSelect={message.maxSelect}
            selectedIds={message.selectedIds}
            submitted={message.submitted}
            onSubmit={(ids) => onInteract?.(message.id, { type: 'multi_choice', selectedIds: ids })}
          />
        )

      case 'image_select':
        return (
          <ImageSelect
            question={message.content}
            images={message.images || []}
            maxSelect={message.maxSelect || 1}
            selectedIds={message.selectedIds}
            submitted={message.submitted}
            onSubmit={(ids) => onInteract?.(message.id, { type: 'image_select', selectedIds: ids })}
          />
        )

      case 'asset_gallery':
        return (
          <AssetGalleryMessage
            title={message.content}
            assets={message.assets || []}
            onSelect={(id) => onInteract?.(message.id, { type: 'asset_select', assetId: id })}
          />
        )

      case 'clarification':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded"
                style={{ background: 'var(--warning-glow)', color: 'var(--warning)' }}
              >
                需求澄清
              </span>
            </div>
            <p className="text-sm text-text-primary whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
          </div>
        )

      default:
        return (
          <p className="text-sm text-text-primary whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>
        )
    }
  }

  return (
    <div className="flex justify-start">
      <div
        className="max-w-[90%] px-3.5 py-3 chat-bubble-ai"
        style={{ borderRadius: 'var(--radius-lens) var(--radius-lens) var(--radius-lens) var(--radius-slate)' }}
      >
        {renderContent()}
        <span className="text-[10px] text-text-muted mt-1.5 block text-right font-mono">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  )
}
