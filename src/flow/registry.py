"""
Flow package registry — name → version → source index.

Default index: <repo>/registry/index.json (bundled).
Overrides:
  FLOW_REGISTRY_PATH  — local index.json path
  FLOW_REGISTRY_URL   — remote JSON URL (fetched and cached under ~/.flow/cache)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
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


@dataclass
class PackageVersion:
    version: str
    yanked: bool = False
    git: Optional[str] = None
    tag: Optional[str] = None
    rev: Optional[str] = None
    branch: Optional[str] = None
    path: Optional[str] = None  # repo-relative or absolute

    def to_dep_spec(self, repo_root: Optional[Path] = None) -> Dict[str, Any]:
        """Convert to a flow.toml dependency table value."""
        if self.path:
            p = Path(self.path)
            if not p.is_absolute():
                root = repo_root or _repo_root()
                p = (root / self.path).resolve()
            return {"path": str(p)}
        if self.git:
            spec: Dict[str, Any] = {"git": self.git}
            if self.tag:
                spec["tag"] = self.tag
            elif self.rev:
                spec["rev"] = self.rev
            elif self.branch:
                spec["branch"] = self.branch
            return spec
        raise ValueError(f"version {self.version} has no path or git source")

    @classmethod
    def from_dict(cls, data: dict) -> "PackageVersion":
        return cls(
            version=str(data.get("version", "0.0.0")),
            yanked=bool(data.get("yanked", False)),
            git=data.get("git"),
            tag=data.get("tag"),
            rev=data.get("rev"),
            branch=data.get("branch"),
            path=data.get("path"),
        )


@dataclass
class PackageInfo:
    name: str
    description: str = ""
    homepage: str = ""
    license: str = "MIT"
    versions: List[PackageVersion] = field(default_factory=list)

    def live_versions(self) -> List[PackageVersion]:
        return [v for v in self.versions if not v.yanked]

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "PackageInfo":
        versions = [PackageVersion.from_dict(v) for v in data.get("versions", [])]
        return cls(
            name=name,
            description=data.get("description", ""),
            homepage=data.get("homepage", ""),
            license=data.get("license", "MIT"),
            versions=versions,
        )


# Back-compat aliases
PacketVersion = PackageVersion
PacketInfo = PackageInfo
CrateVersion = PackageVersion
CrateInfo = PackageInfo


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


def version_matches(requirement: str, version: str) -> bool:
    """Match requirements: *, exact, ^x.y.z, >=x.y.z."""
    req = (requirement or "*").strip()
    if req in ("*", "", "latest"):
        return True
    if req.startswith("^"):
        base = parse_semver(req[1:])
        ver = parse_semver(version)
        if ver[0] != base[0]:
            return False
        if base[0] == 0:
            return ver[1] == base[1] and ver[2] >= base[2]
        return ver >= base
    if req.startswith(">="):
        return parse_semver(version) >= parse_semver(req[2:].strip())
    if req.startswith("=="):
        return parse_semver(version) == parse_semver(req[2:].strip())
    return parse_semver(version) == parse_semver(req)


def resolve_version(
    package: PackageInfo, requirement: str = "*"
) -> Optional[PackageVersion]:
    """Pick the highest matching non-yanked version."""
    candidates = [
        v for v in package.live_versions() if version_matches(requirement, v.version)
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda v: parse_semver(v.version), reverse=True)
    return candidates[0]


class FlowRegistry:
    """Load and query the Flow package index."""

    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path or _default_index_path()
        self._data: Dict[str, Any] = {}
        self._packages: Dict[str, PackageInfo] = {}
        self.reload()

    def reload(self) -> None:
        url = os.environ.get("FLOW_REGISTRY_URL")
        if url and not os.environ.get("FLOW_REGISTRY_PATH"):
            self._data = self._fetch_remote(url)
        else:
            self._data = self._load_local(self.index_path)
        # Prefer "packages"; accept legacy "packets" / "crates" keys.
        packages_raw = (
            self._data.get("packages")
            or self._data.get("packets")
            or self._data.get("crates")
            or {}
        )
        self._packages = {
            name: PackageInfo.from_dict(name, meta)
            for name, meta in packages_raw.items()
        }

    def _load_local(self, path: Path) -> dict:
        if not path.exists():
            return {"version": 1, "name": "flow-packages", "packages": {}}
        return json.loads(path.read_text(encoding="utf-8"))

    def _fetch_remote(self, url: str) -> dict:
        cache = _cache_dir() / "index.json"
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
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

    def get(self, name: str) -> Optional[PackageInfo]:
        return self._packages.get(name)

    def search(self, query: str, limit: int = 20) -> List[PackageInfo]:
        q = query.lower().strip()
        if not q:
            return list(self._packages.values())[:limit]
        scored: List[Tuple[int, PackageInfo]] = []
        for package in self._packages.values():
            hay = f"{package.name} {package.description}".lower()
            if q not in hay:
                continue
            score = 0 if package.name.lower() == q else (
                1 if package.name.lower().startswith(q) else 2
            )
            scored.append((score, package))
        scored.sort(key=lambda t: (t[0], t[1].name))
        return [c for _, c in scored[:limit]]

    def resolve(self, name: str, requirement: str = "*") -> Optional[PackageVersion]:
        package = self.get(name)
        if not package:
            return None
        return resolve_version(package, requirement)

    def list_packages(self) -> List[PackageInfo]:
        return sorted(self._packages.values(), key=lambda c: c.name)

    def list_packets(self) -> List[PackageInfo]:
        return self.list_packages()

    def list_crates(self) -> List[PackageInfo]:
        return self.list_packages()

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
