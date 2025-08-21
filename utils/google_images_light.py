import os
import time
import random
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests  # type: ignore
import json
import hashlib
import threading


SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"


# Local JSON cache configuration
_DEFAULT_CACHE_FILE = os.path.join(
    os.path.dirname(__file__), "serp_cache_google_images_light.json"
)
_CACHE_LOCK = threading.Lock()


def _load_cache(cache_path: str) -> Dict[str, Any]:
    """
    Load cache from disk. Returns an empty dict on any error or missing file.
    """
    with _CACHE_LOCK:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}


def _save_cache(cache_path: str, cache: Dict[str, Any]) -> None:
    """
    Atomically write cache to disk. Best-effort; swallows IO errors.
    """
    with _CACHE_LOCK:
        tmp_path = cache_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, cache_path)
        except Exception:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass


def _make_cache_key(normalized_params: Dict[str, Any]) -> str:
    """Create a stable cache key from normalized request parameters."""
    try:
        payload = json.dumps(
            normalized_params, sort_keys=True, separators=(",", ":")
        )
    except TypeError:
        serializable: Dict[str, Any] = {}
        for k, v in normalized_params.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                serializable[k] = v
            else:
                serializable[k] = str(v)
        payload = json.dumps(serializable, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cache_get(
    cache_path: str, key: str, ttl_seconds: Optional[int]
) -> Optional[Dict[str, Any]]:
    cache = _load_cache(cache_path)
    entry = cache.get(key)
    if not isinstance(entry, dict):
        return None
    if ttl_seconds is not None:
        saved_at = entry.get("saved_at")
        try:
            if saved_at is None or (time.time() - float(saved_at)) > ttl_seconds:
                return None
        except Exception:
            return None
    response = entry.get("response")
    if isinstance(response, dict):
        return response
    return None


def _cache_put(
    cache_path: str,
    key: str,
    request_params: Dict[str, Any],
    response: Dict[str, Any],
) -> None:
    cache = _load_cache(cache_path)
    cache[key] = {
        "saved_at": time.time(),
        "request": request_params,
        "response": response,
    }
    _save_cache(cache_path, cache)


def _resolve_api_key(explicit_api_key: Optional[str]) -> str:
    """
    Resolve the SerpApi API key from an explicit argument or environment variables.

    Checks the following env vars in order if api_key isn't provided:
    - SERPAPI_API_KEY
    - SERP_API_KEY
    - SERPAPI_KEY
    """
    if explicit_api_key and explicit_api_key.strip():
        return explicit_api_key

    for env_var in ("SERPAPI_API_KEY", "SERP_API_KEY", "SERPAPI_KEY"):
        value = os.getenv(env_var)
        if value and value.strip():
            return value

    raise ValueError(
        "SerpApi API key not found. Pass api_key explicitly or set SERPAPI_API_KEY."
    )


def search_google_images_light(
    q: str,
    *,
    api_key: Optional[str] = None,
    device: str = "desktop",
    timeout: float = 20.0,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    no_cache: Optional[bool] = None,
    # Local persistent cache controls (do not confuse with SerpApi's no_cache)
    local_cache_path: Optional[str] = None,
    local_cache_ttl_seconds: Optional[int] = None,
    local_cache_bypass: bool = False,
    location: Optional[str] = None,
    uule: Optional[str] = None,
    google_domain: Optional[str] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    cr: Optional[str] = None,
    period_unit: Optional[str] = None,
    period_value: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tbs: Optional[str] = None,
    imgar: Optional[str] = None,
    imgsz: Optional[str] = None,
    image_color: Optional[str] = None,
    image_type: Optional[str] = None,
    licenses: Optional[str] = None,
    safe: Optional[str] = None,
    nfpr: Optional[int] = None,
    filter: Optional[int] = None,  # noqa: A002 - matches API param name
    start: Optional[int] = None,
    output: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Perform a Google Images Light search via SerpApi with retry + backoff.

    Returns the raw JSON payload as a dict. On mobile device={"mobile"}, results may
    include "original", "original_width", and "original_height" fields.
    """
    if not q or not q.strip():
        raise ValueError("q (query) cannot be empty")

    if device not in ("desktop", "mobile", "tablet"):
        raise ValueError("device must be one of: 'desktop', 'mobile', 'tablet'")

    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")

    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    resolved_key = _resolve_api_key(api_key)

    base_params: Dict[str, Any] = {
        "engine": "google_images_light",
        "q": q,
        "device": device,
        "api_key": resolved_key,
    }

    # Optional parameters (only include if not None)
    optional_params: Dict[str, Any] = {
        "no_cache": no_cache,
        "location": location,
        "uule": uule,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl,
        "cr": cr,
        "period_unit": period_unit,
        "period_value": period_value,
        "start_date": start_date,
        "end_date": end_date,
        "tbs": tbs,
        "imgar": imgar,
        "imgsz": imgsz,
        "image_color": image_color,
        "image_type": image_type,
        "licenses": licenses,
        "safe": safe,
        "nfpr": nfpr,
        "filter": filter,
        "start": start,
        "output": output,
    }

    # Remove None values
    for key in list(optional_params.keys()):
        if optional_params[key] is None:
            del optional_params[key]

    params = {**base_params, **optional_params}

    # Prepare local cache lookup
    cache_path = local_cache_path or _DEFAULT_CACHE_FILE
    cache_key_params = dict(params)
    # Do not include api_key in cache key
    cache_key_params.pop("api_key", None)
    cache_key = _make_cache_key(cache_key_params)

    if not local_cache_bypass:
        cached = _cache_get(cache_path, cache_key, ttl_seconds=local_cache_ttl_seconds)
        if isinstance(cached, dict) and cached:
            return cached

    last_exception: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(SERPAPI_SEARCH_URL, params=params, timeout=timeout)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            # Surface API-declared errors
            if "error" in data and data["error"]:
                raise RuntimeError(str(data["error"]))

            status = (
                data.get("search_metadata", {}).get("status")
                or data.get("search_status")
            )
            if status and status.lower() == "success":
                try:
                    _cache_put(cache_path, cache_key, cache_key_params, data)
                finally:
                    return data

            # If status isn't explicitly success, still return data if images_results present
            if isinstance(data.get("images_results"), list):
                try:
                    _cache_put(cache_path, cache_key, cache_key_params, data)
                finally:
                    return data

            raise RuntimeError(
                f"Unexpected response: status={status!r} params={params}"
            )

        except Exception as e:  # noqa: BLE001 - we re-raise the last one
            last_exception = e
            if attempt == max_retries:
                break
            delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
            print(
                f"Images Light search failed on attempt {attempt + 1}/{max_retries + 1}: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            time.sleep(delay)

    raise Exception(
        f"Google Images Light search failed after {max_retries + 1} attempts. Last error: {last_exception}"
    )


def extract_image_urls(results: Dict[str, Any], prefer_original: bool = True) -> List[str]:
    """
    Extract a list of image URLs from a search result.

    If prefer_original is True and the 'original' field is present (e.g. on mobile
    device results), returns that; otherwise falls back to the 'thumbnail' field.
    """
    images = results.get("images_results") or []
    urls: List[str] = []
    for item in images:
        if prefer_original and isinstance(item.get("original"), str):
            urls.append(item["original"])  # full resolution on mobile
        elif isinstance(item.get("serpapi_thumbnail"), str):
            urls.append(item["serpapi_thumbnail"])  # CDN-proxied thumbnail
        elif isinstance(item.get("thumbnail"), str):
            urls.append(item["thumbnail"])  # direct thumbnail
    return urls


def is_image_url_live(url: str, timeout: float = 10.0) -> bool:
    """
    Return True if the URL responds and appears to be an image.

    Strategy:
    - Try HEAD first (follow redirects). If Content-Type indicates image/* and status <400, accept.
    - If HEAD is not allowed or inconclusive, fallback to GET(stream=True), check status and Content-Type,
      and read a small chunk to ensure content exists.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_0) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        # Some servers reject HEAD; do not fail hard if so
        try:
            head_resp = requests.head(url, allow_redirects=True, timeout=timeout, headers=headers)
            if 200 <= head_resp.status_code < 400:
                content_type = (head_resp.headers.get("Content-Type") or "").lower()
                if content_type.startswith("image/"):
                    return True
                # If Content-Type missing or not clearly image, fall through to GET check
        except Exception:
            # Ignore HEAD-specific failures and try GET
            pass

        get_resp = requests.get(url, stream=True, timeout=timeout, headers=headers, allow_redirects=True)
        try:
            get_resp.raise_for_status()
            content_type = (get_resp.headers.get("Content-Type") or "").lower()
            if not content_type.startswith("image/"):
                return False
            # Ensure there is some content
            for _ in get_resp.iter_content(chunk_size=1024):
                return True
            return False
        finally:
            try:
                get_resp.close()
            except Exception:
                pass
    except Exception:
        return False


def filter_live_image_urls(urls: List[str], *, max_check: Optional[int] = None, timeout: float = 10.0) -> List[str]:
    """
    Filter a list of URLs down to those that are reachable image URLs.

    Args:
        urls: Candidate URLs.
        max_check: If provided, stop once this many live URLs have been found.
        timeout: Per-request timeout in seconds.
    """
    live: List[str] = []
    for url in urls:
        if not isinstance(url, str) or not url.strip():
            continue
        if is_image_url_live(url, timeout=timeout):
            live.append(url)
            if max_check is not None and len(live) >= max_check:
                break
    return live


def is_image_url_downloadable_for_fal(
    url: str,
    *,
    timeout: float = 10.0,
    allowed_content_types: Optional[List[str]] = None,
    min_bytes: int = 4096,
) -> bool:
    """
    Stricter check tailored for fal.ai fetcher compatibility.

    Rules:
    - Must be HTTPS
    - Content-Type must be in allowed_content_types (default: image/jpeg, image/png)
    - Reject SVG, GIF, WEBP explicitly
    - Require at least min_bytes of data
    """
    allowed = allowed_content_types or ["image/jpeg", "image/png"]

    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() != "https":
            return False
        lower_url = url.lower()
        if any(ext in lower_url for ext in [".svg", ".gif", ".webp"]):
            return False

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_0) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        }
        resp = requests.get(url, stream=True, timeout=timeout, headers=headers, allow_redirects=True)
        try:
            resp.raise_for_status()
            content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if content_type not in allowed:
                return False

            # Prefer content-length check
            content_length = resp.headers.get("Content-Length")
            if content_length and content_length.isdigit():
                if int(content_length) < min_bytes:
                    return False

            # Ensure we can read at least min_bytes (or first chunk)
            read_total = 0
            for chunk in resp.iter_content(2048):
                if not chunk:
                    break
                read_total += len(chunk)
                if read_total >= min_bytes:
                    return True
            # If we exit loop without reaching min_bytes, still accept if >0 and no content-length header
            return read_total >= max(1024, min_bytes // 2)
        finally:
            try:
                resp.close()
            except Exception:
                pass
    except Exception:
        return False


def next_page_params(results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse pagination info and return a dict of params suitable for the next call,
    or None if there is no next page link. This extracts query parameters from
    the 'serpapi_pagination.next' URL.
    """
    next_url = (
        results.get("serpapi_pagination", {}).get("next")
        if isinstance(results.get("serpapi_pagination"), dict)
        else None
    )
    if not next_url:
        return None

    try:
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(next_url)
        qs = parse_qs(parsed.query)
        # Flatten single-valued params
        flat: Dict[str, Any] = {}
        for key, values in qs.items():
            if not values:
                continue
            flat[key] = values[0] if len(values) == 1 else values
        return flat
    except Exception:
        return None


def search_google_images_light_urls(
    q: str,
    *,
    prefer_original: bool = True,
    verify_reachable: bool = False,
    fal_strict: bool = False,
    max_results: Optional[int] = None,
    **kwargs: Any,
) -> List[str]:
    """
    Convenience wrapper that returns only a list of image URLs.

    All keyword arguments are forwarded to search_google_images_light.
    Set prefer_original=True to prefer full-resolution URLs when available
    (typically on device="mobile" results).
    """
    results = search_google_images_light(q=q, **kwargs)
    urls = extract_image_urls(results, prefer_original=prefer_original)
    if max_results is not None:
        urls = urls[:max_results]
    if verify_reachable:
        if fal_strict:
            urls = [u for u in urls if is_image_url_downloadable_for_fal(u)]
        else:
            urls = filter_live_image_urls(urls)
    return urls


if __name__ == "__main__":
    # Minimal smoke test when run directly. Set SERPAPI_API_KEY before running.
    try:
        # Quick reachability checks (working and broken examples)
        working = "https://upload.wikimedia.org/wikipedia/commons/d/da/Dario_Amodei_at_TechCrunch_Disrupt_2023_01.jpg"
        broken = "https://www.hertzfoundation.org/wp-content/uploads/2024/11/dario-amodei-listing-1200x720.jpg"
        print(f"Working URL live? {is_image_url_live(working)}")
        print(f"Broken URL live?  {is_image_url_live(broken)}")

        urls = search_google_images_light_urls(
            q="Dario Amodei",
            device="mobile",
            prefer_original=True,
            verify_reachable=True,
            fal_strict=True,
            max_results=3,
        )
        print(f"Fetched {len(urls)} live image URL(s). Example: {urls[0] if urls else 'N/A'}")
    except Exception as e:
        print(f"Error: {e}")


