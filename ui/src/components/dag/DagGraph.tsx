import { useState, useCallback, useMemo } from 'react'
import DagNode, { type DagNodeData } from './DagNode'
import DagEdge, { type DagEdgeData } from './DagEdge'

// 精确布局配置（基于截图优化）
const NODE_W = 160
const NODE_H = 96
const PAD_X = 56
const PAD_Y = 28
const GAP_X = 88
const GAP_Y = 36

interface DagGraphProps {
  nodes: DagNodeData[]
  edges: DagEdgeData[]
}

function computeLayout(nodes: DagNodeData[], edges: DagEdgeData[]) {
  const pos: Record<string, { x: number; y: number }> = {}
  const levels: string[][] = []
  const inDeg: Record<string, number> = {}

  nodes.forEach(n => { inDeg[n.id] = 0 })
  edges.forEach(e => { inDeg[e.to] = (inDeg[e.to] || 0) + 1 })

  let queue = nodes.filter(n => inDeg[n.id] === 0).map(n => n.id)
  const visited = new Set<string>()

  while (queue.length) {
    levels.push([...queue])
    queue.forEach(id => visited.add(id))
    const next = new Set<string>()
    edges.forEach(e => {
      if (queue.includes(e.from) && !visited.has(e.to)) {
        next.add(e.to)
      }
    })
    queue = Array.from(next)
  }

  // 计算坐标
  levels.forEach((level, col) => {
    const count = level.length
    const totalH = count * NODE_H + (count - 1) * GAP_Y
    const startY = PAD_Y + Math.max(0, (264 - totalH) / 2)

    level.forEach((id, row) => {
      pos[id] = {
        x: PAD_X + col * (NODE_W + GAP_X),
        y: startY + row * (NODE_H + GAP_Y),
      }
    })
  })

  return pos
}

export default function DagGraph({ nodes, edges }: DagGraphProps) {
  const [selected, setSelected] = useState<string | null>(null)

  const positions = useMemo(() => computeLayout(nodes, edges), [nodes, edges])

  const maxX = useMemo(() => {
    const xs = Object.values(positions).map(p => p.x)
    return xs.length ? Math.max(...xs) + NODE_W + PAD_X : 400
  }, [positions])

  const maxY = useMemo(() => {
    const ys = Object.values(positions).map(p => p.y)
    return ys.length ? Math.max(...ys) + NODE_H + PAD_Y : 200
  }, [positions])

  const handleClick = useCallback((id: string) => {
    setSelected(prev => (prev === id ? null : id))
  }, [])

  return (
    <div className="relative" style={{ minWidth: maxX, minHeight: maxY }}>
      {/* 连线层 */}
      {edges.map(edge => {
        const fp = positions[edge.from]
        const tp = positions[edge.to]
        if (!fp || !tp) return null
        return (
          <DagEdge
            key={edge.id}
            data={edge}
            fromX={fp.x + NODE_W}
            fromY={fp.y + NODE_H / 2}
            toX={tp.x}
            toY={tp.y + NODE_H / 2}
          />
        )
      })}

      {/* 节点层 */}
      {nodes.map(node => {
        const p = positions[node.id]
        if (!p) return null
        return (
          <div key={node.id} className="absolute" style={{ left: p.x, top: p.y }}>
            <DagNode
              data={node}
              isSelected={selected === node.id}
              onClick={() => handleClick(node.id)}
            />
          </div>
        )
      })}
    </div>
  )
}
