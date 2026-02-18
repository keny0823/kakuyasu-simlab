#!/usr/bin/env python3
"""
格安SIM・ネット回線 自動記事生成エンジン
Usage: python generate.py
"""

import json
import os
import datetime
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "plans_data.json"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = BASE_DIR / "static"

# --- Load Data ---
def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_plan(data, plan_id):
    for p in data['sim_plans']:
        if p['id'] == plan_id:
            return p
    return None

# --- HTML Building Blocks ---
def html_header(title, description, canonical_path=""):
    today = datetime.date.today().strftime("%Y年%m月%d日")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | 格安SIMラボ</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="../static/style.css">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a href="../index.html" class="site-logo">🔬 格安SIM<span>ラボ</span></a>
      <nav class="site-nav">
        <a href="../index.html">トップ</a>
        <a href="../output/ranking_overall.html">おすすめランキング</a>
      </nav>
    </div>
  </header>
  <main class="main-content">
    <div class="container">
      <div class="article-header">
        <span class="article-category">格安SIM比較</span>
        <h1>{title}</h1>
        <p class="article-meta">最終更新: <time>{today}</time></p>
      </div>
      <div class="article-body">
"""

def html_footer(related_links=None):
    related = ""
    if related_links:
        related = '<div class="related-articles"><h3>📚 関連記事</h3><ul>'
        for text, href in related_links:
            related += f'<li><a href="{href}">👉 {text}</a></li>'
        related += '</ul></div>'

    return f"""
        {related}
      </div>
    </div>
  </main>
  <footer class="site-footer">
    <div class="container">
      <p>&copy; {datetime.date.today().year} 格安SIMラボ - 格安SIM比較サイト</p>
      <p class="disclaimer">※ 当サイトはアフィリエイトプログラムに参加しています。記事内のリンクから申し込みが行われた場合、当サイトに報酬が支払われることがあります。<br>※ 掲載情報は記事執筆時点のものです。最新情報は各公式サイトでご確認ください。</p>
    </div>
  </footer>
</body>
</html>"""


# --- Review Article Generator ---
def generate_review(plan, data):
    """Generate a single plan review article."""
    title = f"{plan['carrier']}の評判・メリット・デメリットを徹底解説【{datetime.date.today().year}年最新】"
    desc = f"{plan['carrier']}の料金、速度、メリット・デメリットを詳しく解説。{plan['best_for']}におすすめ。"

    html = html_header(title, desc)

    # Intro
    html += f"""
<p>{plan['carrier']}は{plan['parent']}が提供する格安SIM/モバイル通信サービスです。</p>
<p>本記事では、{plan['carrier']}の<strong>料金プラン・通信速度・メリット・デメリット</strong>を余すことなく解説します。「自分に合っているかどうか」の判断材料にしてください。</p>
"""

    # Price Section
    html += f'<h2>{plan["logo_emoji"]} {plan["carrier"]}の料金プラン</h2>'
    html += f"""
<div class="plan-card">
  <div class="plan-card-header">
    <span style="font-size:2rem">{plan['logo_emoji']}</span>
    <div>
      <h3 style="color:white;border:none;margin:0;padding:0">{plan['carrier']}</h3>
      <span class="parent-label">{plan['parent']}回線</span>
    </div>
  </div>
  <div class="plan-card-body">
    <div class="plan-price">
      <span class="price-label">月額（税込）</span><br>
      <span class="price-value">{plan['monthly_price']:,}</span>
      <span class="price-unit">円/月〜</span><br>
      <span class="price-label">({plan['data_gb']}GB)</span>
    </div>
    <table class="spec-table">
      <tr><th>通信回線</th><td>{plan['network']}</td></tr>
      <tr><th>データ容量</th><td>{plan['data_gb']}GB（大容量: {'無制限' if plan['data_gb_large'] == -1 else str(plan['data_gb_large']) + 'GB'}）</td></tr>
      <tr><th>通話</th><td>{plan['call_included']}</td></tr>
      <tr><th>最低利用期間</th><td>{plan['min_contract']}</td></tr>
      <tr><th>初期費用</th><td>{'無料' if plan['initial_cost'] == 0 else f"{plan['initial_cost']:,}円"}</td></tr>
      <tr><th>eSIM対応</th><td>{'✅ 対応' if plan['esim'] else '❌ 非対応'}</td></tr>
      <tr><th>海外利用</th><td>{'✅ 対応' if plan['overseas'] else '❌ 非対応'}</td></tr>
    </table>
  </div>
