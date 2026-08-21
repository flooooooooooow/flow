import os
import subprocess
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ENSURE_FLOWC = REPO_ROOT / "compiler" / "scripts" / "ensure_flowc.sh"


def _write_executable(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(0o755)


def _make_fixture(tmp_path: Path, *, stale_driver: bool) -> Path:
    (tmp_path / "compiler" / "scripts").mkdir(parents=True)
    (tmp_path / "compiler" / "src").mkdir(parents=True)
    (tmp_path / "compiler" / "build").mkdir(parents=True)

    ensure = tmp_path / "compiler" / "scripts" / "ensure_flowc.sh"
    ensure.write_text(ENSURE_FLOWC.read_text())
    ensure.chmod(0o755)

    source = tmp_path / "compiler" / "src" / "cgen.flow"
    source.write_text("# source marker\n")

    driver = tmp_path / "compiler" / "build" / "stage_a_driver_flow_self"
    _write_executable(driver, "#!/usr/bin/env bash\nexit 0\n")

    _write_executable(tmp_path / "flow", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(
        tmp_path / "compiler" / "scripts" / "roundtrip.sh",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "touch compiler/build/roundtrip-ran\n"
        "cat > compiler/build/stage_a_driver_flow_self <<'EOF'\n"
        "#!/usr/bin/env bash\n"
        "exit 0\n"
        "EOF\n"
        "chmod +x compiler/build/stage_a_driver_flow_self\n"
        "touch compiler/build/stage_a_driver_flow_self\n",
    )

    now = time.time()
    source_time = now - 10
    driver_time = now - 120 if stale_driver else now
    os.utime(source, (source_time, source_time))
    os.utime(driver, (driver_time, driver_time))

    return ensure


def test_stale_driver_is_rebuilt(tmp_path: Path) -> None:
    ensure = _make_fixture(tmp_path, stale_driver=True)

    result = subprocess.run(
        ["bash", str(ensure)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "compiler/build/stage_a_driver_flow_self"
    assert (tmp_path / "compiler" / "build" / "roundtrip-ran").exists()


def test_fresh_driver_is_reused(tmp_path: Path) -> None:
    ensure = _make_fixture(tmp_path, stale_driver=False)

    result = subprocess.run(
        ["bash", str(ensure)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "compiler/build/stage_a_driver_flow_self"
    assert not (tmp_path / "compiler" / "build" / "roundtrip-ran").exists()
