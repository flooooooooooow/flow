from pathlib import Path

from flow.parser import parse_flow_code


ROOT = Path(__file__).resolve().parents[2]
KERNEL = ROOT / "kernel" / "x86_64" / "kernel.flow"


def test_base_kernel_parses_as_flow() -> None:
    source = KERNEL.read_text()
    declarations = parse_flow_code(source)

    assert declarations
    assert "export function kernel_main" in source
    assert "export function kernel_page_count" in source
    assert "@cEmbed" in source