</div>
"""

    # Merits
    html += f'<h2>✅ {plan["carrier"]}のメリット</h2>'
    html += '<ul>'
    for feat in plan['features']:
        html += f'<li><strong>{feat.split("（")[0].split("で")[0]}</strong> — {feat}</li>'
    html += '</ul>'

    # Demerits
    html += f'<h2>⚠️ {plan["carrier"]}のデメリット</h2>'
    html += '<ul>'
    for con in plan['cons']:
        html += f'<li>{con}</li>'
    html += '</ul>'

    # Who is this for?
    html += f'<h2>🎯 {plan["carrier"]}はこんな人におすすめ</h2>'
    html += f'<div class="verdict-box"><h3 style="color:var(--primary);border:none">{plan["best_for"]}</h3></div>'

    # CTA
    pixel_html = ""
    if plan.get('affiliate_pixel'):
        pixel_html = f'<img src="{plan["affiliate_pixel"]}" height="1" width="1" border="0" style="position:absolute">'
    html += f"""
<a href="{plan['affiliate_url']}" class="cta-button" rel="nofollow noopener" target="_blank">
  {pixel_html}{plan['carrier']}の公式サイトはこちら
  <span class="sub-text">※ お申し込みは公式サイトから</span>
</a>
"""

    # Related
    related = []
    for pair in data.get('compare_pairs', []):
        if plan['id'] in pair:
            other_id = pair[0] if pair[1] == plan['id'] else pair[1]
            other = get_plan(data, other_id)
            if other:
                related.append((
                    f"{plan['carrier']} vs {other['carrier']} 徹底比較",
                    f"compare_{plan['id']}_vs_{other_id}.html"
                ))
    related.append(("格安SIM おすすめランキング", "ranking_overall.html"))

    html += html_footer(related)
    return html


# --- Comparison Article Generator ---
def generate_comparison(plan_a, plan_b, data):
    """Generate a comparison article between two plans."""
    title = f"{plan_a['carrier']} vs {plan_b['carrier']}を徹底比較！どっちがおすすめ？【{datetime.date.today().year}年】"
    desc = f"{plan_a['carrier']}と{plan_b['carrier']}の料金・速度・特徴を比較。あなたに合うのはどっち？"

    html = html_header(title, desc)

    html += f"""
<p>格安SIM選びで迷う人が多い「<strong>{plan_a['carrier']}</strong>」と「<strong>{plan_b['carrier']}</strong>」。</p>
<p>どちらも人気のサービスですが、実はターゲットが大きく異なります。本記事では<strong>料金・データ容量・通話・サポート</strong>を一つずつ比較し、「あなたはどっちを選ぶべきか」を結論づけます。</p>
"""

    # Compare Table
    html += '<h2>📊 スペック比較表</h2>'
    
    def price_compare(a, b):
        if a < b: return f'<span class="winner">{a:,}円 ✅</span>', f'{b:,}円'
        elif b < a: return f'{a:,}円', f'<span class="winner">{b:,}円 ✅</span>'
        return f'{a:,}円', f'{b:,}円'
    
    pa, pb = price_compare(plan_a['monthly_price'], plan_b['monthly_price'])

    html += f"""
