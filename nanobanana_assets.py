#!/usr/bin/env python3
"""
Nanobanana2 asset workflow helper.

This script does three things:
1. writes project prompts from a manifest
2. verifies that required raster images exist
3. opens Gemini Web with the prompt prefilled, using an existing browser profile

Notes:
- Actual image generation still depends on the logged-in Gemini session.
- We keep a metadata sidecar next to each generated image so future checks can
  confirm the asset was intended for Nanobanana2.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).parent
DEFAULT_MANIFEST = BASE_DIR / "nanobanana_manifest.json"


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prompt_dir() -> Path:
    path = BASE_DIR / "nanobanana_prompts"
    path.mkdir(exist_ok=True)
    return path


def default_download_dir() -> Path:
    return Path.home() / "Downloads"


def metadata_path(target_path: Path) -> Path:
    return target_path.with_suffix(target_path.suffix + ".json")


def asset_map(manifest: dict) -> dict[str, dict]:
    return {asset["id"]: asset for asset in manifest["assets"]}


def ensure_asset(manifest: dict, asset_id: str) -> dict:
    assets = asset_map(manifest)
    if asset_id not in assets:
        raise KeyError(asset_id)
    return assets[asset_id]


def ensure_prompt(asset: dict) -> Path:
    prompt_path = prompt_dir() / f"{asset['id']}.txt"
    if not prompt_path.exists():
        prompt_path.write_text(asset["prompt"], encoding="utf-8")
    return prompt_path


def write_prompts(manifest: dict) -> None:
    out_dir = prompt_dir()
    for asset in manifest["assets"]:
        prompt_path = out_dir / f"{asset['id']}.txt"
        prompt_path.write_text(asset["prompt"], encoding="utf-8")
        print(f"PROMPT_WRITTEN {prompt_path}")


def verify_assets(manifest: dict, strict: bool = False) -> int:
    issues: list[str] = []
    for asset in manifest["assets"]:
        target = BASE_DIR / asset["target_path"]
        if target.exists():
            meta = metadata_path(target)
            if not meta.exists():
                issues.append(f"{asset['id']}: metadata missing -> {meta.name}")
                continue
            data = json.loads(meta.read_text(encoding="utf-8"))
            if data.get("generator") != manifest["generator"]:
                issues.append(f"{asset['id']}: generator mismatch in {meta.name}")
            continue

        fallback = BASE_DIR / asset.get("fallback_path", "")
        if strict or not fallback.exists():
            issues.append(f"{asset['id']}: generated raster image missing -> {target}")

    if issues:
        print("NANOBANANA_VERIFY_FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("NANOBANANA_VERIFY_PASSED")
    return 0


def register_generated_asset(manifest: dict, asset_id: str, file_path: Path) -> int:
    assets = asset_map(manifest)
    if asset_id not in assets:
        print(f"UNKNOWN_ASSET {asset_id}")
        return 1

    asset = assets[asset_id]
    target = BASE_DIR / asset["target_path"]
    target.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        print(f"FILE_NOT_FOUND {file_path}")
        return 1

    target.write_bytes(file_path.read_bytes())
    meta = {
        "generator": manifest["generator"],
        "asset_id": asset_id,
        "source_file": str(file_path),
        "target_path": asset["target_path"],
        "size": asset["size"],
    }
    metadata_path(target).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"ASSET_REGISTERED {target}")
    return 0


def is_candidate_image(path: Path) -> bool:
    valid_exts = {".png", ".jpg", ".jpeg", ".webp"}
    temp_exts = {".crdownload", ".part", ".tmp"}
    return path.is_file() and path.suffix.lower() in valid_exts and path.suffix.lower() not in temp_exts


def is_stable_file(path: Path, delay_sec: float = 1.2) -> bool:
    if not path.exists():
        return False
    first = path.stat().st_size
    time.sleep(delay_sec)
    if not path.exists():
        return False
    second = path.stat().st_size
    return first == second and second > 0


def find_recent_download(download_dir: Path, started_at: float, seen: set[str]) -> Path | None:
    if not download_dir.exists():
        return None

    candidates = sorted(
        (p for p in download_dir.iterdir() if is_candidate_image(p)),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        resolved = str(path.resolve())
        mtime = path.stat().st_mtime
        if resolved in seen and mtime < started_at:
            continue
        if mtime < started_at:
            continue
        if is_stable_file(path):
            return path
    return None


def describe_asset(manifest: dict, asset_id: str) -> int:
    try:
        asset = ensure_asset(manifest, asset_id)
    except KeyError:
        print(f"UNKNOWN_ASSET {asset_id}")
        return 1

    print(json.dumps(asset, ensure_ascii=False, indent=2))
    return 0


def list_assets(manifest: dict) -> int:
    for asset in manifest["assets"]:
        print(f"{asset['id']}: {asset['target_path']}")
    return 0


def open_gemini_for_asset(manifest: dict, asset_id: str) -> int:
    assets = asset_map(manifest)
    if asset_id not in assets:
        print(f"UNKNOWN_ASSET {asset_id}")
        return 1

    asset = assets[asset_id]
    config_path = (BASE_DIR / manifest["profile_config"]).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    profile_dir = (config_path.parent / config["browser"]["user_data_dir"]).resolve()
    prompt_path = ensure_prompt(asset)

    script = f"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

profile_dir = Path(r"{profile_dir}")
prompt = Path(r"{prompt_path}").read_text(encoding="utf-8")
selectors = [
    'rich-textarea .ql-editor',
    '.ql-editor[contenteditable="true"]',
    'div[role="textbox"]',
    'rich-textarea div[contenteditable="true"]',
    'div[contenteditable="true"]',
]
mode_buttons = [
    'button:has-text("画像を作成")',
    'button:has-text("画像を生成")',
    'button:has-text("Create image")',
    'button:has-text("Images")',
    'button:has-text("Nano Banana")',
    'button:has-text("Imagen")',
]

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=False,
        slow_mo=50,
        viewport={{"width": 1440, "height": 900}},
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        no_viewport=True,
    )
    page = ctx.new_page()
    page.goto("https://gemini.google.com/app")
    page.wait_for_load_state("domcontentloaded")
    time.sleep(4)

    for sel in mode_buttons:
        try:
            button = page.locator(sel).first
            if button.is_visible(timeout=1000):
                button.click()
                time.sleep(1)
                break
        except Exception:
            pass

    for sel in selectors:
        try:
            box = page.locator(sel).first
            if box.is_visible(timeout=3000):
                box.click()
                page.keyboard.press("Control+A")
                page.keyboard.type(prompt)
                break
        except Exception:
            pass

    print("GEMINI_READY")
    print("Prompt inserted for asset: {asset_id}")
    print("Generate the image in Gemini, download it, then run:")
    print(r'python sim-affiliate\\nanobanana_assets.py register {asset_id} "DOWNLOADED_FILE_PATH"')
    input("After confirming the prompt is inserted, press Enter to close...")
    ctx.close()
"""

    temp_script = BASE_DIR / "_tmp_open_nanobanana.py"
    temp_script.write_text(script, encoding="utf-8")
    try:
        os.system(f'"{sys.executable}" "{temp_script}"')
    finally:
        if temp_script.exists():
            temp_script.unlink()
    return 0


