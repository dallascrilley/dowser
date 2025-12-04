#!/usr/bin/env python3
"""
Cache utilities for convert-docs-to-skill analysis caching.

Provides functions to check, load, and save cached analysis results.
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

CACHE_DIR = Path(__file__).parent.parent / ".cache" / "analyses"
CACHE_EXPIRY_DAYS = 30


def normalize_tool_name(tool_name: str) -> str:
    """Normalize tool name for cache key."""
    return tool_name.lower().replace(" ", "-").replace("_", "-")


def compute_doc_hash(doc_content: str) -> str:
    """Compute SHA256 hash of documentation content."""
    return hashlib.sha256(doc_content.encode()).hexdigest()[:8]


def get_cache_key(tool_name: str, version: str, doc_hash: str) -> str:
    """Generate cache key from tool name, version, and doc hash."""
    normalized = normalize_tool_name(tool_name)
    version_str = version if version else "unknown"
    return f"{normalized}-{version_str}-{doc_hash}.json"


def get_cache_path(tool_name: str, version: str, doc_hash: str) -> Path:
    """Get full path to cache file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key = get_cache_key(tool_name, version, doc_hash)
    return CACHE_DIR / cache_key


def cache_exists(tool_name: str, version: str, doc_hash: str) -> bool:
    """Check if valid cache exists for tool/version/doc combination."""
    cache_path = get_cache_path(tool_name, version, doc_hash)
    
    if not cache_path.exists():
        return False
    
    try:
        with open(cache_path) as f:
            cache_data = json.load(f)
        
        # Check expiration
        expires_at = datetime.fromisoformat(cache_data["expires_at"])
        if datetime.now() > expires_at:
            # Cache expired, remove it
            cache_path.unlink()
            return False
        
        # Check version match
        if cache_data.get("version") != version:
            return False
        
        # Check doc hash match
        if cache_data.get("doc_hash") != doc_hash:
            return False
        
        return True
    
    except (json.JSONDecodeError, KeyError, ValueError):
        # Invalid cache file, remove it
        cache_path.unlink()
        return False


def load_from_cache(tool_name: str, version: str, doc_hash: str) -> Optional[Dict[str, Any]]:
    """Load cached analysis and design from cache."""
    if not cache_exists(tool_name, version, doc_hash):
        return None
    
    cache_path = get_cache_path(tool_name, version, doc_hash)
    
    try:
        with open(cache_path) as f:
            cache_data = json.load(f)
        
        return {
            "analysis": cache_data.get("analysis"),
            "component_design": cache_data.get("component_design"),
            "cached_at": cache_data.get("cached_at")
        }
    
    except (json.JSONDecodeError, KeyError):
        return None


def save_to_cache(
    tool_name: str,
    version: str,
    doc_hash: str,
    analysis: Dict[str, Any],
    component_design: Dict[str, Any]
) -> bool:
    """Save analysis and design to cache."""
    cache_path = get_cache_path(tool_name, version, doc_hash)
    
    now = datetime.now()
    expires_at = now + timedelta(days=CACHE_EXPIRY_DAYS)
    
    cache_data = {
        "tool_name": normalize_tool_name(tool_name),
        "version": version or "unknown",
        "doc_hash": doc_hash,
        "cached_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "analysis": analysis,
        "component_design": component_design
    }
    
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(cache_data, f, indent=2)
        return True
    except (OSError, json.JSONEncodeError):
        return False


def clear_expired_caches() -> int:
    """Remove expired cache files. Returns count of files removed."""
    if not CACHE_DIR.exists():
        return 0
    
    removed = 0
    now = datetime.now()
    
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
            
            expires_at = datetime.fromisoformat(cache_data["expires_at"])
            if now > expires_at:
                cache_file.unlink()
                removed += 1
        
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file, remove it
            cache_file.unlink()
            removed += 1
    
    return removed


def list_caches() -> list[Dict[str, Any]]:
    """List all cached analyses with metadata."""
    if not CACHE_DIR.exists():
        return []
    
    caches = []
    
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
            
            caches.append({
                "file": cache_file.name,
                "tool": cache_data.get("tool_name"),
                "version": cache_data.get("version"),
                "cached_at": cache_data.get("cached_at"),
                "expires_at": cache_data.get("expires_at"),
                "size": cache_file.stat().st_size
            })
        
        except (json.JSONDecodeError, KeyError):
            continue
    
    return sorted(caches, key=lambda x: x["cached_at"], reverse=True)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: cache_utils.py <command> [args]")
        print("Commands: list, clear-expired, check <tool> <version> <hash>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        caches = list_caches()
        if not caches:
            print("No cached analyses found.")
        else:
            print(f"Found {len(caches)} cached analyses:")
            for cache in caches:
                print(f"  {cache['tool']} v{cache['version']} - {cache['file']}")
                print(f"    Cached: {cache['cached_at']}")
                print(f"    Expires: {cache['expires_at']}")
    
    elif command == "clear-expired":
        removed = clear_expired_caches()
        print(f"Removed {removed} expired cache files.")
    
    elif command == "check":
        if len(sys.argv) < 5:
            print("Usage: cache_utils.py check <tool> <version> <hash>")
            sys.exit(1)
        
        tool_name = sys.argv[2]
        version = sys.argv[3]
        doc_hash = sys.argv[4]
        
        exists = cache_exists(tool_name, version, doc_hash)
        if exists:
            print(f"Cache exists for {tool_name} v{version}")
            cache_data = load_from_cache(tool_name, version, doc_hash)
            if cache_data:
                print(f"Cached at: {cache_data['cached_at']}")
        else:
            print(f"No valid cache for {tool_name} v{version}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

