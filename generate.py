#!/usr/bin/env python3
"""
Premium static site generator for the SIM affiliate site.

Focus:
- stronger visual presentation
- safer ad/comparison wording
- reusable editorial layouts
- affiliate-friendly but compliance-conscious CTA blocks
"""

from __future__ import annotations

import datetime
import html
import json
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "plans_data.json"
OUTPUT_DIR = BASE_DIR / "output"

SITE_NAME = "格安SIMラボ"
SITE_DESCRIPTION = "料金、回線、サポート条件を整理して、自分に合う格安SIMを比較しやすくするメディア"

HERO_IMAGE = "static/images/hero-sim-network.svg"
BUDGET_IMAGE = "static/images/category-budget.svg"
SUPPORT_IMAGE = "static/images/category-support.svg"


def load_data() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def get_plan(data: dict, plan_id: str) -> dict | None:
    for plan in data["sim_plans"]:
        if plan["id"] == plan_id:
            return plan
    return None


def sanitize_claims(text: str) -> str:
    replacements = {
        "業界最安級": "低価格帯",
        "業界最安クラス": "低価格帯",
        "業界最安": "低価格帯",
        "格安SIM最安級": "低価格帯",
        "日本最安": "低価格水準",
        "最安級": "低価格帯",
        "コスパ最強を求める人": "料金と機能のバランスを重視する人",
        "コスパ最強": "料金と機能のバランスを重視する",
        "圧倒的に安い": "料金を抑えやすい",
        "完全無料": "追加通話料を抑えやすい",
        "通話完全無料": "専用アプリ利用時に追加通話料を抑えやすい",
        "ベスト": "相性のよい",
        "本当におすすめできる": "比較検討しやすい",
    }

    result = str(text)
    for src, dst in replacements.items():
        result = result.replace(src, dst)
    return result


def esc(value: str | int | float) -> str:
    return html.escape(sanitize_claims(str(value)), quote=True)


def yen(value: int | float) -> str:
    if value == 0:
        return "0円"
    return f"{value:,}円"


def cta_url(plan: dict) -> str:
    url = str(plan.get("affiliate_url", "")).strip()
    if not url or url.startswith("#"):
        return str(plan.get("official_url", "#")).strip()
    return url


def feature_list(plan: dict, limit: int | None = None) -> list[str]:
    features = [sanitize_claims(item) for item in plan.get("features", [])]
    return features[:limit] if limit else features


def caution_list(plan: dict) -> list[str]:
    return [sanitize_claims(item) for item in plan.get("cons", [])]


def best_for(plan: dict) -> str:
    return sanitize_claims(plan.get("best_for", ""))


def compare_href(data: dict, left_id: str, right_id: str) -> str:
    if [left_id, right_id] in data["compare_pairs"]:
        return f"compare_{left_id}_vs_{right_id}.html"
    if [right_id, left_id] in data["compare_pairs"]:
        return f"compare_{right_id}_vs_{left_id}.html"
    return f"compare_{left_id}_vs_{right_id}.html"


def has_store_support(plan: dict) -> bool:
    text = " ".join(plan.get("features", []))
    return any(word in text for word in ("ショップ", "店頭", "対面"))


def has_rollover(plan: dict) -> bool:
    return not any("繰り越し不可" in item for item in plan.get("cons", []))


def plan_capacity_label(plan: dict) -> str:
    if plan["data_gb"] == 0:
        return "トッピング制"
    if plan["data_gb_large"] == -1:
        return f"{plan['data_gb']}GB / 無制限系プランあり"
    if plan["data_gb_large"] > plan["data_gb"]:
        return f"{plan['data_gb']}GB / {plan['data_gb_large']}GB"
    return f"{plan['data_gb']}GB"


