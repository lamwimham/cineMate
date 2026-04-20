"""
Unit tests for PipelineDAG (cine_mate/engine/dag.py)

Tests:
- Node operations (add, remove)
- Edge operations (add, dependency)
- Topology queries (get_ready_nodes, get_downstream, get_upstream)
- Dirty propagation analysis (analyze_impact)
- Serialization (to_dict, from_dict)
"""

import pytest
from cine_mate.engine.dag import PipelineDAG, DAGNode, DirtyError


class TestDAGNode:
    """Tests for DAGNode dataclass."""

    def test_dag_node_creation(self):
        """Test basic DAGNode creation."""
        node = DAGNode(
            id="node_1",
            type="text_to_image",
            config={"prompt": "test"}
        )
        assert node.id == "node_1"
        assert node.type == "text_to_image"
        assert node.config == {"prompt": "test"}
        assert node.dependencies == []

    def test_dag_node_with_dependencies(self):
        """Test DAGNode with dependencies."""
        node = DAGNode(
            id="node_2",
            type="image_to_video",
            config={"duration": 5},
            dependencies=["node_1"]
        )
        assert node.dependencies == ["node_1"]


class TestPipelineDAGCreation:
    """Tests for DAG creation and basic operations."""

    def test_empty_dag(self, empty_dag):
        """Test empty DAG has no nodes."""
        assert empty_dag.graph.number_of_nodes() == 0
        assert empty_dag.graph.number_of_edges() == 0

    def test_add_single_node(self, empty_dag):
        """Test adding a single node."""
        empty_dag.add_node("node_A", "text_to_image", {"prompt": "test"})
        assert empty_dag.graph.has_node("node_A")
        assert empty_dag.graph.nodes["node_A"]["type"] == "text_to_image"
        assert empty_dag.node_configs["node_A"] == {"prompt": "test"}

    def test_add_multiple_nodes(self, empty_dag):
        """Test adding multiple nodes."""
        empty_dag.add_node("node_A", "script", {"prompt": "v1"})
        empty_dag.add_node("node_B", "img", {"prompt": "v2"})
        empty_dag.add_node("node_C", "vid", {"prompt": "v3"})

        assert empty_dag.graph.number_of_nodes() == 3
        assert set(empty_dag.graph.nodes()) == {"node_A", "node_B", "node_C"}

    def test_add_node_updates_config(self, empty_dag):
        """Test that add_node updates node_configs dict."""
        empty_dag.add_node("node_1", "test_type", {"key": "value"})
        assert "node_1" in empty_dag.node_configs
        assert empty_dag.node_configs["node_1"]["key"] == "value"

    def test_update_node_config(self, empty_dag):
        """Test updating existing node config."""
        empty_dag.add_node("node_1", "test", {"prompt": "v1"})
        empty_dag.add_node("node_1", "test", {"prompt": "v2"})  # Update

        assert empty_dag.node_configs["node_1"]["prompt"] == "v2"


class TestPipelineDAGEdges:
    """Tests for edge (dependency) operations."""

    def test_add_single_edge(self, empty_dag):
        """Test adding a single dependency edge."""
        empty_dag.add_node("node_A", "script", {})
        empty_dag.add_node("node_B", "img", {})
        empty_dag.add_edge("node_A", "node_B")

        assert empty_dag.graph.has_edge("node_A", "node_B")
        assert empty_dag.graph.number_of_edges() == 1

    def test_add_multiple_edges(self, linear_dag):
        """Test linear DAG has correct edges."""
        assert linear_dag.graph.has_edge("node_A", "node_B")
        assert linear_dag.graph.has_edge("node_B", "node_C")
        assert linear_dag.graph.number_of_edges() == 2

    def test_branching_edges(self, branching_dag):
        """Test branching DAG has correct edges."""
        assert branching_dag.graph.has_edge("node_A", "node_B")
        assert branching_dag.graph.has_edge("node_A", "node_C")
        assert branching_dag.graph.has_edge("node_B", "node_D")
        assert branching_dag.graph.has_edge("node_C", "node_D")
        assert branching_dag.graph.number_of_edges() == 4

    def test_edge_to_nonexistent_node(self, empty_dag):
        """Test adding edge creates target node config entry."""
        empty_dag.add_node("node_A", "script", {})
        empty_dag.add_edge("node_A", "node_B")  # node_B doesn't exist yet

        # Edge should still be added
        assert empty_dag.graph.has_edge("node_A", "node_B")


