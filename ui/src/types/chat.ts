import React from 'react'
export interface ChoiceOption {
  id: string
  label: string
  description?: string
  icon?: React.ReactNode
  disabled?: boolean
}

export interface ImageOption {
  id: string
  url: string
  label: string
  selected?: boolean
}

export interface AssetRef {
  id: string
  type: 'image' | 'video' | 'audio'
  url: string
  thumbnail?: string
  name: string
  metadata: {
    createdAt: string
    cost: string
    prompt?: string
    dimensions?: string
    duration?: string
  }
}

export type MessageType =
  | 'text'
  | 'single_choice'
  | 'multi_choice'
  | 'image_select'
  | 'asset_gallery'
  | 'clarification'

export interface ChatMessage {
  id: string
  role: 'user' | 'ai'
  type: MessageType
  content: string
  options?: ChoiceOption[]
  images?: ImageOption[]
  assets?: AssetRef[]
  maxSelect?: number
  selectedIds?: string[]
  submitted?: boolean
  timestamp: Date
}

export interface ClarificationStep {
  question: string
  type: 'single' | 'multi' | 'text'
  options?: ChoiceOption[]
  answer?: string | string[]
}
