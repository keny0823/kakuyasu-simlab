#!/usr/bin/env python3
"""
Build the SIM affiliate site and run quality checks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).parent


def run(script_name: str) -> None:
    subprocess.run([sys.executable, str(BASE_DIR / script_name)], check=True)


def main() -> int:
    run("generate_site_images.py")
    run("generate.py")
    run("postprocess_generated_html.py")
    run("quality_check.py")
    print("BUILD AND CHECK COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
