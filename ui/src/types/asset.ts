export type AssetType = 'image' | 'video' | 'audio'
export type AssetStatus = 'generating' | 'ready' | 'used' | 'archived'

export interface Asset {
  id: string
  type: AssetType
  name: string
  url: string
  thumbnail: string
  status: AssetStatus
  projectId: string
  runId?: string
  nodeId?: string
  metadata: {
    createdAt: string
    cost: number
    prompt?: string
    dimensions?: string
    duration?: string
    format?: string
    sizeBytes?: number
  }
  tags: string[]
}

export interface AssetFilter {
  type?: AssetType | 'all'
  status?: AssetStatus | 'all'
  projectId?: string
  runId?: string
  search?: string
}

export interface AssetGroup {
  label: string
  assets: Asset[]
}
