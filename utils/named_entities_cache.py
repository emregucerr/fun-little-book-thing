import json
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional


# Default cache file alongside this module
_DEFAULT_CACHE_FILE = os.path.join(
    os.path.dirname(__file__), "named_entities_cache.json"
)
_CACHE_LOCK = threading.Lock()


def _normalize_name_for_key(name: str) -> str:
    """Create a canonical key for a named entity (lowercased, no punctuation/whitespace)."""
    return re.sub(r"[^\w]", "", (name or "").lower())


def _load_cache(cache_path: str) -> Dict[str, Any]:
    """Load the JSON cache from disk. Returns an empty dict on error/missing file."""
    with _CACHE_LOCK:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}


def _save_cache(cache_path: str, cache: Dict[str, Any]) -> None:
    """Atomically write the JSON cache to disk (best-effort)."""
    with _CACHE_LOCK:
        tmp_path = cache_path + ".tmp"
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, cache_path)
        except Exception:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass


def get_entity_by_name(
    name: str, *, cache_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Fetch a cached entity by human-readable name (case/punct/space-insensitive)."""
    if not name:
        return None
    key = _normalize_name_for_key(name)
    path = cache_path or _DEFAULT_CACHE_FILE
    cache = _load_cache(path)
    entry = cache.get(key)
    if isinstance(entry, dict):
        # Ensure mandatory fields exist
        if entry.get("name"):
            return entry
    return None


def upsert_entity(
    entity: Dict[str, Any], *, cache_path: Optional[str] = None
) -> Dict[str, Any]:
    """Insert or update a cached entity. Requires 'name' in the entity dict."""
    name = entity.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("entity must contain a non-empty 'name' field")

    key = _normalize_name_for_key(name)
    path = cache_path or _DEFAULT_CACHE_FILE

    # Store a minimal, stable representation
    to_store: Dict[str, Any] = {
        "name": entity.get("name", ""),
        "description": entity.get("description", ""),
        "prompt": entity.get("prompt", ""),
        "image": entity.get("image", ""),
        "saved_at": time.time(),
    }

    cache = _load_cache(path)
    cache[key] = to_store
    _save_cache(path, cache)
    return to_store


def load_all_entities(*, cache_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load all cached named entities as a list of dicts."""
    path = cache_path or _DEFAULT_CACHE_FILE
    cache = _load_cache(path)
    if not isinstance(cache, dict):
        return []
    entities: List[Dict[str, Any]] = []
    for entry in cache.values():
        if isinstance(entry, dict) and entry.get("name"):
            entities.append(entry)
    return entities


