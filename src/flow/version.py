"""Single source of truth for the Flow language / compiler version.

This is the canonical value. Every other surface (manifests, docs headers,
the CLI banner, the Homebrew formula) mirrors it.

Do not hand-edit the mirrors. Check or update them locally with::

    python3 scripts/sync_version.py --check
    python3 scripts/sync_version.py --set 1.0.2

Release artifacts and Homebrew metadata are qualified and synchronized locally;
do not rely on hosted workflow execution for release validation or publication.
"""

__version__ = "1.0.2"
