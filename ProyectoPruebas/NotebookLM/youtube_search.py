"""
YouTube search using yt-dlp — no API key required.
"""

import json
import subprocess
from dataclasses import dataclass


@dataclass
class Video:
    title: str
    url: str
    channel: str
    duration: int  # seconds
    view_count: int
    description: str

    def duration_fmt(self) -> str:
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def search_youtube(query: str, max_results: int = 10) -> list[Video]:
    """Search YouTube and return video metadata using yt-dlp."""
    search_query = f"ytsearch{max_results}:{query}"
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        "--no-playlist",
        "--quiet",
        search_query,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp error: {result.stderr}")

    videos = []
    for line in result.stdout.strip().splitlines():
        if not line:
            continue
        data = json.loads(line)
        videos.append(
            Video(
                title=data.get("title", ""),
                url=f"https://www.youtube.com/watch?v={data.get('id', '')}",
                channel=data.get("channel", data.get("uploader", "")),
                duration=data.get("duration", 0) or 0,
                view_count=data.get("view_count", 0) or 0,
                description=(data.get("description", "") or "")[:300],
            )
        )

    return videos