class TestGetReadyNodes:
    """Tests for get_ready_nodes (nodes ready to execute)."""

    def test_empty_dag_ready_nodes(self, empty_dag):
        """Empty DAG has no ready nodes."""
        ready = empty_dag.get_ready_nodes(set())
        assert ready == []

    def test_all_nodes_ready_in_empty_completed(self, linear_dag):
        """All nodes are ready when completed_nodes is empty."""
        ready = linear_dag.get_ready_nodes(set())
        # Only node_A should be ready (no dependencies)
        assert ready == ["node_A"]

    def test_partial_completion(self, linear_dag):
        """Test ready nodes after partial completion."""
        # After node_A completes, node_B becomes ready
        ready = linear_dag.get_ready_nodes({"node_A"})
        assert ready == ["node_B"]

        # After node_A and node_B complete, node_C becomes ready
        ready = linear_dag.get_ready_nodes({"node_A", "node_B"})
        assert ready == ["node_C"]

    def test_all_completed(self, linear_dag):
        """No ready nodes when all are completed."""
        ready = linear_dag.get_ready_nodes({"node_A", "node_B", "node_C"})
        assert ready == []

    def test_branching_dag_ready_nodes(self, branching_dag):
        """Test ready nodes in branching DAG."""
        # Initially only node_A is ready
        ready = branching_dag.get_ready_nodes(set())
        assert ready == ["node_A"]

        # After node_A, both B and C are ready
        ready = branching_dag.get_ready_nodes({"node_A"})
        assert set(ready) == {"node_B", "node_C"}

        # After B and C, D is ready
        ready = branching_dag.get_ready_nodes({"node_A", "node_B", "node_C"})
        assert ready == ["node_D"]


class TestGetDownstream:
    """Tests for get_downstream (nodes affected by changes)."""

    def test_downstream_of_leaf_node(self, linear_dag):
        """Leaf node's downstream is just itself."""
        downstream = linear_dag.get_downstream("node_C")
        assert downstream == {"node_C"}

    def test_downstream_of_middle_node(self, linear_dag):
        """Middle node's downstream includes itself and downstream nodes."""
        downstream = linear_dag.get_downstream("node_B")
        assert downstream == {"node_B", "node_C"}

    def test_downstream_of_root_node(self, linear_dag):
        """Root node's downstream includes entire DAG."""
        downstream = linear_dag.get_downstream("node_A")
        assert downstream == {"node_A", "node_B", "node_C"}

    def test_downstream_of_nonexistent_node(self, empty_dag):
        """Nonexistent node returns empty set."""
        downstream = empty_dag.get_downstream("nonexistent")
        assert downstream == set()

    def test_downstream_in_branching_dag(self, branching_dag):
        """Test downstream in branching structure."""
        # node_A affects all nodes
        downstream = branching_dag.get_downstream("node_A")
        assert downstream == {"node_A", "node_B", "node_C", "node_D"}

        # node_B affects B and D
        downstream = branching_dag.get_downstream("node_B")
        assert downstream == {"node_B", "node_D"}

        # node_D (leaf) affects only itself
        downstream = branching_dag.get_downstream("node_D")
        assert downstream == {"node_D"}


