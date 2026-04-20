"""
CineMate DAG Engine
Manages the topology of the video generation pipeline.
Supports Dirty Propagation for incremental updates (Video Git).
"""

import networkx as nx
from typing import List, Set, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class DAGNode:
    id: str
    type: str  # e.g., "IMG_GEN", "VIDEO_GEN", "TTS"
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

class DirtyError(Exception):
    """Raised when a dirty node is encountered."""
    pass

class PipelineDAG:
    """
    Directed Acyclic Graph for the pipeline.
    Handles dependency management and dirty propagation.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_configs: Dict[str, Dict[str, Any]] = {}
        
    def add_node(self, node_id: str, node_type: str, config: Dict[str, Any]):
        """Add a node to the graph."""
        self.graph.add_node(node_id, type=node_type)
        self.node_configs[node_id] = config
        
    def add_edge(self, from_node: str, to_node: str):
        """Add a dependency edge: from_node must complete before to_node."""
        self.graph.add_edge(from_node, to_node)
        if to_node not in self.node_configs:
            # Inherit config if not present? No, usually to_node has its own config
            self.node_configs[to_node] = {}

    def get_ready_nodes(self, completed_nodes: Set[str]) -> List[str]:
        """
        Get all nodes that are ready to execute.
        A node is ready if all its predecessors are in completed_nodes.
        """
        ready = []
        for node_id in self.graph.nodes():
            if node_id in completed_nodes:
                continue
            
            # Check if all dependencies are met
            predecessors = set(self.graph.predecessors(node_id))
            if predecessors.issubset(completed_nodes):
                ready.append(node_id)
        return ready

    def get_downstream(self, node_id: str) -> Set[str]:
        """Get all nodes downstream from the given node (including itself)."""
        if not self.graph.has_node(node_id):
            return set()
        
        # descendants gives all nodes reachable from node_id
        # we also include node_id itself
        downstream = nx.descendants(self.graph, node_id)
        downstream.add(node_id)
        return downstream

    def get_upstream(self, node_id: str) -> Set[str]:
        """Get all nodes upstream from the given node (dependencies)."""
        if not self.graph.has_node(node_id):
            return set()
        
        upstream = nx.ancestors(self.graph, node_id)
        # upstream does not include node_id itself usually in this context
        return upstream

    def analyze_impact(self, changed_nodes: Set[str]) -> Dict[str, Any]:
        """
        Analyze the impact of changes.
        Returns:
            - dirty_nodes: Nodes that need to be re-executed.
            - reusable_nodes: Nodes that can be reused from the previous run.
        """
        dirty_nodes = set()
        
        for node_id in changed_nodes:
            # The changed node itself is dirty
            dirty_nodes.add(node_id)
            # All downstream nodes are dirty
            dirty_nodes.update(self.get_downstream(node_id))
            
        all_nodes = set(self.graph.nodes())
        reusable_nodes = all_nodes - dirty_nodes
        
        return {
            "dirty_nodes": list(dirty_nodes),
            "reusable_nodes": list(reusable_nodes),
            "total_nodes": len(all_nodes)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize DAG to dict for snapshot."""
        return nx.node_link_data(self.graph)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineDAG':
        """Deserialize DAG from dict."""
        dag = cls()
        dag.graph = nx.node_link_graph(data)
        # We need to restore node_configs if available, but nx.node_link_data doesn't store extra dicts easily
        # For now, we assume configs are passed or stored elsewhere
        return dag