def run_asset_pipeline(
    manifest: dict,
    asset_id: str,
    download_dir: Path,
    timeout_sec: int,
) -> int:
    try:
        asset = ensure_asset(manifest, asset_id)
    except KeyError:
        print(f"UNKNOWN_ASSET {asset_id}")
        return 1

    config_path = (BASE_DIR / manifest["profile_config"]).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    profile_dir = (config_path.parent / config["browser"]["user_data_dir"]).resolve()
    prompt_path = ensure_prompt(asset)
    prompt = prompt_path.read_text(encoding="utf-8")

    download_dir = download_dir.expanduser().resolve()
    download_dir.mkdir(parents=True, exist_ok=True)
    seen = {str(path.resolve()) for path in download_dir.iterdir() if path.is_file()}
    started_at = time.time()

    from playwright.sync_api import sync_playwright

    selectors = [
        'rich-textarea .ql-editor',
        '.ql-editor[contenteditable="true"]',
        'div[role="textbox"]',
        'rich-textarea div[contenteditable="true"]',
        'div[contenteditable="true"]',
    ]
    mode_buttons = [
        'button:has-text("画像を作成")',
        'button:has-text("画像を生成")',
        'button:has-text("Create image")',
        'button:has-text("Images")',
        'button:has-text("Nano Banana")',
        'button:has-text("Imagen")',
    ]

    print(f"NANOBANANA_RUN_START asset={asset_id}")
    print(f"DOWNLOAD_DIR {download_dir}")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            slow_mo=50,
            viewport={"width": 1440, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            no_viewport=True,
            accept_downloads=True,
        )
        try:
            page = ctx.new_page()
            page.goto("https://gemini.google.com/app")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(4)

            for sel in mode_buttons:
                try:
                    button = page.locator(sel).first
                    if button.is_visible(timeout=1000):
                        button.click()
                        time.sleep(1)
                        break
                except Exception:
                    pass

            inserted = False
            for sel in selectors:
                try:
                    box = page.locator(sel).first
                    if box.is_visible(timeout=3000):
                        box.click()
                        page.keyboard.press("Control+A")
                        page.keyboard.type(prompt)
                        inserted = True
                        break
                except Exception:
                    pass

            if not inserted:
                print("PROMPT_INSERT_FAILED")
                return 1

            print("GEMINI_READY")
            print(f"Prompt inserted for asset: {asset_id}")
            print("Generate and download the image in Gemini.")
            print("This runner will watch your Downloads folder and auto-register the first new image.")

            deadline = time.time() + timeout_sec
            found: Path | None = None
            while time.time() < deadline:
                page.wait_for_timeout(1000)
                found = find_recent_download(download_dir, started_at, seen)
                if found:
                    print(f"DOWNLOAD_DETECTED {found}")
                    return register_generated_asset(manifest, asset_id, found)

            print("DOWNLOAD_WAIT_TIMEOUT")
            print(
                f'Run manually after download: python sim-affiliate\\nanobanana_assets.py register {asset_id} "DOWNLOADED_FILE_PATH"'
            )
            return 1
        finally:
            ctx.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("write-prompts")
    sub.add_parser("list-assets")

    verify = sub.add_parser("verify")
    verify.add_argument("--strict", action="store_true")

    open_cmd = sub.add_parser("open-gemini")
    open_cmd.add_argument("asset_id")

    show = sub.add_parser("show")
    show.add_argument("asset_id")

    register = sub.add_parser("register")
    register.add_argument("asset_id")
    register.add_argument("file_path")

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("asset_id")
    run_cmd.add_argument("--downloads-dir", default=str(default_download_dir()))
    run_cmd.add_argument("--timeout-sec", type=int, default=900)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest(Path(args.manifest))

    if args.command == "write-prompts":
        write_prompts(manifest)
        return 0
    if args.command == "list-assets":
        return list_assets(manifest)
    if args.command == "verify":
        return verify_assets(manifest, strict=args.strict)
    if args.command == "show":
        return describe_asset(manifest, args.asset_id)
    if args.command == "open-gemini":
        return open_gemini_for_asset(manifest, args.asset_id)
    if args.command == "register":
        return register_generated_asset(manifest, args.asset_id, Path(args.file_path))
    if args.command == "run":
        return run_asset_pipeline(
            manifest,
            args.asset_id,
            Path(args.downloads_dir),
            args.timeout_sec,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