class TestGetUpstream:
    """Tests for get_upstream (dependencies)."""

    def test_upstream_of_root_node(self, linear_dag):
        """Root node has no upstream."""
        upstream = linear_dag.get_upstream("node_A")
        assert upstream == set()

    def test_upstream_of_middle_node(self, linear_dag):
        """Middle node has one upstream dependency."""
        upstream = linear_dag.get_upstream("node_B")
        assert upstream == {"node_A"}

    def test_upstream_of_leaf_node(self, linear_dag):
        """Leaf node has upstream chain."""
        upstream = linear_dag.get_upstream("node_C")
        assert upstream == {"node_A", "node_B"}

    def test_upstream_of_nonexistent_node(self, empty_dag):
        """Nonexistent node returns empty set."""
        upstream = empty_dag.get_upstream("nonexistent")
        assert upstream == set()

    def test_upstream_in_branching_dag(self, branching_dag):
        """Test upstream in branching structure."""
        # node_D has all other nodes as upstream
        upstream = branching_dag.get_upstream("node_D")
        assert upstream == {"node_A", "node_B", "node_C"}

        # node_B and node_C have only node_A
        upstream = branching_dag.get_upstream("node_B")
        assert upstream == {"node_A"}

        upstream = branching_dag.get_upstream("node_C")
        assert upstream == {"node_A"}


class TestAnalyzeImpact:
    """Tests for analyze_impact (dirty propagation)."""

    def test_analyze_empty_change_set(self, linear_dag):
        """Empty change set means all nodes are reusable."""
        impact = linear_dag.analyze_impact(set())
        assert impact["dirty_nodes"] == []
        assert set(impact["reusable_nodes"]) == {"node_A", "node_B", "node_C"}
        assert impact["total_nodes"] == 3

    def test_analyze_leaf_node_change(self, linear_dag):
        """Changing leaf node only affects itself."""
        impact = linear_dag.analyze_impact({"node_C"})
        assert impact["dirty_nodes"] == ["node_C"]
        assert set(impact["reusable_nodes"]) == {"node_A", "node_B"}

    def test_analyze_middle_node_change(self, linear_dag):
        """Changing middle node affects itself and downstream."""
        impact = linear_dag.analyze_impact({"node_B"})
        assert set(impact["dirty_nodes"]) == {"node_B", "node_C"}
        assert impact["reusable_nodes"] == ["node_A"]

    def test_analyze_root_node_change(self, linear_dag):
        """Changing root node affects entire DAG."""
        impact = linear_dag.analyze_impact({"node_A"})
        assert set(impact["dirty_nodes"]) == {"node_A", "node_B", "node_C"}
        assert impact["reusable_nodes"] == []

    def test_analyze_multiple_node_changes(self, linear_dag):
        """Changing multiple nodes."""
        impact = linear_dag.analyze_impact({"node_A", "node_C"})
        # node_A affects B and C, but C is already dirty
        assert set(impact["dirty_nodes"]) == {"node_A", "node_B", "node_C"}
        assert impact["reusable_nodes"] == []

    def test_analyze_in_branching_dag(self, branching_dag):
        """Test impact analysis in branching DAG."""
        # Changing node_A affects all
        impact = branching_dag.analyze_impact({"node_A"})
        assert set(impact["dirty_nodes"]) == {"node_A", "node_B", "node_C", "node_D"}

        # Changing node_B affects B and D, but not C
        impact = branching_dag.analyze_impact({"node_B"})
        assert set(impact["dirty_nodes"]) == {"node_B", "node_D"}
        assert set(impact["reusable_nodes"]) == {"node_A", "node_C"}

        # Changing node_D only affects itself
        impact = branching_dag.analyze_impact({"node_D"})
        assert impact["dirty_nodes"] == ["node_D"]
        assert set(impact["reusable_nodes"]) == {"node_A", "node_B", "node_C"}

    def test_analyze_complex_dag(self, complex_dag):
        """Test impact analysis in complex multi-level DAG."""
        # Changing input_1 affects proc_1, enhance_1, output
        impact = complex_dag.analyze_impact({"input_1"})
        dirty_set = set(impact["dirty_nodes"])
        assert "input_1" in dirty_set
        assert "proc_1" in dirty_set
        assert "enhance_1" in dirty_set
        assert "output" in dirty_set
        # These should NOT be dirty
        assert "input_2" not in dirty_set
        assert "proc_2" not in dirty_set