<table class="compare-table">
  <tr><th>比較項目</th><th>{plan_a['carrier']}</th><th>{plan_b['carrier']}</th></tr>
  <tr><td>月額料金</td><td>{pa}</td><td>{pb}</td></tr>
  <tr><td>データ容量</td><td>{plan_a['data_gb']}GB</td><td>{plan_b['data_gb']}GB</td></tr>
  <tr><td>通信回線</td><td>{plan_a['parent']}回線</td><td>{plan_b['parent']}回線</td></tr>
  <tr><td>通話</td><td>{plan_a['call_included']}</td><td>{plan_b['call_included']}</td></tr>
  <tr><td>eSIM</td><td>{'✅' if plan_a['esim'] else '❌'}</td><td>{'✅' if plan_b['esim'] else '❌'}</td></tr>
  <tr><td>海外利用</td><td>{'✅' if plan_a['overseas'] else '❌'}</td><td>{'✅' if plan_b['overseas'] else '❌'}</td></tr>
  <tr><td>初期費用</td><td>{'無料' if plan_a['initial_cost'] == 0 else f"{plan_a['initial_cost']:,}円"}</td><td>{'無料' if plan_b['initial_cost'] == 0 else f"{plan_b['initial_cost']:,}円"}</td></tr>
</table>
"""

    # Analysis
    html += '<h2>🔍 各項目を詳しく比較</h2>'
    
    # Price
    html += '<h3>💰 料金の比較</h3>'
    if plan_a['monthly_price'] < plan_b['monthly_price']:
        diff = plan_b['monthly_price'] - plan_a['monthly_price']
        html += f'<p>月額料金は<strong>{plan_a["carrier"]}が{diff:,}円安い</strong>です。年間で{diff * 12:,}円の差になります。安さ重視なら{plan_a["carrier"]}が有利です。</p>'
    elif plan_b['monthly_price'] < plan_a['monthly_price']:
        diff = plan_a['monthly_price'] - plan_b['monthly_price']
        html += f'<p>月額料金は<strong>{plan_b["carrier"]}が{diff:,}円安い</strong>です。年間で{diff * 12:,}円の差になります。安さ重視なら{plan_b["carrier"]}が有利です。</p>'
    else:
        html += f'<p>月額料金は<strong>同額</strong>です。料金以外の要素で選びましょう。</p>'

    # Data
    html += '<h3>📶 データ容量の比較</h3>'
    if plan_a['data_gb'] > plan_b['data_gb']:
        html += f'<p>基本プランのデータ容量は{plan_a["carrier"]}（{plan_a["data_gb"]}GB）が{plan_b["carrier"]}（{plan_b["data_gb"]}GB）より多いです。</p>'
    elif plan_b['data_gb'] > plan_a['data_gb']:
        html += f'<p>基本プランのデータ容量は{plan_b["carrier"]}（{plan_b["data_gb"]}GB）が{plan_a["carrier"]}（{plan_a["data_gb"]}GB）より多いです。</p>'

    # Verdict
    html += '<h2>🏆 結論：どっちを選ぶべき？</h2>'
    html += f"""
<div class="verdict-box">
  <h3 style="color:var(--primary);border:none">{plan_a['carrier']}がおすすめな人</h3>
  <p>{plan_a['best_for']}</p>
</div>
<div class="verdict-box">
  <h3 style="color:var(--primary);border:none">{plan_b['carrier']}がおすすめな人</h3>
  <p>{plan_b['best_for']}</p>
</div>
"""

    # CTAs
    html += f"""
<a href="{plan_a['affiliate_url']}" class="cta-button" rel="nofollow noopener" target="_blank">
  {plan_a['carrier']}の公式サイトはこちら
</a>
<a href="{plan_b['affiliate_url']}" class="cta-button" rel="nofollow noopener" target="_blank">
  {plan_b['carrier']}の公式サイトはこちら
</a>
"""
    
    related = [
        (f"{plan_a['carrier']}の詳細レビュー", f"review_{plan_a['id']}.html"),
        (f"{plan_b['carrier']}の詳細レビュー", f"review_{plan_b['id']}.html"),
        ("格安SIM おすすめランキング", "ranking_overall.html"),
    ]

    html += html_footer(related)
    return html


# --- Ranking Article Generator ---
def generate_ranking(ranking_def, data):
    """Generate a ranking article."""
    title = f"{ranking_def['title']}【{datetime.date.today().year}年最新版】"
    desc = ranking_def['description']

    html = html_header(title, desc)

    html += f"""
