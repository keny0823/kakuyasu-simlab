#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


BASE_DIR = Path(__file__).parent
TARGETS = [BASE_DIR / "index.html", *sorted((BASE_DIR / "output").glob("*.html"))]
GA_ID_FILE = BASE_DIR / "ga_measurement_id.txt"

TEXT_REPLACEMENTS = {
    "Quick Start": "はじめに",
    "Good First Check": "最初の見比べ",
    "Decision Entry": "比較メニュー",
    "Top Picks": "注目サービス",
    "What We Compare": "比較の見方",
    "Before Apply": "申込前チェック",
    "All Reviews": "個別レビュー",
    "Review": "レビュー",
    "Audience": "向いている人",
    "Related": "関連比較",
    "Comparison Table": "比較表",
    "Comparison": "比較",
    "Ranking": "ランキング",
    "Guide": "選び方",
    "How To Choose": "選び方のコツ",
    "Snapshot Table": "早見表",
    "Plan A": "比較対象A",
    "Plan B": "比較対象B",
    "編集メモ": "比較のヒント",
}

IMAGE_REPLACEMENTS = {
    "hero-sim-network.svg": "hero-sim-network.png",
    "category-budget.svg": "category-budget.png",
    "category-support.svg": "category-support.png",
    "category-checklist.svg": "category-checklist.png",
}

BRANDS = {
    "ahamo": ("brand-ahamo", "ah"),
    "楽天モバイル": ("brand-rakuten", "楽"),
    "LINEMO": ("brand-linemo", "LI"),
    "UQモバイル": ("brand-uqmobile", "UQ"),
    "povo2.0": ("brand-povo", "po"),
    "ワイモバイル": ("brand-ymobile", "YM"),
    "IIJmio": ("brand-iijmio", "IIJ"),
    "mineo": ("brand-mineo", "mi"),
    "J:COMモバイル": ("brand-jcom", "J:C"),
    "日本通信SIM": ("brand-nihontsushin", "日通"),
    "NUROモバイル": ("brand-nuro", "NU"),
}


def load_ga_measurement_id() -> str:
    if not GA_ID_FILE.exists():
        return ""
    measurement_id = GA_ID_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"G-[A-Z0-9]+", measurement_id):
        return ""
    if "X" in measurement_id:
        return ""
    return measurement_id


def build_ga_snippet(measurement_id: str, is_root: bool) -> str:
    _ = is_root
    return (
        f'  <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>\n'
        "  <script>\n"
        "    window.dataLayer = window.dataLayer || [];\n"
        "    function gtag(){dataLayer.push(arguments);}\n"
        "    gtag('js', new Date());\n"
        f"    gtag('config', '{measurement_id}');\n"
        "  </script>\n"
    )


def inject_ga_snippet(text: str, measurement_id: str, is_root: bool) -> str:
    if not measurement_id:
        return text
    if "googletagmanager.com/gtag/js" in text or "gtag('config'" in text:
        return text
    snippet = build_ga_snippet(measurement_id, is_root)
    return text.replace("</head>", f"{snippet}</head>")


def apply_brand_marks(text: str) -> str:
    for carrier, (class_name, label) in BRANDS.items():
        text = re.sub(
            rf'<span class="summary-card-mark">\?\?</span>(\s*<div>\s*<strong>{re.escape(carrier)}</strong>)',
            rf'<span class="summary-card-mark {class_name}">{label}</span>\1',
            text,
        )
        text = re.sub(
            rf'<span class="carrier-mark">\?\?</span>(\s*<div>\s*<h3>{re.escape(carrier)}</h3>)',
            rf'<span class="carrier-mark {class_name}">{label}</span>\1',
            text,
        )
    return text


def main() -> None:
    ga_measurement_id = load_ga_measurement_id()
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "通信費を見直したい人へ。<br>料金・回線・サポートから選べます。",
            "通信費を見直したい人へ。<span>料金・回線・サポートで比べて選べます。</span>",
        )
        for src, dst in TEXT_REPLACEMENTS.items():
            text = text.replace(src, dst)
        for src, dst in IMAGE_REPLACEMENTS.items():
            text = text.replace(src, dst)
        text = text.replace(">c 2026 ", ">&copy; 2026 ")
        script_tag = '<script defer src="static/site.js"></script>' if path.name == "index.html" else '<script defer src="../static/site.js"></script>'
        if "site.js" not in text:
            text = text.replace("</head>", f'  {script_tag}\n</head>')
        text = inject_ga_snippet(text, ga_measurement_id, path.name == "index.html")
        text = apply_brand_marks(text)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
