import { useState } from 'react'
import { CheckIcon, FramePlaceholderIcon } from '../icons'
import type { ImageOption } from '../../types/chat'

interface ImageSelectProps {
  question: string
  images: ImageOption[]
  maxSelect?: number
  onSubmit: (selectedIds: string[]) => void
  submitted?: boolean
  selectedIds?: string[]
}

export default function ImageSelect({
  question,
  images,
  maxSelect = 1,
  onSubmit,
  submitted,
  selectedIds: initialSelected = [],
}: ImageSelectProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set(initialSelected))
  const isLocked = submitted

  const toggle = (id: string) => {
    if (isLocked) return
    const next = new Set(selected)
    if (next.has(id)) {
      next.delete(id)
    } else {
      if (maxSelect === 1) {
        next.clear()
        next.add(id)
      } else if (next.size < maxSelect) {
        next.add(id)
      }
    }
    setSelected(next)
  }

  const selectedArray = Array.from(selected)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-primary">{question}</p>
        {maxSelect > 1 && (
          <span className="text-[11px] font-mono text-text-muted">
            {selected.size}/{maxSelect}
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-2">
        {images.map(img => {
          const isSelected = selected.has(img.id)
          const isDisabled = isLocked && !isSelected

          return (
            <button
              key={img.id}
              disabled={isDisabled}
              onClick={() => toggle(img.id)}
              className={`
                relative rounded-xl overflow-hidden transition-all duration-200 group
                ${isDisabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
              `}
              style={{
                border: isSelected
                  ? `2px solid var(--cine-gold)`
                  : `2px solid transparent`,
                borderRadius: 'var(--radius-lens)',
                boxShadow: isSelected
                  ? '0 0 16px rgba(245,197,66,0.25)'
                  : 'none',
                aspectRatio: '4/3',
              }}
            >
              {/* 图片占位 */}
              <div
                className="absolute inset-0 flex items-center justify-center"
                style={{
                  background: isSelected
                    ? 'linear-gradient(135deg, #1e1b4b, #312e81)'
                    : 'linear-gradient(135deg, #1a1a2e, #252540)',
                }}
              >
                <FramePlaceholderIcon size={32} color="var(--text-tertiary)" />
              </div>

              {/* 悬停遮罩 */}
              {!isLocked && (
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
              )}

              {/* 选中标记 */}
              {isSelected && (
                <div className="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center z-10"
                  style={{ background: 'var(--brand)' }}
                >
                  <CheckIcon size={14} color="white" />
                </div>
              )}

              {/* 底部标签 */}
              <div className="absolute bottom-0 left-0 right-0 px-2 py-1.5"
                style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)' }}
              >
                <span className="text-[11px] text-text-primary font-medium">{img.label}</span>
              </div>
            </button>
          )
        })}
      </div>
      {!isLocked && selected.size > 0 && (
        <button
          onClick={() => onSubmit(selectedArray)}
          className="w-full py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98]"
          style={{
            background: 'linear-gradient(135deg, var(--cine-gold), var(--cine-gold-dim))',
            boxShadow: '0 0 16px rgba(245,197,66,0.2)',
            borderRadius: 'var(--radius-lens)',
          }}
        >
          {maxSelect === 1 ? '确认选择' : `确认选择 (${selected.size})`}
        </button>
      )}
      {isLocked && selectedArray.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-text-tertiary">
          <CheckIcon size={14} color="var(--success)" />
          已选择
        </div>
      )}
    </div>
  )
}
