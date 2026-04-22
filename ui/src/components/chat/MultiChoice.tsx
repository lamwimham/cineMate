import { useState } from 'react'
import { CheckIcon } from '../icons'
import type { ChoiceOption } from '../../types/chat'

interface MultiChoiceProps {
  question: string
  options: ChoiceOption[]
  maxSelect?: number
  onSubmit: (selectedIds: string[]) => void
  submitted?: boolean
  selectedIds?: string[]
}

export default function MultiChoice({
  question,
  options,
  maxSelect,
  onSubmit,
  submitted,
  selectedIds: initialSelected = [],
}: MultiChoiceProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set(initialSelected))
  const isLocked = submitted

  const toggle = (id: string) => {
    if (isLocked) return
    const next = new Set(selected)
    if (next.has(id)) {
      next.delete(id)
    } else {
      if (maxSelect && next.size >= maxSelect) return
      next.add(id)
    }
    setSelected(next)
  }

  const selectedArray = Array.from(selected)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-primary leading-relaxed">{question}</p>
        {maxSelect && (
          <span className="text-[11px] font-mono text-text-muted">
            {selected.size}/{maxSelect}
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-2">
        {options.map(opt => {
          const isSelected = selected.has(opt.id)
          const isDisabled = isLocked && !isSelected

          return (
            <button
              key={opt.id}
              disabled={isDisabled}
              onClick={() => toggle(opt.id)}
              className={`
                text-left p-2.5 rounded-xl transition-all duration-200
                ${isDisabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
              `}
              style={{
                background: isSelected
                  ? 'linear-gradient(135deg, rgba(99,102,241,0.12), rgba(79,70,229,0.06))'
                  : 'var(--bg-elevated)',
                border: isSelected
                  ? `1px solid var(--cine-gold-glow)`
                  : `1px solid var(--slate-mark)`,
                borderRadius: 'var(--radius-lens)',
                boxShadow: isSelected
                  ? '0 0 12px rgba(99,102,241,0.12)'
                  : '0 1px 2px rgba(0,0,0,0.2)',
              }}
            >
              <div className="flex items-start gap-2.5">
                {/* 多选方框 */}
                <div
                  className="w-4 h-4 rounded shrink-0 mt-0.5 flex items-center justify-center transition-all"
                  style={{
                    border: isSelected ? `2px solid var(--cine-gold)` : '2px solid var(--text-muted)',
                    background: isSelected ? 'var(--cine-gold)' : 'transparent',
                  }}
                >
                  {isSelected && (
                    <CheckIcon size={10} color="white" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    {opt.icon && <span className="text-sm flex items-center">{opt.icon}</span>}
                    <span className={`text-xs font-medium ${isSelected ? 'text-[#f5c542]' : 'text-text-primary'}`}>
                      {opt.label}
                    </span>
                  </div>
                  {opt.description && (
                    <p className="text-[10px] text-text-tertiary mt-0.5 leading-snug">{opt.description}</p>
                  )}
                </div>
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
          确认选择 ({selected.size} 项)
        </button>
      )}
      {isLocked && selectedArray.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-text-tertiary">
          <CheckIcon size={14} color="var(--success)" />
          已选择 {selectedArray.length} 项
        </div>
      )}
    </div>
  )
}
