#!/usr/bin/env python3
"""prototype/index.html のスクリーンショットを docs/assets/proximity-role-demo.png へ保存する。

macOSローカルのGoogle Chromeバイナリをheadlessモードで呼び出す実装。
CI・他OSでは動作しない可能性がある（OPEN-ISSUES.md「スクリーンショット自動化のOS依存」参照）。
"""
import shutil
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
PROTOTYPE_PATH = APP_ROOT / "prototype" / "index.html"
OUTPUT_PATH = APP_ROOT / "docs" / "assets" / "proximity-role-demo.png"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("chromium"),
    shutil.which("google-chrome"),
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    return None


def main():
    if not PROTOTYPE_PATH.exists():
        print("prototype/index.html が無い。先に make demo を実行してください", file=sys.stderr)
        sys.exit(2)

    chrome = find_chrome()
    if not chrome:
        print(
            "Chrome/Chromiumが見つからない。手動でprototype/index.htmlを開きスクリーンショットを保存してください: "
            f"{OUTPUT_PATH}",
            file=sys.stderr,
        )
        sys.exit(3)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1366,768",
        f"--screenshot={OUTPUT_PATH}",
        PROTOTYPE_PATH.resolve().as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0 or not OUTPUT_PATH.exists():
        print("スクリーンショット生成に失敗しました", file=sys.stderr)
        print(result.stdout, result.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