class TestDAGSerialization:
    """Tests for DAG serialization (to_dict, from_dict)."""

    def test_to_dict(self, linear_dag):
        """Test DAG serialization to dict."""
        data = linear_dag.to_dict()
        assert "nodes" in data
        assert "links" in data
        assert len(data["nodes"]) == 3

    def test_from_dict(self, linear_dag):
        """Test DAG deserialization from dict."""
        data = linear_dag.to_dict()
        restored_dag = PipelineDAG.from_dict(data)

        assert restored_dag.graph.number_of_nodes() == 3
        assert restored_dag.graph.has_edge("node_A", "node_B")
        assert restored_dag.graph.has_edge("node_B", "node_C")

    def test_serialization_preserves_topology(self, branching_dag):
        """Test serialization preserves branching topology."""
        data = branching_dag.to_dict()
        restored_dag = PipelineDAG.from_dict(data)

        assert restored_dag.graph.number_of_nodes() == 4
        assert restored_dag.graph.number_of_edges() == 4

        # Check edges
        assert restored_dag.graph.has_edge("node_A", "node_B")
        assert restored_dag.graph.has_edge("node_A", "node_C")
        assert restored_dag.graph.has_edge("node_B", "node_D")
        assert restored_dag.graph.has_edge("node_C", "node_D")


class TestDAGNodeTypes:
    """Tests for various node types."""

    def test_text_to_image_node(self, empty_dag):
        """Test text_to_image node creation."""
        empty_dag.add_node("img_1", "text_to_image", {
            "prompt": "A sunset",
            "seed": 42
        })
        assert empty_dag.graph.nodes["img_1"]["type"] == "text_to_image"

    def test_image_to_video_node(self, empty_dag):
        """Test image_to_video node creation."""
        empty_dag.add_node("vid_1", "image_to_video", {
            "duration": 5,
            "motion_strength": 0.5
        })
        assert empty_dag.graph.nodes["vid_1"]["type"] == "image_to_video"

    def test_video_concat_node(self, empty_dag):
        """Test video_concat node creation."""
        empty_dag.add_node("concat_1", "video_concat", {
            "transition": "crossfade"
        })
        assert empty_dag.graph.nodes["concat_1"]["type"] == "video_concat"

    def test_color_grade_node(self, empty_dag):
        """Test color_grade node creation."""
        empty_dag.add_node("grade_1", "color_grade", {
            "style": "wong_kar_wai"
        })
        assert empty_dag.graph.nodes["grade_1"]["type"] == "color_grade"


@pytest.mark.performance
class TestDAGPerformance:
    """Performance tests for large DAGs."""

    def test_large_dag_ready_nodes(self):
        """Test get_ready_nodes performance on large DAG."""
        dag = PipelineDAG()

        # Create 100 nodes in linear chain
        for i in range(100):
            dag.add_node(f"node_{i}", "test", {})

        for i in range(99):
            dag.add_edge(f"node_{i}", f"node_{i+1}")

        # Should efficiently find ready nodes
        ready = dag.get_ready_nodes(set())
        assert ready == ["node_0"]

    def test_large_dag_analyze_impact(self):
        """Test analyze_impact performance on large DAG."""
        dag = PipelineDAG()

        # Create 100 nodes
        for i in range(100):
            dag.add_node(f"node_{i}", "test", {})

        for i in range(99):
            dag.add_edge(f"node_{i}", f"node_{i+1}")

        # Analyzing impact of node_50 change
        impact = dag.analyze_impact({"node_50"})
        # Should mark node_50 to node_99 as dirty (50 nodes)
        assert len(impact["dirty_nodes"]) == 50
        assert len(impact["reusable_nodes"]) == 50