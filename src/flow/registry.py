"""
Flow package registry index, as `flow publish` writes it.

Reading the index, choosing versions and installing packages is the Flow
package manager in compiler/src/pkg.flow. What is left here is
FlowPackageManager.publish's side: loading and rewriting a local index.json.

Default index: <repo>/registry/index.json (bundled).
Overrides:
  FLOW_REGISTRY_PATH  local index.json path
  FLOW_REGISTRY_URL   remote JSON URL (fetched and cached under ~/.flow/cache)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_index_path() -> Path:
    override = os.environ.get("FLOW_REGISTRY_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return _repo_root() / "registry" / "index.json"


def _cache_dir() -> Path:
    base = Path(os.environ.get("FLOW_HOME", Path.home() / ".flow"))
    d = base / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def parse_semver(v: str) -> Tuple[int, int, int]:
    """Parse leading X.Y.Z; non-numeric junk after is ignored."""
    core = v.strip().lstrip("v").split("+")[0].split("-")[0]
    parts = core.split(".")
    nums = []
    for i in range(3):
        try:
            nums.append(int(parts[i]) if i < len(parts) else 0)
        except ValueError:
            nums.append(0)
    return nums[0], nums[1], nums[2]


class FlowRegistry:
    """Load the Flow package index and register versions in a local one."""

    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path or _default_index_path()
        self._data: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        url = os.environ.get("FLOW_REGISTRY_URL")
        if url and not os.environ.get("FLOW_REGISTRY_PATH"):
            self._data = self._fetch_remote(url)
        else:
            self._data = self._load_local(self.index_path)

    def _load_local(self, path: Path) -> dict:
        if not path.exists():
            return {"version": 1, "name": "flow-packages", "packages": {}}
        return json.loads(path.read_text(encoding="utf-8"))

    def _fetch_remote(self, url: str) -> dict:
        cache = _cache_dir() / "index.json"
        if not url.startswith(("https://", "http://")):
            raise ValueError(f"registry URL must be http(s): {url}")
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:  # nosec B310 - scheme checked above
                raw = resp.read().decode("utf-8")
            cache.write_text(raw, encoding="utf-8")
            return json.loads(raw)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if cache.exists():
                return json.loads(cache.read_text(encoding="utf-8"))
            raise RuntimeError(f"Failed to fetch registry index from {url}: {e}") from e

    @property
    def name(self) -> str:
        return str(self._data.get("name", "flow-packages"))

    def publish_local(
        self,
        *,
        name: str,
        version: str,
        description: str = "",
        license: str = "MIT",
        homepage: str = "",
        git: Optional[str] = None,
        tag: Optional[str] = None,
        rev: Optional[str] = None,
        path: Optional[str] = None,
        yanked: bool = False,
    ) -> Path:
        """Register (or update) a package version in the local index.json."""
        path_obj = self.index_path
        data = self._load_local(path_obj)
        for legacy in ("crates", "packets"):
            if legacy in data and "packages" not in data:
                data["packages"] = data.pop(legacy)
        packages = data.setdefault("packages", {})
        data["name"] = data.get("name") or "flow-packages"
        entry = packages.setdefault(
            name,
            {
                "description": description,
                "homepage": homepage,
                "license": license,
                "versions": [],
            },
        )
        if description:
            entry["description"] = description
        if homepage:
            entry["homepage"] = homepage
        if license:
            entry["license"] = license

        versions: List[dict] = entry.setdefault("versions", [])
        versions = [v for v in versions if str(v.get("version")) != version]
        ver_obj: Dict[str, Any] = {"version": version, "yanked": yanked}
        if path:
            ver_obj["path"] = path
        if git:
            ver_obj["git"] = git
            if tag:
                ver_obj["tag"] = tag
            if rev:
                ver_obj["rev"] = rev
        versions.append(ver_obj)
        versions.sort(key=lambda v: parse_semver(str(v.get("version", "0"))), reverse=True)
        entry["versions"] = versions
        packages[name] = entry
        data["packages"] = packages
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        path_obj.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.reload()
        return path_obj
