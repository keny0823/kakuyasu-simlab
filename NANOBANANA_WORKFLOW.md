# Nanobanana2 Image Workflow

このサイトでは、今後の画像追加を `Nanobanana2` 前提で管理します。

## 方針

- 画像プロンプトは [nanobanana_manifest.json](/c:/Users/since/Blue%20Ocean/sim-affiliate/nanobanana_manifest.json) に集約する
- 実画像は `png` などのラスター画像として保存する
- 画像を登録したら、同名の `.json` メタデータを保存する
- 公開前に `verify` を通して、必要画像の有無を確認する

## 使い方

1. プロンプトを書き出す

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py write-prompts
```

2. Gemini を開いて対象アセットのプロンプトを自動挿入する

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py open-gemini hero_main
```

3. Gemini 側で画像生成し、ダウンロードした画像を登録する

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py register hero_main "C:\path\to\downloaded-image.png"
```

4. 画像の登録状態を確認する

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py verify
```

## 対象アセット

- `hero_main`
- `budget_card`
- `support_card`
- `checklist_card`

## 注意

- 現時点では Gemini / Nanobanana2 の生成そのものは、ログイン済みブラウザセッションに依存します
- このスクリプトは「Gemini を開く」「プロンプトを入れる」「保存先を管理する」部分を標準化するためのものです
- 将来的に API 経路が使えるようになったら、このフローを完全自動化に置き換えます