def page_head(title: str, description: str, root: str = "../") -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} | {SITE_NAME}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="stylesheet" href="{root}static/style.css">
</head>
<body>
  <div class="site-shell">
    <header class="site-header">
      <div class="container nav-row">
        <a href="{root}index.html" class="site-logo">{SITE_NAME}</a>
        <nav class="site-nav">
          <a href="{root}index.html">トップ</a>
          <a href="{root}output/ranking_overall.html">総合ランキング</a>
          <a href="{root}output/hikaku_table.html">比較表</a>
          <a href="{root}output/guide_kakuyasu.html">選び方ガイド</a>
        </nav>
      </div>
    </header>
    <div class="pr-disclosure">
      <div class="container">
        <strong>広告について</strong>
        当サイトにはアフィリエイト広告が含まれます。申込条件、料金、キャンペーンの適用有無は必ず公式サイトでご確認ください。
      </div>
    </div>
    <main class="page-main">
      <div class="container">
"""


def page_foot() -> str:
    year = datetime.date.today().year
    return f"""
      </div>
    </main>
    <footer class="site-footer">
      <div class="container footer-grid">
        <div>
          <p class="footer-title">{SITE_NAME}</p>
          <p>{SITE_DESCRIPTION}</p>
        </div>
        <div>
          <p>当サイトの記載内容は公開情報をもとにした編集部整理です。</p>
          <p>最新の料金、キャンペーン、注意事項は各公式サイトをご確認ください。</p>
        </div>
      </div>
      <div class="container footer-copy">© {year} {SITE_NAME}</div>
    </footer>
  </div>
