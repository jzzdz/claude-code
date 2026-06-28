from __future__ import annotations

from types import SimpleNamespace

from graph_viewer.render.selection_event import extract_selected_node_id


def test_extract_selected_node_id_from_streamlit_plotly_payload():
    event_payload = {
        "selection": {
            "points": [
                {
                    "curve_number": 1,
                    "point_number": 0,
                    "customdata": "node-a",
                }
            ]
        }
    }

    assert extract_selected_node_id(event_payload) == "node-a"


def test_extract_selected_node_id_supports_object_like_streamlit_payload():
    event_payload = SimpleNamespace(
        selection=SimpleNamespace(points=[{"customdata": ["node-b", "Beta"]}])
    )

    assert extract_selected_node_id(event_payload) == "node-b"


def test_extract_selected_node_id_returns_none_for_empty_or_non_node_selection():
    assert extract_selected_node_id(None) is None
    assert extract_selected_node_id({"selection": {"points": []}}) is None
    assert extract_selected_node_id({"selection": {"points": [{"customdata": None}]}}) is None

