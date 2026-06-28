# Render Interaction Contract

This contract defines the boundary between pure render preparation and the
Streamlit presentation layer.

## Render Input

Pure render preparation receives:

- `GraphModel`
- `LayoutPositions`
- optional `SelectionState`
- optional `SearchState`
- edge level-of-detail options

It returns `RenderGraphData` only. It MUST NOT call Streamlit.

## Plotly Node Trace Contract

Each rendered node point MUST include:

- `x`, `y`: numeric layout coordinates.
- `text`: display label.
- `customdata`: node id.
- `marker.color`: derived from visual state.
- `marker.size`: derived from visual state and optional degree metadata.

The order of `customdata` MUST match `RenderGraphData.node_ids`.

## Selection Event Contract

The Streamlit layer calls `st.plotly_chart(..., on_select="rerun",
selection_mode=["points"])`. When Plotly returns selected point data, the
Streamlit layer extracts the node id from the selected point's `customdata` and
passes it to the pure selection module.

Expected selection outputs:

- selected node id
- direct neighbor id set
- visual state map for selected, neighbor, and dimmed nodes

## Search Centering Contract

The search module returns ordered matches by node id. The viewport module
accepts an active node id and layout positions, then returns axis ranges that
center the node while preserving a useful surrounding context.

No-result searches return a user-facing message and MUST NOT change the current
viewport.
