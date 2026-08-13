"""Single source of truth for the Flow language / compiler version.

Keep this in sync with ROADMAP.md "Current version". Other surfaces
(CLI help, pyproject.toml, REPL banner, LSP initialize) should import
or mirror this value — do not hardcode divergent strings.
"""

__version__ = "0.11.0"
