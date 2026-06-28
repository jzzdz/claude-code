# Data Model: Interactive Graph Viewer

## SourcePaths

Represents the user-provided filesystem inputs.

Fields:
- `graph_path`: path string to a readable Python file.
- `nodes_path`: path string to a readable directory.
- `signature`: deterministic signature derived from relevant file paths,
  modification times, sizes, and content hashes where needed for cache keys.

Validation:
- `graph_path` MUST exist, be a file, be readable, and have `.py` suffix.
- `nodes_path` MUST exist, be a directory, and be readable.
- Signature generation MUST be deterministic and testable without Streamlit.

## RawGraphPayload

JSON-compatible data extracted from the trusted Python graph file and node
directory before schema validation.

Fields:
- `directed`: boolean, defaults to `true` when omitted.
- `nodes`: list of raw node objects.
- `edges`: list of raw edge objects.
- `metadata`: optional object with graph-level metadata.

Validation:
- Must be JSON-compatible: dictionaries, lists, strings, numbers, booleans, and
  null only.
- Must pass `contracts/graph-input.schema.json` before graph construction.

## GraphNode

Canonical node after validation.

Fields:
- `id`: non-empty string, unique within the graph.
- `label`: non-empty human-readable string.
- `metadata`: optional object.
- `degree`: computed integer.

Validation:
- `id` uniqueness is enforced by semantic validation.
- `label` is required for search and display.

## GraphEdge

Canonical edge after validation.

Fields:
- `source`: existing node id.
- `target`: existing node id.
- `directed`: optional edge-level boolean; graph-level default applies when
  omitted.
- `label`: optional string.
- `metadata`: optional object.

Validation:
- `source` and `target` MUST reference existing nodes.
- Self-loops are allowed unless later feature requirements reject them.
- Duplicate edges are allowed only when they carry distinct metadata or labels;
  otherwise duplicates are reported as warnings in the semantic validation
  report.

## GraphModel

Validated NetworkX graph plus query indexes.

Fields:
- `graph`: NetworkX `Graph` or `DiGraph`.
- `node_by_id`: mapping from node id to `GraphNode`.
- `label_index`: normalized label string to ordered node id list.
- `neighbors_by_id`: mapping from node id to direct neighbor id set.
- `edge_count`: integer.
- `node_count`: integer.
- `signature`: graph-content signature for layout and render cache keys.

Relationships:
- Built from `RawGraphPayload` only after schema and semantic validation.
- Used by layout, selection, and search modules.

## LayoutPositions

Deterministic two-dimensional positions for each node.

Fields:
- `positions`: mapping from node id to `{x, y}` numeric coordinates.
- `algorithm`: layout algorithm name.
- `options`: deterministic layout options used to compute positions.
- `signature`: graph signature plus layout options signature.

Validation:
- Every graph node MUST have exactly one position.
- Positions MUST be finite numeric values.

## RenderGraphData

Plotly-ready data generated from `GraphModel`, `LayoutPositions`, and current
viewer state.

Fields:
- `node_x`, `node_y`: ordered node coordinate arrays.
- `node_ids`: ordered node ids matching Plotly point indices.
- `node_labels`: ordered display labels.
- `node_colors`: ordered visual state colors.
- `node_sizes`: ordered visual sizes.
- `edge_x`, `edge_y`: edge segment coordinate arrays with separators.
- `edge_mode`: `all`, `sampled`, or `focused`.
- `viewport`: optional axis ranges used for search centering.

Validation:
- `node_ids` order MUST match Plotly `customdata` and selection lookup.
- Edge arrays MUST only reference positions present in `LayoutPositions`.

## SelectionState

Current selected node and highlighted neighborhood.

Fields:
- `selected_node_id`: optional node id.
- `neighbor_ids`: set of direct neighbor node ids.
- `highlighted_edge_ids`: optional set of edges adjacent to selected node.

State transitions:
- `none -> selected`: user selects a node.
- `selected -> selected`: user selects another node.
- `selected -> none`: user clears selection or loads a different graph.

## SearchState

Current label search state.

Fields:
- `query`: user-entered string.
- `matches`: ordered node id list.
- `active_node_id`: optional selected search result.
- `message`: optional user-facing no-result or multi-result message.

Validation:
- Exact case-insensitive label matches are ranked before partial matches.
- Search MUST NOT mutate `GraphModel`.

## ValidationErrorReport

User-facing validation feedback.

Fields:
- `code`: stable error code.
- `path`: input path or JSON path where the problem occurred.
- `message`: actionable human-readable message.
- `severity`: `error` or `warning`.

Rules:
- Any `error` blocks rendering.
- Warnings may render only if graph structure remains valid.
