"""
Workspace utilities
- History & downloads logging
- Reading list management
"""

from __future__ import annotations

import json
import os
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

WORKSPACE_PATH = "storage/workspace.json"


def _now_iso() -> str:
    return datetime.now().isoformat()


def _ensure_dir() -> None:
    os.makedirs(os.path.dirname(WORKSPACE_PATH), exist_ok=True)


def _load() -> Dict[str, Any]:
    _ensure_dir()
    if not os.path.exists(WORKSPACE_PATH):
        return {"history": [], "downloads": [], "reading_list": [], "summaries": {}, "collections": {}}
    try:
        with open(WORKSPACE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure keys
            data.setdefault("history", [])
            data.setdefault("downloads", [])
            data.setdefault("reading_list", [])
            data.setdefault("summaries", {})
            data.setdefault("collections", {})
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {"history": [], "downloads": [], "reading_list": [], "summaries": {}, "collections": {}}


def _save(data: Dict[str, Any]) -> bool:
    try:
        with open(WORKSPACE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def compute_summary_id(url: Optional[str], title: Optional[str], summary: str) -> str:
    base = (url or "") + "\n" + (title or "") + "\n" + (summary or "")
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]


def log_view(url: str, title: str, summary_id: str) -> None:
    data = _load()
    entry = {
        "timestamp": _now_iso(),
        "url": url,
        "title": title,
        "summary_id": summary_id,
    }
    data["history"].append(entry)
    # Trim
    if len(data["history"]) > 2000:
        data["history"] = data["history"][-2000:]
    _save(data)


def upsert_summary(summary_id: str, url: str, title: str, team_names: Optional[List[str]] = None, tournament: Optional[str] = None) -> None:
    data = _load()
    summaries = data.get("summaries", {})
    meta = summaries.get(summary_id, {
        "summary_id": summary_id,
        "url": url,
        "title": title,
        "team_names": [],
        "view_count": 0,
        "last_viewed": None,
        "collections": [],
        "tags": [],
        "tournament": tournament or "",
    })
    meta["url"] = url or meta.get("url")
    meta["title"] = title or meta.get("title")
    if team_names:
        merged = list(dict.fromkeys((meta.get("team_names") or []) + team_names))
        meta["team_names"] = merged[:12]
    meta["view_count"] = (meta.get("view_count") or 0) + 1
    meta["last_viewed"] = _now_iso()
    if tournament:
        meta["tournament"] = tournament
    summaries[summary_id] = meta
    data["summaries"] = summaries
    _save(data)


def log_download(summary_id: str, file_type: str) -> None:
    data = _load()
    entry = {
        "timestamp": _now_iso(),
        "summary_id": summary_id,
        "file_type": file_type,
    }
    data["downloads"].append(entry)
    if len(data["downloads"]) > 5000:
        data["downloads"] = data["downloads"][-5000:]
    _save(data)


def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    data = _load()
    return list(reversed(data.get("history", [])[-limit:]))


def get_downloads(limit: int = 50) -> List[Dict[str, Any]]:
    data = _load()
    return list(reversed(data.get("downloads", [])[-limit:]))


def get_summary(summary_id: str) -> Optional[Dict[str, Any]]:
    return _load().get("summaries", {}).get(summary_id)


def list_summaries() -> List[Dict[str, Any]]:
    return list(_load().get("summaries", {}).values())


def add_to_collection(name: str, summary_id: str) -> None:
    data = _load()
    cols = data.get("collections", {})
    items = cols.get(name, [])
    if summary_id not in items:
        items.append(summary_id)
    cols[name] = items
    data["collections"] = cols
    _save(data)


def remove_from_collection(name: str, summary_id: str) -> None:
    data = _load()
    cols = data.get("collections", {})
    items = [s for s in cols.get(name, []) if s != summary_id]
    cols[name] = items
    data["collections"] = cols
    _save(data)


def list_collections() -> Dict[str, List[str]]:
    return _load().get("collections", {})


def add_to_reading_list(url: str) -> None:
    if not url:
        return
    data = _load()
    items = data.get("reading_list", [])
    if not any(i.get("url") == url for i in items):
        items.append({"url": url, "added": _now_iso(), "status": "queued", "tags": [], "thumb": ""})
    data["reading_list"] = items
    _save(data)


def remove_from_reading_list(url: str) -> None:
    data = _load()
    items = data.get("reading_list", [])
    items = [i for i in items if i.get("url") != url]
    data["reading_list"] = items
    _save(data)


def clear_reading_list() -> None:
    data = _load()
    data["reading_list"] = []
    _save(data)


def get_reading_list() -> List[Dict[str, Any]]:
    data = _load()
    return data.get("reading_list", [])


def set_reading_list_tags(url: str, tags: List[str]) -> None:
    data = _load()
    rl = data.get("reading_list", [])
    for item in rl:
        if item.get("url") == url:
            item["tags"] = tags
            break
    data["reading_list"] = rl
    _save(data)


def set_reading_list_thumb(url: str, thumb_url: str) -> None:
    data = _load()
    rl = data.get("reading_list", [])
    for item in rl:
        if item.get("url") == url:
            item["thumb"] = thumb_url
            break
    data["reading_list"] = rl
    _save(data)


def export_workspace(fmt: str = "json") -> str:
    data = _load()
    if fmt == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    elif fmt == "csv":
        # Minimal CSV export of summaries
        import csv
        import io
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["summary_id","title","url","team","views","last_viewed","tournament"]) 
        for s in list_summaries():
            writer.writerow([
                s.get("summary_id"),
                s.get("title"),
                s.get("url"),
                " / ".join(s.get("team_names", [])),
                s.get("view_count", 0),
                s.get("last_viewed", ""),
                s.get("tournament", ""),
            ])
        return buf.getvalue()
    else:
        return ""



