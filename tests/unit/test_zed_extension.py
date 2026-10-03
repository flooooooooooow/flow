import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
ZED_DIR = ROOT / "third_party" / "integrations" / "zed"
FLOW_LANG_DIR = ZED_DIR / "languages" / "flow"


def test_zed_extension_manifest_exists_and_valid():
    extension_toml = ZED_DIR / "extension.toml"
    assert extension_toml.exists(), "extension.toml must exist"
    data = tomllib.loads(extension_toml.read_text(encoding="utf-8"))

    assert data.get("id") == "flow"
    assert data.get("name") == "Flow"
    assert data.get("version") == "0.1.0"
    assert data.get("schema_version") == 1
    assert "language_servers" in data
    assert "flow-lsp" in data["language_servers"]
    assert "Flow" in data["language_servers"]["flow-lsp"]["languages"]


def test_zed_language_config_exists_and_valid():
    config_toml = FLOW_LANG_DIR / "config.toml"
    assert config_toml.exists(), "config.toml must exist"
    data = tomllib.loads(config_toml.read_text(encoding="utf-8"))

    assert data.get("name") == "Flow"
    assert data.get("grammar") == "flow"
    assert "flow" in data.get("path_suffixes", [])
    assert "# " in data.get("line_comments", [])
    assert "language_servers" in data
    assert "flow-lsp" in data["language_servers"]


def test_zed_tree_sitter_queries_exist_and_non_empty():
    query_files = ["highlights.scm", "brackets.scm", "indents.scm", "outline.scm"]
    for qf in query_files:
        path = FLOW_LANG_DIR / qf
        assert path.exists(), f"Query file {qf} must exist"
        content = path.read_text(encoding="utf-8").strip()
        assert len(content) > 0, f"Query file {qf} must not be empty"


def test_zed_semantic_token_rules_valid_json():
    json_path = FLOW_LANG_DIR / "semantic_token_rules.json"
    assert json_path.exists(), "semantic_token_rules.json must exist"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    assert isinstance(data, list)
    assert len(data) > 0
    token_types = [rule.get("token_type") for rule in data if "token_type" in rule]
    assert "keyword" in token_types
    assert "type" in token_types
    assert "function" in token_types


def test_zed_readme_documentation_exists():
    readme = ZED_DIR / "README.md"
    assert readme.exists(), "README.md must exist in third_party/integrations/zed/"
    text = readme.read_text(encoding="utf-8")
    assert "Flow Language Extension for Zed" in text
    assert "Installation" in text
    assert "flow-lsp" in text