<p>{ranking_def['description']}</p>
<p>本ランキングは<strong>料金・通信品質・サポート・独自機能</strong>を総合的に評価し、本当におすすめできる格安SIMだけを厳選しました。</p>
"""

    html += '<h2>🏆 ランキング</h2>'

    for i, plan_id in enumerate(ranking_def['ranking_order']):
        plan = get_plan(data, plan_id)
        if not plan:
            continue
        
        rank = i + 1
        rank_label = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}位"
        rank_class = f"rank-{rank}" if rank <= 3 else ""

        html += f"""
<div class="plan-card">
  <div class="plan-card-header {rank_class}">
    <span class="rank-badge">{rank_label}</span>
    <div>
      <h3 style="color:white;border:none;margin:0;padding:0">{plan['carrier']}</h3>
      <span class="parent-label">{plan['parent']}回線</span>
    </div>
  </div>
  <div class="plan-card-body">
    <div class="plan-price">
      <span class="price-label">月額（税込）</span><br>
      <span class="price-value">{plan['monthly_price']:,}</span>
      <span class="price-unit">円/月〜</span>
    </div>
    <div class="feature-tags">"""
        for feat in plan['features'][:3]:
            html += f'<span class="feature-tag">✅ {feat.split("（")[0][:20]}</span>'
        html += """</div>
    <p style="margin-top:12px"><strong>こんな人におすすめ：</strong>""" + plan['best_for'] + """</p>"""
        
        html += f"""
    <a href="{plan['affiliate_url']}" class="cta-button" rel="nofollow noopener" target="_blank">
      {plan['carrier']}を申し込む
      <span class="sub-text">※ 公式サイトへ移動します</span>
    </a>
    <p style="text-align:center"><a href="review_{plan['id']}.html">→ {plan['carrier']}の詳細レビューを読む</a></p>
  </div>
</div>
"""

    html += html_footer()
    return html


# --- Guide Article: 格安SIMとは ---
def generate_guide(data):
    """Generate the beginner guide article explaining what 格安SIM is."""
    year = datetime.date.today().year
    title = f"格安SIMとは？大手キャリアとの違い・メリット・デメリットを初心者向けに解説【{year}年】"
    desc = "格安SIMとは何か？ドコモ・au・ソフトバンクとの違い、メリット・デメリットを初心者にもわかりやすく解説します。"

    html = html_header(title, desc)

    html += """
<p>「<strong>格安SIM</strong>」という言葉を聞いたことはあるけれど、<strong>実際に何が違うのか、本当に安くなるのか</strong>不安な方も多いのではないでしょうか。</p>
<p>この記事では、格安SIMの仕組みから大手キャリア（ドコモ・au・ソフトバンク）との違い、乗り換えるメリット・デメリットまで<strong>初心者向けにわかりやすく</strong>解説します。</p>

<h2>📱 格安SIMとは？</h2>
<p>格安SIMとは、ドコモ・au・ソフトバンクの<strong>大手3キャリアの通信回線を借りて</strong>サービスを提供する通信事業者のことです。正式には<strong>MVNO（仮想移動体通信事業者）</strong>と呼ばれます。</p>
<p>自社で通信設備を持たないため設備投資コストが抑えられ、その分<strong>月額料金が安く</strong>なっています。</p>

<div class="info-box">
<h4>💡 ポイント</h4>
<p>最近では大手キャリア自身も「ahamo」「LINEMO」「povo」などの<strong>オンライン専用格安プラン</strong>を提供しており、これらも広い意味で「格安SIM」に含まれます。大手の回線品質のまま安く使えるのが特徴です。</p>
</div>

<h2>🔄 大手キャリアと格安SIMの違い</h2>
<table class="compare-table">
  <tr><th>比較項目</th><th>大手キャリア<br>（ドコモ/au/SB）</th><th>格安SIM</th></tr>
  <tr><td>月額料金</td><td>5,000〜8,000円</td><td><span class="winner">500〜3,000円 ✅</span></td></tr>
  <tr><td>通信速度</td><td><span class="winner">常に安定 ✅</span></td><td>昼休みに遅くなる場合あり</td></tr>
  <tr><td>店舗サポート</td><td><span class="winner">全国に店舗あり ✅</span></td><td>オンライン中心（一部あり）</td></tr>
  <tr><td>通信エリア</td><td>広い</td><td>同じ（大手の回線を利用）</td></tr>
  <tr><td>初期設定</td><td>店頭でやってくれる</td><td>自分で行う場合が多い</td></tr>
  <tr><td>契約の縛り</td><td>なし（最近は）</td><td>なし</td></tr>
  <tr><td>端末の種類</td><td><span class="winner">最新機種が豊富 ✅</span></td><td>限定的（SIMフリー端末利用）</td></tr>
  <tr><td>年間コスト（目安）</td><td>60,000〜96,000円</td><td><span class="winner">6,000〜36,000円 ✅</span></td></tr>
