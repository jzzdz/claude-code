# CLAUDE.md — youtube_notebooklm

This file provides guidance to Claude Code when working in this project.

## What this project does

A terminal-based research agent that:
1. Searches YouTube for videos on a topic using `yt-dlp` (no API key required)
2. Opens NotebookLM via Playwright browser automation
3. Creates a new notebook and adds the YouTube video URLs as sources
4. NotebookLM then processes the videos and lets the user generate study guides / audio overviews

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Running

```bash
python3 main.py "tu tema de investigación" --videos 8
python3 main.py "machine learning" --videos 5 --title "ML Research"
```

**First run:** A Chrome window will open. Log into Google manually — the session is saved in `~/.research-agent/browser-profile` for future runs.

## Architecture

| File | Role |
|------|------|
| `main.py` | CLI entry point (Click), orchestrates the full flow |
| `youtube_search.py` | Calls `yt-dlp` as a subprocess, returns `Video` dataclasses |
| `notebooklm.py` | Playwright async automation: login persistence, notebook creation, source upload |

### Key design decisions

- **Persistent browser profile** (`~/.research-agent/browser-profile`) — avoids re-authenticating on every run.
- **Headless=False** — required because NotebookLM needs real Google auth; headless mode is blocked by Google.
- **yt-dlp subprocess** — simpler than the Python API; `ytsearch{N}:query` format returns N results as JSON lines.
- **No Claude API in the hot path** — the agent is orchestrated by Claude Code itself; `anthropic` is in requirements for future tool-use extensions.

### NotebookLM automation notes

NotebookLM's UI selectors can change. The automation uses text-based locators (`:has-text()`) rather than CSS class names to be more resilient. If the automation breaks after a NotebookLM UI update, check `_add_youtube_source()` and `_create_notebook()` first.

The automation flow:
1. Navigate to `notebooklm.google.com`
2. Wait for login (first run only)
3. Click "New notebook"
4. For each video URL: click "Add source" → "YouTube" → paste URL → confirm
5. Leave the browser open for the user to trigger generation
