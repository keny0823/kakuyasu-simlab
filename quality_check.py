#!/usr/bin/env python3
"""
Quality checks for the SIM affiliate site.

Checks:
- risky ad expressions in generated HTML
- broken local links between generated pages
- missing PR disclosure block
"""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).parent
INDEX_FILE = BASE_DIR / "index.html"
OUTPUT_DIR = BASE_DIR / "output"

BANNED_PHRASES = [
    "業界最安",
    "日本最安",
    "最安級",
    "コスパ最強",
    "完全無料",
    "圧倒的に安い",
    "本当におすすめできる",
]

IMAGE_MANIFEST_FILE = BASE_DIR / "nanobanana_manifest.json"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href:
            self.hrefs.append(href)


def generated_html_files() -> list[Path]:
    files = [INDEX_FILE]
    files.extend(sorted(OUTPUT_DIR.glob("*.html")))
    return files


def find_phrase_issues(files: list[Path]) -> list[str]:
    issues: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for phrase in BANNED_PHRASES:
            if phrase in text:
                issues.append(f"{path.relative_to(BASE_DIR)}: 禁止表現 `{phrase}` が残っています")
    return issues


def find_disclosure_issues(files: list[Path]) -> list[str]:
    issues: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "当サイトにはアフィリエイト広告が含まれます" not in text:
            issues.append(f"{path.relative_to(BASE_DIR)}: PR表記が見つかりません")
    return issues


def is_local_html_link(href: str) -> bool:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return False
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
        return False
    return href.endswith(".html")


def resolve_local_link(source: Path, href: str) -> Path:
    return (source.parent / href).resolve()


def find_broken_links(files: list[Path]) -> list[str]:
    issues: list[str] = []
    for path in files:
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for href in parser.hrefs:
            if not is_local_html_link(href):
                continue
            target = resolve_local_link(path, href)
            if not target.exists():
                issues.append(
                    f"{path.relative_to(BASE_DIR)}: リンク先が存在しません -> {href}"
                )
    return issues


def find_nanobanana_asset_issues() -> list[str]:
    if not IMAGE_MANIFEST_FILE.exists():
        return []

    manifest = json.loads(IMAGE_MANIFEST_FILE.read_text(encoding="utf-8"))
    issues: list[str] = []
    for asset in manifest.get("assets", []):
        target = BASE_DIR / asset["target_path"]
        if target.exists():
            meta = target.with_suffix(target.suffix + ".json")
            if not meta.exists():
                issues.append(f"{asset['target_path']}: 画像メタデータがありません")
            continue

        fallback = BASE_DIR / asset.get("fallback_path", "")
        if fallback.exists():
            issues.append(f"{asset['target_path']}: Nanobanana2画像未生成のためフォールバック使用中")
        else:
            issues.append(f"{asset['target_path']}: 必須画像がありません")
    return issues


def main() -> int:
    files = generated_html_files()
    issues = []
    issues.extend(find_phrase_issues(files))
    issues.extend(find_disclosure_issues(files))
    issues.extend(find_broken_links(files))
    if "--strict-images" in sys.argv:
        issues.extend(find_nanobanana_asset_issues())

    if issues:
        print("QUALITY CHECK FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"QUALITY CHECK PASSED ({len(files)} HTML files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
