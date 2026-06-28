GRAPH = {
    "directed": True,
    "metadata": {"name": "four-node-with-nested-subgraph"},
    "nodes": [
        {"id": "node-1", "label": "Node 1"},
        {
            "id": "node-2",
            "label": "Node 2 - Subgraph",
            "metadata": {
                "subgraph": {
                    "directed": True,
                    "nodes": [
                        {"id": "node-2-a", "label": "Subnode A"},
                        {"id": "node-2-b", "label": "Subnode B"},
                        {"id": "node-2-c", "label": "Subnode C"},
                        {"id": "node-2-d", "label": "Subnode D"},
                        {"id": "node-2-e", "label": "Subnode E"},
                    ],
                    "edges": [
                        {"source": "node-2-a", "target": "node-2-b"},
                        {"source": "node-2-b", "target": "node-2-c"},
                        {"source": "node-2-c", "target": "node-2-d"},
                        {"source": "node-2-d", "target": "node-2-e"},
                    ],
                }
            },
        },
        {"id": "node-3", "label": "Node 3"},
        {"id": "node-4", "label": "Node 4"},
    ],
    "edges": [
        {"source": "node-1", "target": "node-2"},
        {"source": "node-2", "target": "node-3"},
        {"source": "node-2", "target": "node-4"},
    ],
}