</table>

<div class="verdict-box">
<h3>💰 乗り換えで年間3〜6万円の節約も！</h3>
<p>例えば、ドコモで月7,000円 → ahamoで月2,970円に変更すると、<strong>年間約48,000円の節約</strong>になります。家族4人なら<strong>約19万円</strong>も浮く計算です。</p>
</div>

<h2>✅ 格安SIMのメリット</h2>
<ul>
  <li><strong>月額料金が圧倒的に安い</strong> — 大手の半額〜1/10の料金で使えるプランも多数</li>
  <li><strong>契約の縛りがない</strong> — ほぼ全社で解約金・最低利用期間なし。気軽に試せる</li>
  <li><strong>使い方に合わせてプランが選べる</strong> — 1GBから無制限まで、豊富なプラン展開</li>
  <li><strong>大手と同じ電波エリア</strong> — ドコモ・au・ソフトバンクの回線を使うので、エリアは同じ</li>
  <li><strong>乗り換えが簡単</strong> — MNP（番号ポータビリティ）でそのまま電話番号を引き継げる</li>
  <li><strong>eSIM対応で即日開通</strong> — 最短数分で開通できるサービスも増えている</li>
</ul>

<h2>⚠️ 格安SIMのデメリット</h2>
<ul>
  <li><strong>昼休み・夕方に速度が低下することがある</strong> — 回線を借りているため、混雑時に遅くなりやすい（ahamoやLINEMOなどキャリア直営は除く）</li>
  <li><strong>店頭サポートが少ない</strong> — 多くはオンライン手続きのみ。対面相談が必要な人には不向きな場合も</li>
  <li><strong>初期設定を自分で行う必要がある</strong> — SIMの差し替えやAPN設定など。ただし最近は簡略化されている</li>
  <li><strong>キャリアメールが使えない</strong> — @docomo.ne.jp 等のメールは基本的に使えなくなる（有料で持ち運び可能）</li>
  <li><strong>最新端末のセット購入が限られる</strong> — 最新のiPhoneなどは自分で別途購入する必要がある場合が多い</li>
</ul>

<h2>🤔 格安SIMに向いている人・向いていない人</h2>
<div class="verdict-box">
<h3>✅ 格安SIMに向いている人</h3>
<p>月額料金を安くしたい ／ オンラインでの手続きに抵抗がない ／ 通信速度にそこまでこだわらない ／ 自分で調べて解決できる</p>
</div>
<div class="verdict-box">
<h3>❌ 格安SIMに向いていない人</h3>
<p>店頭でサポートを受けたい ／ 常に最速の通信速度が必要 ／ 最新端末をセットで買いたい ／ キャリアメールが手放せない</p>
</div>
<p>ただし、<strong>UQモバイル</strong>や<strong>ワイモバイル</strong>は全国のショップで対面サポートを受けられるため、「安くしたいけどサポートも欲しい」という方にもおすすめです。</p>

<h2>📋 格安SIMの選び方 3つのポイント</h2>
<h3>① 月にどれくらいデータを使うか？</h3>
<ul>
  <li><strong>1〜3GB</strong>（SNS・メール中心） → 日本通信SIM、LINEMO ミニプラン</li>
  <li><strong>5〜10GB</strong>（動画もそこそこ） → IIJmio、NUROモバイル</li>
  <li><strong>20GB以上</strong>（動画・テザリング多め） → ahamo、楽天モバイル</li>
  <li><strong>無制限</strong>（ヘビーユーザー） → 楽天モバイル</li>