</body>
</html>
"""


def methodology_section() -> str:
    return """
    <section class="methodology-card">
      <div class="eyebrow">Editorial Policy</div>
      <h2>比較の前提を先に確認する</h2>
      <p>
        当サイトでは、月額料金、回線の種類、店頭サポート、eSIM対応、データ容量の見やすさを中心に整理しています。
        特定サービスが常に優れていることを保証するものではなく、用途との相性を見つけやすくするための比較ガイドです。
      </p>
      <ul class="bullet-list">
        <li>料金は代表的な公開プランを基準に整理</li>
        <li>キャンペーン価格や限定特典は必ず公式ページで再確認</li>
        <li>通信品質やサポートは回線種別と提供形態の特徴を中心に記載</li>
      </ul>
    </section>
    """


def cta_button(plan: dict, label: str | None = None) -> str:
    if label is None:
        label = f"{plan['carrier']}の公式情報を見る"
    return f"""
    <a class="cta-button" href="{html.escape(cta_url(plan), quote=True)}" rel="nofollow sponsored noopener" target="_blank">
      <span>{esc(label)}</span>
      <small>広告リンクを含みます</small>
    </a>
    """


def hero_summary_card(plan: dict) -> str:
    return f"""
    <article class="summary-card">
      <span class="summary-card-mark">{html.escape(plan['logo_emoji'])}</span>
      <div>
        <strong>{esc(plan['carrier'])}</strong>
        <p>{esc(yen(plan['monthly_price']))} / 月・{esc(plan_capacity_label(plan))}</p>
      </div>
    </article>
    """


def plan_card(plan: dict, compact: bool = False, detail_root: str = "") -> str:
    features = feature_list(plan, 3 if compact else 4)
    feature_html = "".join(f"<li>{esc(item)}</li>" for item in features)
    badges = [
        f"月額 {yen(plan['monthly_price'])}",
        f"回線 {sanitize_claims(plan['parent'])}",
        "店頭あり" if has_store_support(plan) else "オンライン中心",
    ]
    badge_html = "".join(f"<span>{esc(item)}</span>" for item in badges)
    return f"""
    <article class="plan-card{' compact' if compact else ''}">
      <div class="plan-card-top">
        <div class="plan-card-brand">
          <span class="carrier-mark">{html.escape(plan['logo_emoji'])}</span>
          <div>
            <h3>{esc(plan['carrier'])}</h3>
            <p class="carrier-meta">{esc(plan['network'])}</p>
          </div>
        </div>
        <div class="price-box">
          <strong>{esc(yen(plan['monthly_price']))}</strong>
          <span>{esc(plan_capacity_label(plan))}</span>
        </div>
      </div>
      <div class="plan-badges">{badge_html}</div>
      <p class="plan-audience">向いている人: {esc(best_for(plan))}</p>
      <ul class="feature-list">{feature_html}</ul>
      <div class="plan-card-actions">
        <a class="text-link" href="{html.escape(detail_root, quote=True)}review_{html.escape(plan['id'])}.html">詳細レビュー</a>
        {cta_button(plan)}
      </div>
    </article>
    """


def generate_index(data: dict) -> str:
    top_ids = data["ranking_articles"][0]["ranking_order"][:3]
    top_plans = [get_plan(data, plan_id) for plan_id in top_ids]
    top_plans = [plan for plan in top_plans if plan]
    ranking_cards = "".join(
        f"""
        <a class="category-link" href="output/ranking_{html.escape(item['id'])}.html">
          <span class="category-label">{esc(item['target_keyword'])}</span>
          <strong>{esc(item['title'])}</strong>
          <small>{esc(item['description'])}</small>
        </a>
        """
        for item in data["ranking_articles"]
    )
    review_links = "".join(
        f"<li><a href=\"output/review_{html.escape(plan['id'])}.html\">{esc(plan['carrier'])}のレビューを見る</a></li>"
        for plan in data["sim_plans"]
    )
    summary_cards = "".join(hero_summary_card(plan) for plan in top_plans)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{SITE_NAME} | 自分に合う格安SIMを比較しやすくするメディア</title>
  <meta name="description" content="{esc(SITE_DESCRIPTION)}">
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <div class="site-shell">
    <header class="site-header">
      <div class="container nav-row">
        <a href="index.html" class="site-logo">{SITE_NAME}</a>
        <nav class="site-nav">
          <a href="output/ranking_overall.html">総合ランキング</a>
          <a href="output/hikaku_table.html">比較表</a>
          <a href="output/guide_kakuyasu.html">選び方ガイド</a>
        </nav>
      </div>
    </header>
    <div class="pr-disclosure">
      <div class="container">
        <strong>広告について</strong>
        当サイトにはアフィリエイト広告が含まれます。リンク先の申込条件や価格情報は必ず公式サイトでご確認ください。
      </div>
    </div>
    <main class="page-main">
      <div class="container">
        <section class="hero-home hero-image-layout">
          <div class="hero-copy">
            <div class="eyebrow">SIM Comparison Media</div>
            <h1>通信費を下げたい人へ。<br>比較の軸から、きれいに選べる。</h1>
            <p>
              格安SIM選びで迷いやすい「料金」「回線」「店頭サポート」「eSIM対応」を整理して、
              自分に合うサービスを探しやすくした比較メディアです。
            </p>
            <div class="hero-chips">
              <span>比較対象 {len(data['sim_plans'])}サービス</span>
              <span>ランキング {len(data['ranking_articles'])}カテゴリ</span>
              <span>広告リンクを含みます</span>
            </div>
            <div class="hero-actions">
              <a class="primary-link" href="output/ranking_overall.html">総合ランキングを見る</a>
              <a class="secondary-link" href="output/hikaku_table.html">比較表を見る</a>
            </div>
            <div class="hero-summary-grid">{summary_cards}</div>
          </div>
          <div class="hero-visual hero-visual-stack">
            <div class="visual-image-card">
              <img src="{HERO_IMAGE}" alt="格安SIM比較サイトのヒーロービジュアル">
            </div>
            <div class="visual-mini-grid">
              <article class="visual-mini-card">
                <img src="{BUDGET_IMAGE}" alt="料金比較のイメージ">
                <div>
                  <strong>料金の見やすさ</strong>
                  <p>価格帯と容量を一目で比較</p>
                </div>
              </article>
              <article class="visual-mini-card">
                <img src="{SUPPORT_IMAGE}" alt="サポート比較のイメージ">
                <div>
                  <strong>サポート条件</strong>
                  <p>店頭対応や契約導線も確認</p>
                </div>
              </article>
            </div>
          </div>
        </section>

        <section class="section-block">
          <div class="section-head">
            <div>
              <div class="eyebrow">Decision Entry</div>
              <h2>目的から入る</h2>
            </div>
          </div>
          <div class="category-grid">{ranking_cards}</div>
        </section>

        <section class="section-block feature-band">
          <article class="feature-band-card">
            <div class="eyebrow">Top Picks</div>
            <h2>注目の3サービス</h2>
            <div class="card-grid">
              {''.join(plan_card(plan, compact=True, detail_root='output/') for plan in top_plans)}
            </div>
          </article>
        </section>

        <section class="section-block editorial-grid">
          <article class="content-card">
            <div class="eyebrow">What We Compare</div>
            <h2>見る軸を絞るだけで、選びやすくなる</h2>
            <ul class="bullet-list">
              <li>月額料金と初期費用</li>
              <li>回線の種類と使い方の相性</li>
              <li>店頭サポートの有無</li>
              <li>eSIM対応と開通しやすさ</li>
            </ul>
          </article>
          <article class="content-card dark-card">
            <div class="eyebrow">Design Note</div>
            <h2>Nanobanana2画像を差し込みやすい構造</h2>
            <p>
              ヒーロー、カテゴリカード、レビュー導線の画像枠を分離しているので、
              後から高品質ビジュアルを差し込んでも全体のデザインが崩れにくい構成です。
            </p>
          </article>
        </section>

        {methodology_section()}

        <section class="section-block">
          <div class="section-head">
            <div>
              <div class="eyebrow">All Reviews</div>
              <h2>個別レビュー一覧</h2>
            </div>
          </div>
          <article class="content-card">
            <ul class="link-list">{review_links}</ul>
          </article>
        </section>
      </div>
    </main>
    <footer class="site-footer">
      <div class="container footer-grid">
        <div>
          <p class="footer-title">{SITE_NAME}</p>
          <p>{SITE_DESCRIPTION}</p>
        </div>
        <div>
          <p>各サービスの料金、キャンペーン、注意事項は変更される場合があります。</p>
          <p>申込前に必ず公式サイトの最新情報をご確認ください。</p>
        </div>
      </div>
      <div class="container footer-copy">© {datetime.date.today().year} {SITE_NAME}</div>
    </footer>
  </div>
</body>
</html>
"""


