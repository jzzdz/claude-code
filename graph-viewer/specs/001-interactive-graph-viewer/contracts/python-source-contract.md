# Python Source Contract

The app accepts local, trusted Python sources supplied by the user. It does not
attempt to sandbox arbitrary untrusted code.

## Graph Source File

The graph source path MUST point to a readable `.py` file. The parser accepts
the first valid export in this order:

1. `get_graph() -> dict`
2. `GRAPH: dict`

The returned/exported dictionary MUST be JSON-compatible and may include:

- `directed`: optional boolean.
- `edges`: required list of edge objects.
- `nodes`: optional list of node objects. Node directory entries are merged
  with this list before validation.
- `metadata`: optional object.

## Node Source Directory

The node source path MUST point to a readable directory. Each direct child
`.py` file may expose one node by the first valid export in this order:

1. `get_node() -> dict`
2. `NODE: dict`

Files without either export are ignored with a warning. Exported nodes are
merged with any nodes from the graph source before validation.

## Combined Payload

The parser produces one combined payload:

```json
{
  "directed": true,
  "nodes": [
    {"id": "node-a", "label": "Node A"}
  ],
  "edges": [
    {"source": "node-a", "target": "node-b"}
  ]
}
```

The combined payload MUST pass `graph-input.schema.json`, then semantic
validation:

- Node ids are unique.
- Edge endpoints exist.
- At least one node exists.
- Labels are non-empty after trimming.
- User-facing errors include source path context when possible.