</ul>
<h3>② 通話はどれくらい使うか？</h3>
<ul>
  <li><strong>ほぼ使わない</strong> → 通話オプション不要のプランを選べばOK</li>
  <li><strong>短い通話が多い</strong> → ahamoなら5分かけ放題が込み</li>
  <li><strong>長電話が多い</strong> → 楽天モバイル（Rakuten Linkで無料）</li>
</ul>
<h3>③ サポートは必要か？</h3>
<ul>
  <li><strong>自分でできる</strong> → オンライン専用（ahamo、LINEMO、povo）が安い</li>
  <li><strong>店頭相談したい</strong> → UQモバイル、ワイモバイル、楽天モバイル</li>
</ul>
"""

    # CTA to ranking
    html += """
<a href="ranking_overall.html" class="cta-button">
  おすすめ格安SIMランキングを見る
  <span class="sub-text">→ あなたにぴったりの格安SIMを探す</span>
</a>
"""

    related = [
        ("格安SIM おすすめランキング", "ranking_overall.html"),
        ("とにかく安い格安SIM ランキング", "ranking_cheapest.html"),
        ("格安SIM 全プラン比較表", "hikaku_table.html"),
    ]

    html += html_footer(related)
    return html


# --- Full Comparison Table Generator ---
def generate_comparison_table(data):
    """Generate a full comparison table of all SIM plans."""
    year = datetime.date.today().year
    plans = data['sim_plans']
    title = f"格安SIM 全{len(plans)}社 比較表【{year}年最新】料金・データ容量・特徴を一覧で比較"
    desc = f"主要格安SIM {len(plans)}社の料金・データ容量・通信速度・特徴を一覧表で比較。ひと目でわかる比較表で最適な格安SIMが見つかります。"

    html = html_header(title, desc)

    html += f"""
<p>「結局どの格安SIMが自分に合っているの？」という方のために、主要<strong>{len(plans)}社の格安SIMを一覧表</strong>で比較しました。</p>
<p>まずは料金やデータ量をざっと見比べて、気になるサービスの詳細レビューへ進んでください。</p>

<h2>📊 格安SIM 比較一覧表</h2>
<div style="overflow-x:auto; margin: 24px 0;">
<table class="compare-table" style="min-width:800px;">
  <tr>
    <th>格安SIM</th>
    <th>月額料金</th>
    <th>データ容量</th>
    <th>回線</th>
    <th>通話</th>
    <th>eSIM</th>
    <th>初期費用</th>
    <th>詳細</th>
  </tr>
"""

    for plan in plans:
        data_text = f"{plan['data_gb']}GB"
        if plan['data_gb_large'] == -1:
            data_text += " 〜 無制限"
        elif plan['data_gb_large'] > 0:
            data_text += f" 〜 {plan['data_gb_large']}GB"

        price_text = f"{plan['monthly_price']:,}円" if plan['monthly_price'] > 0 else "0円〜"
        initial = "無料" if plan['initial_cost'] == 0 else f"{plan['initial_cost']:,}円"
        esim = "✅" if plan['esim'] else "❌"

        html += f"""  <tr>
    <td><strong>{plan['logo_emoji']} {plan['carrier']}</strong><br><span style="font-size:0.75rem;color:var(--text-muted)">{plan['parent']}</span></td>
    <td><strong style="color:var(--accent-blue)">{price_text}</strong></td>
    <td>{data_text}</td>
    <td>{plan['network'].split(' ')[0]}</td>
    <td style="font-size:0.8rem">{plan['call_included'][:15]}...</td>
    <td>{esim}</td>
    <td>{initial}</td>
    <td><a href="review_{plan['id']}.html" style="font-weight:700">詳細→</a></td>
  </tr>
"""

    html += """</table>
</div>
"""

    # Price sort section
    sorted_by_price = sorted(plans, key=lambda p: p['monthly_price'])
    html += """
<h2>💰 月額料金が安い順</h2>
<p>最安プランの月額料金順に並べると、以下のようになります。</p>
"""
    for i, plan in enumerate(sorted_by_price):
        rank = i + 1
        price = f"{plan['monthly_price']:,}円" if plan['monthly_price'] > 0 else "0円〜"
        html += f"""
