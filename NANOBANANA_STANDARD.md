# Nanobanana2 Website Image Standard

このサイトでは、今後の画像追加も含めて `Nanobanana2` を基準に運用する。

## 基本ルール

- ヒーロー画像、カテゴリ画像、特集バナー、比較カード用ビジュアルは `Nanobanana2` を第一選択にする
- 画像要件は `nanobanana_manifest.json` にまとめる
- 生成画像は `png` または `webp` で保存する
- 登録時に同名のメタデータ JSON を残す
- 本番公開前に `quality_check.py --strict-images` を通す
- SVG や仮画像のフォールバックは制作中のみ許可し、本番公開前に差し替える

## 必須ファイル

- `nanobanana_manifest.json`
- `nanobanana_assets.py`
- `NANOBANANA_WORKFLOW.md`
- `quality_check.py --strict-images`

## 運用フロー

1. 画像要件を manifest に追加する
2. Gemini / Nanobanana2 で画像を生成する
3. 生成画像を `static/images/` 配下へ登録する
4. メタデータ JSON を保存する
5. `quality_check.py --strict-images` を通す
6. その後に build / deploy / push する

## 他サイトへ展開するとき

新しい Web サイトを作るときも、同じ 4 ファイル構成を最初に用意してから制作を始める。
