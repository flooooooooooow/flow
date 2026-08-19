"""Single source of truth for the Flow language / compiler version.

This is the canonical value. Every other surface (manifests, docs headers,
the CLI banner, the Homebrew formula) mirrors it, and CI fails on drift.

Do not hand-edit the mirrors. Bump with::

    python3 scripts/sync_version.py --set 0.12.0

Tagging ``v*`` also triggers .github/workflows/version-bump.yml, which opens
a PR syncing the tree to the tag.
"""

__version__ = "0.12.0"