<div class="plan-card" style="margin:12px 0">
  <div class="plan-card-body" style="padding:16px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
    <div style="display:flex;align-items:center;gap:12px">
      <span style="font-size:1.3rem;font-weight:900;color:var(--text-muted);min-width:36px">{rank}位</span>
      <div>
        <strong style="font-size:1.1rem">{plan['logo_emoji']} {plan['carrier']}</strong>
        <span style="color:var(--text-muted);font-size:0.85rem;margin-left:8px">{plan['parent']}</span>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:16px">
      <span style="font-size:1.4rem;font-weight:900;color:var(--accent-blue)">{price}</span>
      <span style="color:var(--text-muted);font-size:0.85rem">/ {plan['data_gb']}GB</span>
      <a href="review_{plan['id']}.html" style="font-weight:700;font-size:0.85rem">詳細→</a>
    </div>
  </div>
</div>
"""

    # Data volume comparison
    html += """
<h2>📶 データ容量で比較</h2>
<table class="compare-table">
  <tr><th>格安SIM</th><th>最安プラン</th><th>最大プラン</th><th>月額（最安）</th><th>月額（最大）</th></tr>
"""
    for plan in plans:
        large = "無制限" if plan['data_gb_large'] == -1 else f"{plan['data_gb_large']}GB"
        large_price = "3,278円" if plan['large_plan_price'] == -1 else f"{plan['large_plan_price']:,}円" if plan['large_plan_price'] > 0 else "-"
        if plan['large_plan_price'] == -1:
            large_price = "3,278円"
        elif plan['large_plan_price'] > 0:
            large_price = f"{plan['large_plan_price']:,}円"
        else:
            large_price = "-"
        html += f"  <tr><td><strong>{plan['carrier']}</strong></td><td>{plan['data_gb']}GB</td><td>{large}</td><td>{plan['monthly_price']:,}円</td><td>{large_price}</td></tr>\n"

    html += "</table>\n"

    # Features comparison
    html += """
<h2>🔧 機能比較</h2>
<table class="compare-table">
  <tr><th>格安SIM</th><th>eSIM</th><th>海外利用</th><th>家族割</th><th>データ繰越</th><th>店舗サポート</th></tr>
"""
    for plan in plans:
        esim = "✅" if plan['esim'] else "❌"
        overseas = "✅" if plan['overseas'] else "❌"
        family = "✅" if plan['family_discount'] else "❌"
        # Infer data rollover and store support from features/cons
        rollover = "❌" if any("繰り越し不可" in c for c in plan['cons']) else "✅"
        store = "✅" if any("ショップ" in f or "店舗" in f or "対面" in f for f in plan['features']) else "❌"
        html += f"  <tr><td><strong>{plan['carrier']}</strong></td><td>{esim}</td><td>{overseas}</td><td>{family}</td><td>{rollover}</td><td>{store}</td></tr>\n"

    html += "</table>\n"

    html += """
<a href="ranking_overall.html" class="cta-button">
  おすすめ格安SIMランキングを見る
  <span class="sub-text">→ 総合評価で選ぶならこちら</span>
