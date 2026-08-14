from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_marker_audit_tool_help_exposes_ready_gate():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "run_live_receptor_marker_audit.py"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--ready-gate" in result.stdout
