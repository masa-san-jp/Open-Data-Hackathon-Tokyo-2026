#!/usr/bin/env python3
"""エージェントとCIが共通で使う、まちかどQRの受け入れ検証。"""
from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=BASE, check=True)


def main() -> int:
    for path in sorted((BASE / "scripts").glob("*.py")):
        py_compile.compile(str(path), doraise=True)
    for path in sorted((BASE / "tests").glob("*.py")):
        py_compile.compile(str(path), doraise=True)
    print("✓ Python syntax")

    node = shutil.which("node")
    if node:
        run([node, "--check", "src/app.js"])
        print("✓ JavaScript syntax")
    else:
        print("⚠ node が無いため JavaScript 構文検査を省略")

    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    print("✓ まちかどQR verification passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, subprocess.CalledProcessError, py_compile.PyCompileError) as error:
        print(f"✗ verification failed: {error}", file=sys.stderr)
        sys.exit(1)
