from __future__ import annotations


def build_large_graph(node_count: int = 5000, extra_stride: int = 17) -> dict:
    nodes = [
        {"id": f"node-{index:05d}", "label": f"Node {index:05d}"}
        for index in range(node_count)
    ]
    edges = [
        {"source": f"node-{index:05d}", "target": f"node-{index + 1:05d}"}
        for index in range(node_count - 1)
    ]
    edges.extend(
        {
            "source": f"node-{index:05d}",
            "target": f"node-{(index + extra_stride) % node_count:05d}",
        }
        for index in range(0, node_count, extra_stride)
    )
    return {
        "directed": True,
        "metadata": {"name": "generated-large", "node_count": node_count},
        "nodes": nodes,
        "edges": edges,
    }


GRAPH = build_large_graph()

