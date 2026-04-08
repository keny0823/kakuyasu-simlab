#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).parent
IMAGE_DIR = BASE_DIR / "static" / "images"

FONT_BOLD = Path(r"C:\Windows\Fonts\YuGothB.ttc")
FONT_REGULAR = Path(r"C:\Windows\Fonts\meiryo.ttc")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def make_canvas(size: tuple[int, int], start: tuple[int, int, int], end: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, start)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(int(start[i] + (end[i] - start[i]) * ratio) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    return image


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int], outline=None, radius: int = 28) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2 if outline else 0)


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int, fill: tuple[int, int, int], bold: bool = False) -> None:
    draw.text(xy, text, font=font(size, bold), fill=fill)


def save_meta(path: Path, title: str) -> None:
    meta = {
        "generator": "local-design-rebuild",
        "title": title,
        "note": "Nanobanana2最終差し替えまでのサイト改善用PNG",
    }
    path.with_suffix(path.suffix + ".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_hero() -> None:
    image = make_canvas((1536, 1024), (243, 248, 255), (227, 239, 250))
    draw = ImageDraw.Draw(image)

    rounded_panel(draw, (58, 58, 1478, 966), (255, 255, 255), outline=(225, 235, 246), radius=42)
    rounded_panel(draw, (94, 96, 698, 920), (247, 250, 255), outline=(225, 235, 246), radius=34)
    rounded_panel(draw, (734, 96, 1440, 920), (15, 29, 55), radius=38)
    rounded_panel(draw, (780, 146, 1390, 544), (31, 61, 108), radius=28)
    rounded_panel(draw, (780, 576, 1082, 850), (19, 128, 175), radius=26)
    rounded_panel(draw, (1114, 576, 1390, 850), (27, 71, 125), radius=26)

    label(draw, (132, 140), "料金・回線・サポートを", 40, (31, 105, 255), True)
    label(draw, (132, 196), "見比べやすい構成", 54, (19, 34, 56), True)
    label(draw, (132, 296), "月額料金・データ容量・店頭対応を", 30, (89, 107, 132))
    label(draw, (132, 338), "最初の画面で迷わず確認できる比較サイト用ビジュアル", 30, (89, 107, 132))

    for idx, text in enumerate(["月額料金", "回線の種類", "店頭サポート", "eSIM対応"]):
        x0 = 132 + (idx % 2) * 248
        y0 = 430 + (idx // 2) * 138
        rounded_panel(draw, (x0, y0, x0 + 216, y0 + 112), (255, 255, 255), outline=(215, 226, 241), radius=24)
        label(draw, (x0 + 22, y0 + 24), text, 26, (19, 34, 56), True)
        label(draw, (x0 + 22, y0 + 60), "比較ポイントを整理", 20, (89, 107, 132))

    label(draw, (826, 182), "比較ダッシュボード", 28, (237, 244, 255), True)
    rounded_panel(draw, (826, 240, 1060, 486), (243, 247, 255), radius=22)
    rounded_panel(draw, (1088, 240, 1338, 322), (243, 247, 255), radius=18)
    rounded_panel(draw, (1088, 348, 1338, 486), (243, 247, 255), radius=18)
    rounded_panel(draw, (1160, 612, 1350, 798), (243, 247, 255), radius=18)

    label(draw, (850, 274), "月額料金", 22, (24, 51, 94), True)
    label(draw, (850, 312), "990円", 44, (31, 105, 255), True)
    label(draw, (850, 378), "容量", 22, (24, 51, 94), True)
    label(draw, (850, 416), "3GB / 20GB", 30, (19, 34, 56), True)
    label(draw, (1118, 266), "回線", 22, (24, 51, 94), True)
    label(draw, (1118, 386), "サポート", 22, (24, 51, 94), True)
    label(draw, (1142, 646), "店頭あり", 34, (31, 105, 255), True)
    label(draw, (1142, 700), "オンライン中心", 24, (89, 107, 132))

    for cy in (286, 376, 466):
        draw.ellipse((1358, cy, 1384, cy + 26), fill=(210, 227, 247))
    draw.ellipse((1358, 286, 1384, 312), fill=(255, 255, 255))

    path = IMAGE_DIR / "hero-sim-network.png"
    image.save(path, quality=95)
    save_meta(path, "格安SIMヒーロー画像")


def generate_budget() -> None:
    image = make_canvas((1024, 768), (242, 249, 255), (225, 239, 248))
    draw = ImageDraw.Draw(image)
    rounded_panel(draw, (58, 58, 966, 710), (255, 255, 255), outline=(223, 235, 245), radius=36)
    label(draw, (92, 100), "料金と容量を見比べる", 38, (19, 34, 56), True)
    label(draw, (92, 154), "価格帯とデータ容量がひと目で分かるカード", 24, (89, 107, 132))
    for idx, item in enumerate([("月額料金", "990円"), ("3GB", "小容量"), ("20GB", "中容量")]):
        x = 92 + idx * 286
        rounded_panel(draw, (x, 258, x + 244, 560), (247, 250, 255), outline=(223, 235, 245), radius=24)
        label(draw, (x + 24, 294), item[0], 26, (19, 34, 56), True)
        label(draw, (x + 24, 354), item[1], 42, (31, 105, 255), True)
        label(draw, (x + 24, 432), "比較しやすい表示", 22, (89, 107, 132))
    path = IMAGE_DIR / "category-budget.png"
    image.save(path, quality=95)
    save_meta(path, "料金比較カード画像")


def generate_support() -> None:
    image = make_canvas((1024, 768), (243, 249, 255), (228, 239, 249))
    draw = ImageDraw.Draw(image)
    rounded_panel(draw, (58, 58, 966, 710), (255, 255, 255), outline=(223, 235, 245), radius=36)
    label(draw, (92, 100), "サポート条件を比較", 38, (19, 34, 56), True)
    label(draw, (92, 154), "店頭相談・オンライン申込・チャット対応を整理", 24, (89, 107, 132))
    rounded_panel(draw, (92, 248, 422, 620), (244, 249, 255), outline=(223, 235, 245), radius=24)
    rounded_panel(draw, (468, 248, 932, 620), (19, 34, 56), radius=28)
    label(draw, (122, 290), "店頭サポート", 30, (19, 34, 56), True)
    label(draw, (122, 348), "あり / なし", 40, (31, 105, 255), True)
    label(draw, (122, 428), "相談しやすさを確認", 22, (89, 107, 132))
    label(draw, (500, 298), "申込導線チェック", 30, (239, 245, 255), True)
    label(draw, (500, 370), "オンライン完結", 42, (255, 255, 255), True)
    label(draw, (500, 438), "チャット・電話窓口", 24, (208, 224, 246))
    path = IMAGE_DIR / "category-support.png"
    image.save(path, quality=95)
    save_meta(path, "サポート比較カード画像")


def generate_checklist() -> None:
    image = make_canvas((1024, 768), (245, 249, 255), (228, 238, 248))
    draw = ImageDraw.Draw(image)
    rounded_panel(draw, (58, 58, 966, 710), (17, 28, 48), radius=36)
    label(draw, (92, 106), "申し込み前に確認したい3つ", 38, (244, 248, 255), True)
    items = [
        "キャンペーン条件",
        "通話オプション込みの総額",
        "開通方法とサポート窓口",
    ]
    for idx, item in enumerate(items):
        y = 214 + idx * 152
        rounded_panel(draw, (92, y, 932, y + 108), (244, 248, 255), radius=24)
        draw.ellipse((120, y + 28, 172, y + 80), fill=(31, 105, 255))
        label(draw, (138, y + 34), "✓", 32, (255, 255, 255), True)
        label(draw, (198, y + 28), item, 28, (19, 34, 56), True)
        label(draw, (198, y + 64), "比較前に確認しておきたい項目", 20, (89, 107, 132))
    path = IMAGE_DIR / "category-checklist.png"
    image.save(path, quality=95)
    save_meta(path, "申込前チェック画像")


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    generate_hero()
    generate_budget()
    generate_support()
    generate_checklist()


if __name__ == "__main__":
    main()
