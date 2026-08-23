#!/usr/bin/env python3
"""実データ位置マップのオフラインスクリーンショットを保存する。"""
import shutil
import subprocess
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent.parent
PAGE_PATH = APP_ROOT / "prototype" / "real-map.html"
OUTPUT_PATH = APP_ROOT / "docs" / "assets" / "proximity-role-real-map.png"
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("chromium"),
    shutil.which("google-chrome"),
]


def main() -> None:
    if not PAGE_PATH.exists():
        print("prototype/real-map.html が無い。先に make real-map を実行してください", file=sys.stderr)
        sys.exit(2)
    chrome = next((candidate for candidate in CHROME_CANDIDATES if candidate and Path(candidate).exists()), None)
    if not chrome:
        print("Chrome/Chromiumが見つからないため、スクリーンショットを生成できません", file=sys.stderr)
        sys.exit(3)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1366,768",
        f"--screenshot={OUTPUT_PATH}",
        PAGE_PATH.resolve().as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode != 0 or not OUTPUT_PATH.exists():
        print("実データマップのスクリーンショット生成に失敗しました", file=sys.stderr)
        print(result.stdout, result.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
