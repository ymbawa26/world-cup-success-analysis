"""Small launcher for the Streamlit dashboard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    dashboard = PROJECT_ROOT / "app" / "dashboard.py"
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(dashboard)])


if __name__ == "__main__":
    raise SystemExit(main())
