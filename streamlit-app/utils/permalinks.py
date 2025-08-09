"""
Permalink and share-card utilities
Generates stable URLs (local scheme) and simple OpenGraph card data for teams.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional


def compute_team_fingerprint(team: List[Dict[str, Any]], title: Optional[str] = None, url: Optional[str] = None) -> str:
    """Compute a short fingerprint for a team composition."""
    payload = {
        "title": title or "",
        "url": url or "",
        "team": [
            {
                "name": p.get("name"),
                "item": p.get("item"),
                "ability": p.get("ability"),
                "tera": p.get("tera_type"),
                "moves": p.get("moves", []),
            }
            for p in (team or [])
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def build_permalink(base_url: str, fingerprint: str) -> str:
    """Build a shareable permalink. In local dev we just use a hash fragment."""
    if not base_url:
        base_url = "http://localhost:8501"
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    return f"{base_url}/?team={fingerprint}"


def build_opengraph_card(title: str, description: str) -> Dict[str, str]:
    """Return meta tag values for OpenGraph-like cards (used by external hosts)."""
    # The Streamlit app cannot set HTTP headers, but we can expose data for hosting layers
    return {
        "og:title": title or "Pokemon VGC Team",
        "og:description": description or "Team analysis and composition",
        "twitter:card": "summary_large_image",
    }


