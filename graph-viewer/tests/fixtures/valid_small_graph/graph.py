GRAPH = {
    "directed": True,
    "metadata": {"name": "valid-small"},
    "nodes": [
        {"id": "graph-only", "label": "Graph Only Node"},
    ],
    "edges": [
        {"source": "node-a", "target": "node-b", "label": "A to B"},
        {"source": "node-a", "target": "node-c", "label": "A to C"},
        {"source": "node-c", "target": "graph-only", "label": "C to Graph"},
    ],
}