def generate_review(plan: dict, data: dict) -> str:
    title = f"{plan['carrier']}の特徴と注意点"
    description = f"{plan['carrier']}の料金、回線、サポート条件、注意点を整理したレビューです。"
    related_links = []
    for pair in data["compare_pairs"]:
        if plan["id"] in pair:
            other_id = pair[0] if pair[1] == plan["id"] else pair[1]
            other = get_plan(data, other_id)
            if other:
                related_links.append(
                    f"<li><a href=\"{compare_href(data, plan['id'], other_id)}\">{esc(plan['carrier'])}と{esc(other['carrier'])}の比較を見る</a></li>"
                )
    return f"""{page_head(title, description)}
    <section class="page-hero article-hero">
      <div class="eyebrow">Review</div>
      <h1>{esc(plan['carrier'])}の特徴と注意点</h1>
      <p>{esc(plan['carrier'])}の料金、回線、サポート条件、向いている使い方を整理しました。</p>
      <div class="hero-chips">
        <span>{esc(yen(plan['monthly_price']))} / 月</span>
        <span>{esc(plan_capacity_label(plan))}</span>
        <span>{esc(plan['network'])}</span>
      </div>
    </section>

    <section class="content-grid two-col">
      <article class="content-card">
        <h2>基本情報</h2>
        <table class="compare-table">
          <tr><th>サービス名</th><td>{esc(plan['carrier'])}</td></tr>
          <tr><th>月額料金</th><td>{esc(yen(plan['monthly_price']))}</td></tr>
          <tr><th>データ容量</th><td>{esc(plan_capacity_label(plan))}</td></tr>
          <tr><th>回線</th><td>{esc(plan['network'])}</td></tr>
          <tr><th>初期費用</th><td>{esc(yen(plan['initial_cost']))}</td></tr>
          <tr><th>店頭サポート</th><td>{'あり' if has_store_support(plan) else '限定的'}</td></tr>
          <tr><th>eSIM</th><td>{'対応' if plan['esim'] else '非対応'}</td></tr>
        </table>
      </article>
      <article class="content-card accent-card">
        <div class="eyebrow">Audience</div>
        <h2>向いている人</h2>
        <p class="lead-copy">{esc(best_for(plan))}</p>
        {cta_button(plan, f"{plan['carrier']}の申込条件を見る")}
      </article>
    </section>

    <section class="content-grid two-col">
      <article class="content-card">
        <h2>主なポイント</h2>
        <ul class="bullet-list">
          {''.join(f'<li>{esc(item)}</li>' for item in feature_list(plan))}
        </ul>
      </article>
      <article class="content-card caution">
        <h2>事前に確認したい点</h2>
        <ul class="bullet-list">
          {''.join(f'<li>{esc(item)}</li>' for item in caution_list(plan))}
        </ul>
      </article>
    </section>

    <section class="content-card">
      <div class="eyebrow">Related</div>
      <h2>比較ページ</h2>
      <ul class="link-list">{''.join(related_links) if related_links else '<li>関連比較ページは準備中です。</li>'}</ul>
    </section>
{page_foot()}"""


