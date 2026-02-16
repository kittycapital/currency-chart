#!/usr/bin/env python3
"""
JSON 데이터를 읽어서 차트 HTML 생성
"""

import json
from pathlib import Path
from datetime import datetime

def generate_html():
    # 데이터 로드
    data_path = Path(__file__).parent.parent / "data" / "performance.json"
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    last_updated = data["lastUpdated"]
    assets_json = json.dumps(data["assets"], ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>글로벌 환율 퍼포먼스 비교</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
    <script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js"></script>
    <style>
        :root {{
            --bg: #000000;
            --surface: #0a0a0a;
            --surface2: #111111;
            --border: #1a1a1a;
            --border-hover: #2a2a2a;
            --text: #e4e4e7;
            --text-dim: #71717a;
            --text-muted: #52525b;
            --green: #22c55e;
            --red: #ef4444;
            --cyan: #22d3ee;
            --blue: #4a90ff;
            --gold: #ffd644;
            --mono: 'JetBrains Mono', monospace;
            --sans: 'Noto Sans KR', -apple-system, sans-serif;
            --radius: 12px;
            --radius-sm: 8px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scrollbar-width: none; }}
        html::-webkit-scrollbar {{ display: none; }}
        html, body {{
            height: 100%;
            overflow: hidden;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--sans);
            padding: 0;
            -webkit-overflow-scrolling: touch;
            -webkit-font-smoothing: antialiased;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}

        /* ====== HEADER ====== */
        .header {{
            padding: 20px 20px 14px;
            text-align: center;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }}
        .header h1 {{
            font-size: clamp(18px, 4vw, 28px);
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.02em;
            margin-bottom: 4px;
        }}
        .sub {{ font-size: 12px; color: var(--text-dim); }}
        .time {{ font-family: var(--mono); font-size: 10px; color: var(--text-muted); margin-top: 6px; }}

        /* ====== SHARE ====== */
        .share-bar {{ display: flex; gap: 5px; justify-content: center; margin: 10px 0 2px; flex-wrap: wrap; flex-shrink: 0; }}
        .share-btn {{ display: flex; align-items: center; gap: 4px; padding: 5px 10px; border-radius: 6px; border: 1px solid var(--border-hover); background: var(--surface); color: #a1a1aa; font-size: 10px; cursor: pointer; font-family: var(--sans); transition: all 0.2s; -webkit-tap-highlight-color: transparent; touch-action: manipulation; }}
        .share-btn:hover {{ border-color: #444; color: var(--text); }}
        .share-btn svg {{ width: 13px; height: 13px; flex-shrink: 0; }}
        .share-btn.twitter:hover {{ border-color: #1d9bf0; color: #1d9bf0; }}
        .share-btn.kakao:hover {{ border-color: #fee500; color: #fee500; }}
        .share-btn.telegram:hover {{ border-color: #26a5e4; color: #26a5e4; }}
        .share-btn.instagram:hover {{ border-color: #e1306c; color: #e1306c; }}
        .share-btn.instagram.copied {{ border-color: var(--green); color: var(--green); }}
        .share-btn.copy:hover {{ border-color: var(--green); color: var(--green); }}
        .share-btn.copied {{ border-color: var(--green); color: var(--green); }}

        .toast {{ position: fixed; bottom: 20px; right: 20px; background: var(--green); color: #000; padding: 10px 16px; border-radius: var(--radius-sm); font-size: 13px; font-weight: 600; z-index: 9999; opacity: 0; transform: translateY(10px); transition: all 0.3s ease; pointer-events: none; }}
        .toast.show {{ opacity: 1; transform: translateY(0); }}

        /* ====== CONTROLS ====== */
        .controls {{
            display: flex;
            justify-content: center;
            padding: 10px 16px;
            flex-shrink: 0;
        }}
        .period-buttons {{
            display: flex;
            gap: 4px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 3px;
            border-radius: var(--radius-sm);
            flex-shrink: 0;
        }}
        .period-btn {{
            padding: 6px 12px;
            border: none;
            background: transparent;
            color: var(--text-dim);
            font: 500 12px var(--sans);
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }}
        .period-btn:hover {{ color: var(--text); }}
        .period-btn.active {{ background: var(--cyan); color: #000; font-weight: 600; }}

        /* ====== MAIN CONTENT ====== */
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 260px;
            gap: 12px;
            flex: 1;
            min-height: 0;
            padding: 0 16px;
        }}

        /* ====== CHART ====== */
        .chart-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 14px;
            min-height: 0;
            position: relative;
        }}
        .chart-container::after {{
            content: 'Herdvibe.com';
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            font: 700 26px var(--mono);
            color: rgba(255,255,255,0.04);
            pointer-events: none;
            z-index: 2;
            white-space: nowrap;
        }}

        /* ====== STATS BOX ====== */
        .stats-box {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 12px;
            overflow-y: auto;
            min-height: 0;
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
        .stats-box::-webkit-scrollbar {{ display: none; }}

        .stats-title {{
            font: 600 13px var(--sans);
            color: var(--text);
            margin-bottom: 8px;
            text-align: center;
        }}
        .stats-list {{ list-style: none; }}
        .stats-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid var(--border);
            transition: all 0.15s;
            -webkit-tap-highlight-color: transparent;
        }}
        .stats-item:active {{
            background: var(--surface2);
            border-radius: 6px;
            padding-left: 8px;
            margin-left: -8px;
            padding-right: 8px;
            margin-right: -8px;
        }}
        @media (hover: hover) {{
            .stats-item:hover {{
                background: var(--surface2);
                border-radius: 6px;
                padding-left: 8px;
                margin-left: -8px;
                padding-right: 8px;
                margin-right: -8px;
            }}
        }}
        .stats-item:last-child {{ border-bottom: none; }}
        .stats-asset {{
            display: flex;
            align-items: center;
            gap: 6px;
            min-width: 0;
        }}
        .stats-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .stats-name {{ font: 500 11px var(--sans); white-space: nowrap; }}
        .stats-symbol {{ color: var(--text-muted); font-size: 9px; }}
        .stats-perf {{
            font: 600 12px var(--mono);
            flex-shrink: 0;
            margin-left: 8px;
        }}
        .stats-perf.positive {{ color: var(--green); }}
        .stats-perf.negative {{ color: var(--red); }}

        /* ====== LEGEND ====== */
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 16px;
            padding: 10px 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            flex-shrink: 0;
            justify-content: center;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            opacity: 1;
            transition: opacity 0.2s;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }}
        .legend-item.disabled {{ opacity: 0.3; }}
        .legend-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .legend-label {{ font-size: 10px; color: var(--text-dim); white-space: nowrap; }}

        /* ====== FOOTER ====== */
        .footer {{
            padding: 8px 16px 16px;
            text-align: center;
            font-size: 9px;
            color: var(--text-muted);
            flex-shrink: 0;
        }}

        /* === TABLET === */
        @media (max-width: 1024px) {{
            .main-content {{
                grid-template-columns: 1fr;
                grid-template-rows: 1fr auto;
            }}
            .stats-box {{ max-height: 180px; }}
        }}

        /* === MOBILE === */
        @media (max-width: 600px) {{
            .header {{ padding: 14px 12px 10px; }}
            .header h1 {{ font-size: 16px; }}
            .share-bar {{ gap: 4px; margin: 8px 0 2px; }}
            .share-btn {{ padding: 4px 8px; font-size: 9px; }}
            .share-btn svg {{ width: 11px; height: 11px; }}
            .controls {{ padding: 8px 12px; }}
            .period-buttons {{
                width: 100%;
                justify-content: space-between;
            }}
            .period-btn {{
                flex: 1;
                padding: 7px 2px;
                font-size: 11px;
                text-align: center;
            }}
            .main-content {{
                grid-template-columns: 1fr;
                grid-template-rows: 1fr auto;
                gap: 8px;
                padding: 0 10px;
            }}
            .chart-container {{
                padding: 8px 4px 8px 8px;
                border-radius: 10px;
            }}
            .chart-container::after {{ font-size: 18px; }}
            .stats-box {{
                padding: 10px;
                max-height: 150px;
                border-radius: 10px;
            }}
            .stats-item {{ padding: 5px 0; }}
            .stats-name {{ font-size: 10px; }}
            .stats-perf {{ font-size: 11px; }}
            .legend {{
                gap: 6px;
                padding: 8px 10px;
                margin: 8px 10px;
                border-radius: 8px;
            }}
            .legend-label {{ font-size: 9px; }}
            .legend-dot {{ width: 6px; height: 6px; }}
            .footer {{ padding: 6px 10px 12px; font-size: 8px; }}
        }}

        /* === 아주 작은 화면 === */
        @media (max-width: 420px) {{
            .header {{ padding: 10px 8px 8px; }}
            .header h1 {{ font-size: 14px; }}
            .stats-box {{ max-height: 130px; }}
            .legend {{ gap: 4px; padding: 6px 8px; }}
            .legend-label {{ font-size: 8px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>글로벌 환율 퍼포먼스 비교</h1>
            <div class="sub">주요 통화쌍 환율 변동률 비교 — 달러 강약 흐름 한눈에 파악</div>
            <div class="time">마지막 업데이트: {last_updated}</div>
        </div>

        <div class="share-bar">
            <button class="share-btn twitter" onclick="shareTwitter()"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>트위터</button>
            <button class="share-btn kakao" onclick="shareKakao()"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3c-5.52 0-10 3.36-10 7.5 0 2.66 1.74 5 4.36 6.33-.14.53-.9 3.4-.93 3.61 0 0-.02.17.09.23.11.07.24.03.24.03.32-.04 3.7-2.42 4.28-2.83.62.09 1.27.13 1.96.13 5.52 0 10-3.36 10-7.5S17.52 3 12 3z"/></svg>카카오톡</button>
            <button class="share-btn telegram" onclick="shareTelegram()"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.479.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>텔레그램</button>
            <button class="share-btn instagram" onclick="shareInstagram(this)"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>인스타그램</button>
            <button class="share-btn copy" onclick="copyLink(this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>링크복사</button>
        </div>

        <div class="controls">
            <div class="period-buttons">
                <button class="period-btn" data-period="1W">1주</button>
                <button class="period-btn" data-period="1M">1개월</button>
                <button class="period-btn" data-period="3M">3개월</button>
                <button class="period-btn" data-period="12M">1년</button>
                <button class="period-btn active" data-period="YTD">YTD</button>
            </div>
        </div>

        <div class="main-content">
            <div class="chart-container">
                <canvas id="perfChart"></canvas>
            </div>
            <div class="stats-box">
                <div class="stats-title">변동률 (<span id="period-label">YTD</span>)</div>
                <ul class="stats-list" id="stats-list"></ul>
            </div>
        </div>

        <div class="legend" id="legend"></div>

        <div class="footer">데이터 출처: Yahoo Finance · 주요 통화쌍 기준 · 투자 판단은 본인의 책임입니다</div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        /* ====== SHARE ====== */
        const SHARE_URL = 'https://herdvibe.com/fx-performance';
        const SHARE_TITLE = '글로벌 환율 퍼포먼스 비교 — Herdvibe';
        const SHARE_DESC = '주요 통화쌍 환율 변동률 비교 | Herdvibe';

        function showToast(msg) {{
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 3000);
        }}
        function shareTwitter() {{
            window.open(`https://twitter.com/intent/tweet?text=${{encodeURIComponent(SHARE_TITLE)}}&url=${{encodeURIComponent(SHARE_URL)}}`, '_blank');
        }}
        function shareKakao() {{
            if (window.Kakao && !Kakao.isInitialized()) Kakao.init('a43ed7b39fac35458f4f9df925a279b5');
            if (window.Kakao) {{
                Kakao.Share.sendDefault({{
                    objectType: 'feed',
                    content: {{ title: SHARE_TITLE, description: SHARE_DESC, imageUrl: 'https://herdvibe.com/og-fx.png', link: {{ mobileWebUrl: SHARE_URL, webUrl: SHARE_URL }} }}
                }});
            }}
        }}
        function shareTelegram() {{
            window.open(`https://t.me/share/url?url=${{encodeURIComponent(SHARE_URL)}}&text=${{encodeURIComponent(SHARE_TITLE)}}`, '_blank');
        }}
        function shareInstagram(btn) {{
            try {{
                if (window.parent !== window) {{ window.parent.postMessage({{ type: 'copy', text: SHARE_URL }}, '*'); }}
                else {{ navigator.clipboard.writeText(SHARE_URL); }}
                const orig = btn.innerHTML;
                btn.classList.add('copied');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>복사됨!';
                showToast('링크가 복사되었습니다 - 인스타그램에 붙여넣기 하세요');
                setTimeout(() => {{ btn.classList.remove('copied'); btn.innerHTML = orig; }}, 2000);
            }} catch(e) {{ showToast('복사 실패'); }}
        }}
        function copyLink(btn) {{
            try {{
                if (window.parent !== window) {{ window.parent.postMessage({{ type: 'copy', text: SHARE_URL }}, '*'); }}
                else {{ navigator.clipboard.writeText(SHARE_URL); }}
                const orig = btn.innerHTML;
                btn.classList.add('copied');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>복사됨!';
                showToast('링크가 복사되었습니다');
                setTimeout(() => {{ btn.classList.remove('copied'); btn.innerHTML = orig; }}, 2000);
            }} catch(e) {{ showToast('복사 실패'); }}
        }}

        /* ====== DATA ====== */
        const ASSETS_DATA = {assets_json};

        let currentPeriod = 'YTD';
        let chart = null;
        let hiddenAssets = new Set();
        let selectedAsset = null;

        function getDisplaySymbol(ticker) {{
            return ticker.replace('=X', '');
        }}

        function getStartDate(period) {{
            const now = new Date();
            switch(period) {{
                case '1W': return new Date(now - 7 * 24 * 60 * 60 * 1000);
                case '1M': return new Date(now - 30 * 24 * 60 * 60 * 1000);
                case '3M': return new Date(now - 90 * 24 * 60 * 60 * 1000);
                case '12M': return new Date(now - 365 * 24 * 60 * 60 * 1000);
                case 'YTD': return new Date(now.getFullYear(), 0, 1);
                default: return new Date(now.getFullYear(), 0, 1);
            }}
        }}

        function calculatePercentChange(prices, startDate) {{
            const startStr = startDate.toISOString().split('T')[0];
            const filtered = prices.filter(p => p.date >= startStr);
            if (filtered.length === 0) return [];
            const basePrice = filtered[0].price;
            return filtered.map(p => ({{
                x: p.date,
                y: ((p.price - basePrice) / basePrice * 100).toFixed(2)
            }}));
        }}

        function updateChart() {{
            const startDate = getStartDate(currentPeriod);
            const datasets = [];

            Object.entries(ASSETS_DATA).forEach(([symbol, data]) => {{
                if (hiddenAssets.has(symbol)) return;
                const percentData = calculatePercentChange(data.prices, startDate);
                if (percentData.length > 0) {{
                    let borderWidth = 2;
                    let borderColor = data.color;

                    if (selectedAsset) {{
                        if (symbol === selectedAsset) {{
                            borderWidth = 4;
                        }} else {{
                            borderWidth = 1;
                            borderColor = data.color + '50';
                        }}
                    }}

                    datasets.push({{
                        label: getDisplaySymbol(symbol),
                        data: percentData,
                        borderColor: borderColor,
                        backgroundColor: data.color + '20',
                        borderWidth: borderWidth,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.1,
                        fill: false,
                        originalColor: data.color,
                        symbol: symbol
                    }});
                }}
            }});

            if (chart) {{
                chart.data.datasets = datasets;
                chart.update('none');
            }} else {{
                const ctx = document.getElementById('perfChart').getContext('2d');
                chart = new Chart(ctx, {{
                    type: 'line',
                    data: {{ datasets }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {{
                            padding: {{ right: window.innerWidth <= 600 ? 5 : 85 }}
                        }},
                        interaction: {{
                            mode: 'index',
                            intersect: false
                        }},
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                backgroundColor: '#18181b',
                                titleColor: '#fff',
                                bodyColor: '#a1a1aa',
                                borderColor: '#2a2a2a',
                                borderWidth: 1,
                                padding: window.innerWidth <= 600 ? 6 : 10,
                                titleFont: {{ family: 'Noto Sans KR' }},
                                bodyFont: {{ family: 'JetBrains Mono', size: window.innerWidth <= 600 ? 10 : 11 }},
                                callbacks: {{
                                    label: (ctx) => `${{ctx.dataset.label}}: ${{ctx.parsed.y >= 0 ? '+' : ''}}${{ctx.parsed.y}}%`
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                type: 'time',
                                time: {{
                                    unit: currentPeriod === '1W' ? 'day' :
                                          currentPeriod === '1M' ? 'week' : 'month',
                                    displayFormats: {{
                                        day: 'MM/dd',
                                        week: 'MM/dd',
                                        month: 'yy/MM'
                                    }}
                                }},
                                grid: {{ color: '#1a1a1a' }},
                                ticks: {{ color: '#52525b', font: {{ family: 'JetBrains Mono', size: window.innerWidth <= 600 ? 9 : 10 }} }}
                            }},
                            y: {{
                                grid: {{ color: '#1a1a1a' }},
                                ticks: {{
                                    color: '#52525b',
                                    font: {{ family: 'JetBrains Mono', size: window.innerWidth <= 600 ? 9 : 10 }},
                                    callback: (v) => v + '%'
                                }}
                            }}
                        }}
                    }},
                    plugins: [{{
                        id: 'endLabels',
                        afterDraw: (chart) => {{
                            if (window.innerWidth <= 600) return;

                            const ctx = chart.ctx;
                            const chartArea = chart.chartArea;
                            const endpoints = [];

                            chart.data.datasets.forEach((dataset, i) => {{
                                const meta = chart.getDatasetMeta(i);
                                if (meta.hidden) return;
                                const lastPoint = meta.data[meta.data.length - 1];
                                if (!lastPoint) return;
                                const value = parseFloat(dataset.data[dataset.data.length - 1].y);
                                endpoints.push({{
                                    y: lastPoint.y,
                                    originalY: lastPoint.y,
                                    value: value,
                                    label: dataset.label,
                                    color: dataset.borderColor
                                }});
                            }});

                            endpoints.sort((a, b) => a.y - b.y);
                            const minGap = 14;
                            for (let i = 1; i < endpoints.length; i++) {{
                                if (endpoints[i].y - endpoints[i-1].y < minGap) {{
                                    endpoints[i].y = endpoints[i-1].y + minGap;
                                }}
                            }}

                            ctx.save();
                            endpoints.forEach(ep => {{
                                const sign = ep.value >= 0 ? '+' : '';
                                const text = `${{ep.label}} ${{sign}}${{ep.value.toFixed(1)}}%`;
                                ctx.font = 'bold 9px JetBrains Mono, monospace';
                                ctx.fillStyle = ep.color;
                                ctx.textAlign = 'left';
                                ctx.textBaseline = 'middle';
                                ctx.fillText(text, chartArea.right + 5, ep.y);
                            }});
                            ctx.restore();
                        }}
                    }}]
                }});
            }}
        }}

        function updateStats() {{
            const list = document.getElementById('stats-list');
            document.getElementById('period-label').textContent = currentPeriod;

            const sorted = Object.entries(ASSETS_DATA)
                .map(([symbol, data]) => ({{
                    symbol,
                    displaySymbol: getDisplaySymbol(symbol),
                    name: data.name,
                    color: data.color,
                    perf: data.performance[currentPeriod]
                }}))
                .filter(a => a.perf !== null)
                .sort((a, b) => b.perf - a.perf);

            list.innerHTML = sorted.map(asset => {{
                const perfClass = asset.perf >= 0 ? 'positive' : 'negative';
                const perfSign = asset.perf >= 0 ? '+' : '';
                const isHidden = hiddenAssets.has(asset.symbol);
                const isSelected = selectedAsset === asset.symbol;

                let opacity = '1';
                if (isHidden) {{ opacity = '0.3'; }}
                else if (selectedAsset && !isSelected) {{ opacity = '0.4'; }}

                const selectedStyle = isSelected ? 'background: rgba(34,211,238,0.08); border-radius: 6px; padding-left: 8px; margin-left: -8px; padding-right: 8px; margin-right: -8px;' : '';

                return `
                    <li class="stats-item" data-symbol="${{asset.symbol}}" style="opacity: ${{opacity}}; cursor: pointer; ${{selectedStyle}}">
                        <div class="stats-asset">
                            <div class="stats-dot" style="background: ${{asset.color}}"></div>
                            <span class="stats-name">${{asset.displaySymbol}} <span class="stats-symbol">(${{asset.name}})</span></span>
                        </div>
                        <span class="stats-perf ${{perfClass}}">${{perfSign}}${{asset.perf}}%</span>
                    </li>
                `;
            }}).join('');

            list.querySelectorAll('.stats-item').forEach(item => {{
                item.addEventListener('click', () => {{
                    const symbol = item.dataset.symbol;
                    if (selectedAsset === symbol) {{ selectedAsset = null; }}
                    else {{ selectedAsset = symbol; }}
                    updateChart();
                    updateStats();
                }});
            }});
        }}

        function createLegend() {{
            const legend = document.getElementById('legend');
            legend.innerHTML = Object.entries(ASSETS_DATA).map(([symbol, data]) =>
                `<div class="legend-item" data-symbol="${{symbol}}">
                    <div class="legend-dot" style="background: ${{data.color}}"></div>
                    <span class="legend-label">${{getDisplaySymbol(symbol)}} (${{data.name}})</span>
                </div>`
            ).join('');

            legend.querySelectorAll('.legend-item').forEach(item => {{
                item.addEventListener('click', () => {{
                    const symbol = item.dataset.symbol;
                    if (hiddenAssets.has(symbol)) {{
                        hiddenAssets.delete(symbol);
                        item.classList.remove('disabled');
                    }} else {{
                        hiddenAssets.add(symbol);
                        item.classList.add('disabled');
                    }}
                    updateChart();
                    updateStats();
                }});
            }});
        }}

        document.querySelectorAll('.period-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentPeriod = btn.dataset.period;
                updateChart();
                updateStats();
            }});
        }});

        let resizeTimeout;
        window.addEventListener('resize', () => {{
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {{
                if (chart) {{
                    const isMobile = window.innerWidth <= 600;
                    chart.options.layout.padding.right = isMobile ? 5 : 85;
                    chart.update('none');
                }}
            }}, 200);
        }});

        createLegend();
        updateChart();
        updateStats();
    </script>
</body>
</html>'''
    
    output_path = Path(__file__).parent.parent / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ HTML 생성 완료: {output_path}")


if __name__ == "__main__":
    generate_html()
