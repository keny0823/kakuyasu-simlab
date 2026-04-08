# Nanobanana2 Image Workflow

このサイトでは、今後の画像追加を `Nanobanana2` 前提で管理します。

## 方針

- 画像プロンプトは [nanobanana_manifest.json](/c:/Users/since/Blue%20Ocean/sim-affiliate/nanobanana_manifest.json) に集約する
- 実画像は `png` などのラスター画像として保存する
- 画像を登録したら、同名の `.json` メタデータを保存する
- 公開前に `verify` を通して、必要画像の有無を確認する

## 使い方

最短ルートはこれです。

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py run hero_main
```

これで次の流れを1コマンドで実行します。

- 対象アセットのプロンプト確認
- ログイン済みブラウザプロフィールで Gemini を起動
- プロンプト自動入力
- 生成ボタンを自動で押せる場合は自動押下
- ダウンロードボタンを自動で押せる場合は自動押下
- `Downloads` フォルダを監視
- 新しくダウンロードされた画像を自動で `target_path` に登録
- 同名 `.json` メタデータも自動保存

理想系では Gemini 側の手作業なしで進みますが、UI差分がある場合だけ手動で生成またはダウンロードしてください。

## 個別コマンド

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

## 補助コマンド

アセット一覧を確認する

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py list-assets
```

アセット定義を確認する

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py show hero_main
```

`Downloads` 以外を監視したい場合

```powershell
.venv\Scripts\python.exe sim-affiliate\nanobanana_assets.py run hero_main --downloads-dir "C:\Users\since\Downloads"
```

## 対象アセット

- `hero_main`
- `budget_card`
- `support_card`
- `checklist_card`

## 注意

- 現時点では Gemini / Nanobanana2 の生成そのものは、ログイン済みブラウザセッションに依存します
- `run` は Gemini UI のテキスト差分に対応するため、生成・ダウンロードボタンを複数セレクタで自動探索します
- UI差分で完全自動化できない場合でも、ダウンロード監視と登録までは継続します
- 実行時スクリーンショットは `sim-affiliate/nanobanana_logs/` に保存されます
- このスクリプトは「Gemini を開く」「プロンプトを入れる」「生成/ダウンロードを試行する」「ダウンロードを検知する」「保存先を管理する」部分を標準化するためのものです
- 将来的に API 経路が使えるようになったら、このフローを完全自動化に置き換えます