def generate_comparison(plan_a: dict, plan_b: dict) -> str:
    title = f"{plan_a['carrier']}と{plan_b['carrier']}の比較"
    description = f"{plan_a['carrier']}と{plan_b['carrier']}の料金、容量、サポート条件を比較しています。"
    return f"""{page_head(title, description)}
    <section class="page-hero article-hero">
      <div class="eyebrow">Comparison</div>
      <h1>{esc(plan_a['carrier'])}と{esc(plan_b['carrier'])}を比較</h1>
      <p>料金、データ容量、店頭サポート、eSIM対応を同じ軸で見比べられるように整理しています。</p>
    </section>

    <section class="content-card">
      <table class="compare-table">
        <tr><th>比較項目</th><th>{esc(plan_a['carrier'])}</th><th>{esc(plan_b['carrier'])}</th></tr>
        <tr><td>月額料金</td><td>{esc(yen(plan_a['monthly_price']))}</td><td>{esc(yen(plan_b['monthly_price']))}</td></tr>
        <tr><td>データ容量</td><td>{esc(plan_capacity_label(plan_a))}</td><td>{esc(plan_capacity_label(plan_b))}</td></tr>
        <tr><td>回線</td><td>{esc(plan_a['network'])}</td><td>{esc(plan_b['network'])}</td></tr>
        <tr><td>初期費用</td><td>{esc(yen(plan_a['initial_cost']))}</td><td>{esc(yen(plan_b['initial_cost']))}</td></tr>
        <tr><td>eSIM</td><td>{'対応' if plan_a['esim'] else '非対応'}</td><td>{'対応' if plan_b['esim'] else '非対応'}</td></tr>
        <tr><td>店頭サポート</td><td>{'あり' if has_store_support(plan_a) else '限定的'}</td><td>{'あり' if has_store_support(plan_b) else '限定的'}</td></tr>
        <tr><td>繰り越し</td><td>{'あり' if has_rollover(plan_a) else 'なし'}</td><td>{'あり' if has_rollover(plan_b) else 'なし'}</td></tr>
      </table>
    </section>

    <section class="content-grid two-col">
      <article class="content-card">
        <div class="eyebrow">Plan A</div>
        <h2>{esc(plan_a['carrier'])}が向く人</h2>
        <p class="lead-copy">{esc(best_for(plan_a))}</p>
        <ul class="bullet-list">{''.join(f'<li>{esc(item)}</li>' for item in feature_list(plan_a, 3))}</ul>
        {cta_button(plan_a, f"{plan_a['carrier']}の詳細を見る")}
      </article>
      <article class="content-card">
        <div class="eyebrow">Plan B</div>
        <h2>{esc(plan_b['carrier'])}が向く人</h2>
        <p class="lead-copy">{esc(best_for(plan_b))}</p>
        <ul class="bullet-list">{''.join(f'<li>{esc(item)}</li>' for item in feature_list(plan_b, 3))}</ul>
        {cta_button(plan_b, f"{plan_b['carrier']}の詳細を見る")}
      </article>
    </section>
{page_foot()}"""


def generate_ranking(ranking_def: dict, data: dict) -> str:
    title = ranking_def["title"]
    description = sanitize_claims(ranking_def["description"])
    cards = []
    for index, plan_id in enumerate(ranking_def["ranking_order"], start=1):
        plan = get_plan(data, plan_id)
        if not plan:
            continue
        cards.append(f"""
        <article class="rank-card">
          <div class="rank-number">#{index}</div>
          {plan_card(plan, compact=True)}
        </article>
        """)
    return f"""{page_head(title, description)}
    <section class="page-hero article-hero">
      <div class="eyebrow">Ranking</div>
      <h1>{esc(title)}</h1>
      <p>{esc(description)}</p>
    </section>
    {methodology_section()}
    <section class="card-grid">{''.join(cards)}</section>
{page_foot()}"""


