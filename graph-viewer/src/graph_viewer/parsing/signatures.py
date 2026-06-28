from __future__ import annotations

import hashlib
import json
from pathlib import Path

from graph_viewer.graph.model import SourcePaths


def _json_hash(payload: object) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def file_signature(path: str | Path) -> str:
    resolved = Path(path).expanduser().resolve()
    stat = resolved.stat()
    digest = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return _json_hash(
        {
            "path": str(resolved),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "sha256": digest.hexdigest(),
        }
    )


def directory_signature(path: str | Path) -> str:
    resolved = Path(path).expanduser().resolve()
    entries = []
    for child in sorted(resolved.glob("*.py"), key=lambda item: item.name):
        stat = child.stat()
        entries.append(
            {
                "name": child.name,
                "size": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
                "signature": file_signature(child),
            }
        )
    return _json_hash({"path": str(resolved), "entries": entries})


def create_source_paths(graph_path: str | Path, nodes_path: str | Path) -> SourcePaths:
    graph_resolved = Path(graph_path).expanduser().resolve()
    nodes_resolved = Path(nodes_path).expanduser().resolve()
    signature = _json_hash(
        {
            "graph": file_signature(graph_resolved),
            "nodes": directory_signature(nodes_resolved),
        }
    )
    return SourcePaths(
        graph_path=str(graph_resolved),
        nodes_path=str(nodes_resolved),
        signature=signature,
    )

