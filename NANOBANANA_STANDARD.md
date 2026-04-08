# Nanobanana2 Website Image Standard

## ウェブサイトデザイン部の役割

この基準は、今後の「ウェブサイトデザイン部」の標準ルールとして扱う。

- サイト設計時は、レイアウト・導線・コピー・画像を分離して設計する
- ビジュアルが必要な箇所は `Nanobanana2` と協力して高品質画像を用意する
- 画像は飾りではなく、「何を比較するサイトか」「誰向けか」が一目で伝わる内容にする
- 生成画像を入れる前提で、カード・ヒーロー・特集枠も最初から差し替えやすく組む
- 公開前に `quality_check.py --strict-images` を通し、仮画像のまま出さない

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

## デザイン品質の原則

- 英語ラベルや抽象的すぎるビジュアルを安易に置かない
- 第一印象で「何のサイトか」「何が比較できるか」が分かる構成にする
- 画像は UI 風の意味ある絵、もしくは実写寄りの訴求画像にする
- 文字だけで押し切らず、視線誘導と理解補助のために画像を使う
- チープな仮 SVG を長く残さず、早い段階で Nanobanana2 画像へ置き換える