def generate_guide() -> str:
    title = "格安SIMの選び方ガイド"
    description = "はじめて乗り換える人向けに、料金、回線、サポート条件の見方を整理しています。"
    return f"""{page_head(title, description)}
    <section class="page-hero article-hero">
      <div class="eyebrow">Guide</div>
      <h1>格安SIMの選び方ガイド</h1>
      <p>料金だけでなく、回線、店頭サポート、eSIM対応まで見て選ぶと失敗しにくくなります。</p>
    </section>

    <section class="content-grid two-col">
      <article class="content-card">
        <h2>先に見るべき3項目</h2>
        <ul class="bullet-list">
          <li>毎月どのくらいのデータ容量が必要か</li>
          <li>店頭サポートが必要か、オンラインで完結できるか</li>
          <li>今の回線品質と比較してどこまで許容できるか</li>
        </ul>
      </article>
      <article class="content-card accent-card">
        <h2>見落としやすいポイント</h2>
        <ul class="bullet-list">
          <li>初期費用や通話オプション込みの総額</li>
          <li>キャンペーンの適用条件</li>
          <li>繰り越しやeSIM対応の有無</li>
        </ul>
      </article>
    </section>

    {methodology_section()}
{page_foot()}"""


def generate_comparison_table(data: dict) -> str:
    title = f"格安SIM全{len(data['sim_plans'])}社の比較表"
    description = "主要サービスの料金、容量、回線、店頭サポート、eSIM対応を一覧で見比べられます。"
    rows = []
    for plan in data["sim_plans"]:
        rows.append(f"""
        <tr>
          <td>{esc(plan['carrier'])}</td>
          <td>{esc(yen(plan['monthly_price']))}</td>
          <td>{esc(plan_capacity_label(plan))}</td>
          <td>{esc(plan['network'])}</td>
          <td>{'対応' if plan['esim'] else '非対応'}</td>
          <td>{'あり' if has_rollover(plan) else 'なし'}</td>
          <td>{'あり' if has_store_support(plan) else '限定的'}</td>
          <td><a href="review_{html.escape(plan['id'])}.html">詳細</a></td>
        </tr>
        """)
    return f"""{page_head(title, description)}
    <section class="page-hero article-hero">
      <div class="eyebrow">Comparison Table</div>
      <h1>{esc(title)}</h1>
      <p>{esc(description)}</p>
    </section>

    <section class="content-card">
      <div class="table-wrap">
        <table class="compare-table">
          <tr>
            <th>サービス</th>
            <th>月額料金</th>
            <th>基本容量</th>
            <th>回線</th>
            <th>eSIM</th>
            <th>繰り越し</th>
            <th>店頭サポート</th>
            <th>詳細</th>
          </tr>
          {''.join(rows)}
        </table>
      </div>
    </section>
{page_foot()}"""


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    data = load_data()
    OUTPUT_DIR.mkdir(exist_ok=True)

    for plan in data["sim_plans"]:
        write_text(OUTPUT_DIR / f"review_{plan['id']}.html", generate_review(plan, data))

    for left, right in data["compare_pairs"]:
        plan_a = get_plan(data, left)
        plan_b = get_plan(data, right)
        if plan_a and plan_b:
            write_text(OUTPUT_DIR / f"compare_{left}_vs_{right}.html", generate_comparison(plan_a, plan_b))

    for ranking in data["ranking_articles"]:
        write_text(OUTPUT_DIR / f"ranking_{ranking['id']}.html", generate_ranking(ranking, data))

    write_text(OUTPUT_DIR / "guide_kakuyasu.html", generate_guide())
    write_text(OUTPUT_DIR / "hikaku_table.html", generate_comparison_table(data))
    write_text(BASE_DIR / "index.html", generate_index(data))

    print(f"Generated site at: {BASE_DIR}")


if __name__ == "__main__":
    main()