</a>
"""

    related = [
        ("格安SIMとは？初心者向けガイド", "guide_kakuyasu.html"),
        ("格安SIM おすすめランキング", "ranking_overall.html"),
        ("とにかく安い格安SIM ランキング", "ranking_cheapest.html"),
    ]

    html += html_footer(related)
    return html


# --- Index Page Generator ---
def generate_index(data):
    """Generate the top page."""
    today = datetime.date.today().strftime("%Y年%m月%d日")
    plans = data['sim_plans']

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>格安SIMラボ | 格安SIM・ネット回線 比較サイト</title>
  <meta name="description" content="格安SIMを料金・速度・サポートで徹底比較。あなたにぴったりの格安SIMが見つかります。">
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a href="index.html" class="site-logo">🔬 格安SIM<span>ラボ</span></a>
      <nav class="site-nav">
        <a href="index.html">トップ</a>
        <a href="output/ranking_overall.html">おすすめランキング</a>
      </nav>
    </div>
  </header>
  <main class="main-content">
    <div class="container">
      <div class="article-header">
        <h1>🔬 格安SIMラボ<br>あなたにベストな格安SIMを見つけよう</h1>
        <p class="article-meta">最終更新: <time>{today}</time></p>
      </div>
      <div class="article-body">
        <p>当サイトでは、人気の格安SIM・モバイル通信サービスを<strong>料金・速度・サポート</strong>の観点から比較し、あなたに最適なプランをご提案します。</p>

        <h2>📖 はじめての方へ</h2>
        <ul>
          <li><a href="output/guide_kakuyasu.html"><strong>格安SIMとは？</strong> 大手キャリアとの違い・メリット・デメリットを解説</a></li>
          <li><a href="output/hikaku_table.html"><strong>格安SIM 全{len(plans)}社 比較表</strong> — 料金・容量・機能を一覧で比較</a></li>
        </ul>

        <h2>📊 ランキング記事</h2>
        <ul>
"""
    for r in data.get('ranking_articles', []):
        html += f'          <li><a href="output/ranking_{r["id"]}.html">{r["title"]}</a></li>\n'

    html += """        </ul>

        <h2>📝 個別レビュー</h2>
        <ul>
"""
    for p in plans:
        html += f'          <li><a href="output/review_{p["id"]}.html">{p["carrier"]} 評判・メリット・デメリット</a></li>\n'

    html += """        </ul>

        <h2>⚔️ 比較記事</h2>
        <ul>
"""
    for pair in data.get('compare_pairs', []):
        a = get_plan(data, pair[0])
        b = get_plan(data, pair[1])
        if a and b:
            html += f'          <li><a href="output/compare_{pair[0]}_vs_{pair[1]}.html">{a["carrier"]} vs {b["carrier"]}</a></li>\n'

    html += f"""        </ul>
      </div>
    </div>
  </main>
  <footer class="site-footer">
    <div class="container">
      <p>&copy; {datetime.date.today().year} 格安SIMラボ</p>
      <p class="disclaimer">※ 当サイトはアフィリエイトプログラムに参加しています。</p>
    </div>
  </footer>
</body>
</html>"""
    return html


# --- Main ---
def main():
    print("🚀 記事生成を開始します...")
    
    data = load_data()
    plans = data['sim_plans']

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    count = 0

    # 1. Reviews
    for plan in plans:
        html = generate_review(plan, data)
        path = OUTPUT_DIR / f"review_{plan['id']}.html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✅ レビュー: {plan['carrier']} → {path.name}")
        count += 1

    # 2. Comparisons
    for pair in data.get('compare_pairs', []):
        plan_a = get_plan(data, pair[0])
        plan_b = get_plan(data, pair[1])
        if plan_a and plan_b:
            html = generate_comparison(plan_a, plan_b, data)
            path = OUTPUT_DIR / f"compare_{pair[0]}_vs_{pair[1]}.html"
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  ✅ 比較: {plan_a['carrier']} vs {plan_b['carrier']} → {path.name}")
            count += 1

    # 3. Rankings
    for ranking in data.get('ranking_articles', []):
        html = generate_ranking(ranking, data)
        path = OUTPUT_DIR / f"ranking_{ranking['id']}.html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✅ ランキング: {ranking['title']} → {path.name}")
        count += 1

    # 4. Guide article
    guide_html = generate_guide(data)
    guide_path = OUTPUT_DIR / "guide_kakuyasu.html"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_html)
    print(f"  ✅ ガイド: 格安SIMとは？ → guide_kakuyasu.html")
    count += 1

    # 5. Comparison table
    table_html = generate_comparison_table(data)
    table_path = OUTPUT_DIR / "hikaku_table.html"
    with open(table_path, 'w', encoding='utf-8') as f:
        f.write(table_html)
    print(f"  ✅ 比較表: 全プラン比較表 → hikaku_table.html")
    count += 1

    # 6. Index
    index_html = generate_index(data)
    index_path = BASE_DIR / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"  ✅ トップページ → index.html")
    count += 1

    print(f"\n🎉 完了！ {count}件の記事を生成しました。")
    print(f"📂 出力先: {OUTPUT_DIR}")
    print(f"🌐 index.html をブラウザで開いてください。")

if __name__ == "__main__":
    main()
