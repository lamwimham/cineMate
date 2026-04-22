import { useState } from 'react'
import { CheckIcon } from '../icons'
import type { ChoiceOption } from '../../types/chat'

interface SingleChoiceProps {
  question: string
  options: ChoiceOption[]
  onSubmit: (selectedId: string) => void
  submitted?: boolean
  selectedId?: string
}

export default function SingleChoice({
  question,
  options,
  onSubmit,
  submitted,
  selectedId: initialSelected,
}: SingleChoiceProps) {
  const [selected, setSelected] = useState<string | undefined>(initialSelected)
  const isLocked = submitted

  return (
    <div className="space-y-3">
      <p className="text-sm text-text-primary leading-relaxed">{question}</p>
      <div className="space-y-2">
        {options.map(opt => {
          const isSelected = selected === opt.id
          const isDisabled = isLocked && !isSelected

          return (
            <button
              key={opt.id}
              disabled={isDisabled}
              onClick={() => !isLocked && setSelected(opt.id)}
              className={`
                w-full text-left p-3 rounded-xl transition-all duration-200 relative overflow-hidden
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
                  ? '0 0 16px rgba(99,102,241,0.15), inset 0 1px 0 rgba(255,255,255,0.05)'
                  : '0 1px 3px rgba(0,0,0,0.2)',
              }}
            >
              <div className="flex items-start gap-3">
                {/* 单选圆圈 */}
                <div
                  className="w-5 h-5 rounded-full shrink-0 mt-0.5 flex items-center justify-center transition-all"
                  style={{
                    border: isSelected ? `2px solid var(--cine-gold)` : '2px solid var(--text-muted)',
                    background: isSelected ? 'var(--cine-gold)' : 'transparent',
                  }}
                >
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-white" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    {opt.icon && <span className="text-base flex items-center">{opt.icon}</span>}
                    <span className={`text-sm font-medium ${isSelected ? 'text-[#f5c542]' : 'text-text-primary'}`}>
                      {opt.label}
                    </span>
                  </div>
                  {opt.description && (
                    <p className="text-xs text-text-tertiary mt-0.5">{opt.description}</p>
                  )}
                </div>
              </div>
            </button>
          )
        })}
      </div>
      {!isLocked && selected && (
        <button
          onClick={() => selected && onSubmit(selected)}
          className="w-full py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98]"
          style={{
            background: 'linear-gradient(135deg, var(--cine-gold), var(--cine-gold-dim))',
            boxShadow: '0 0 16px rgba(245,197,66,0.2)',
            borderRadius: 'var(--radius-lens)',
          }}
        >
          确认选择
        </button>
      )}
      {isLocked && selected && (
        <div className="flex items-center gap-2 text-xs text-text-tertiary">
          <CheckIcon size={14} color="var(--success)" />
          已选择
        </div>
      )}
    </div>
  )
}
