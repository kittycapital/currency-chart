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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>글로벌 환율 퍼포먼스 비교</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', -apple-system, sans-serif; 
            background: #000; 
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        .header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .title {{ font-size: 24px; font-weight: 700; }}
        .updated {{ font-size: 12px; color: #6b7280; }}
        
        .period-buttons {{
            display: flex;
            gap: 8px;
            background: #111;
            padding: 4px;
            border-radius: 8px;
        }}
        .period-btn {{
            padding: 8px 16px;
            border: none;
            background: transparent;
            color: #9ca3af;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .period-btn:hover {{ color: #fff; }}
        .period-btn.active {{ background: #3b82f6; color: #fff; }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
        }}
        @media (max-width: 1024px) {{
            .main-content {{ grid-template-columns: 1fr; }}
        }}
        
        .chart-container {{
            background: #111;
            border-radius: 12px;
            padding: 20px;
            height: 500px;
        }}
        
        .stats-box {{
            background: #111;
            border-radius: 12px;
            padding: 16px;
            max-height: 500px;
            overflow-y: auto;
        }}
        .stats-title {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #9ca3af;
        }}
        .stats-list {{ list-style: none; }}
        .stats-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #222;
            transition: all 0.2s;
        }}
        .stats-item:hover {{
            background: #1a1a1a;
            border-radius: 6px;
            padding-left: 8px;
            margin-left: -8px;
            padding-right: 8px;
            margin-right: -8px;
        }}
        .stats-item:last-child {{ border-bottom: none; }}
        .stats-asset {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .stats-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        .stats-name {{ font-weight: 500; font-size: 12px; }}
        .stats-symbol {{ color: #6b7280; font-size: 10px; }}
        .stats-perf {{
            font-weight: 600;
            font-size: 13px;
        }}
        .stats-perf.positive {{ color: #22c55e; }}
        .stats-perf.negative {{ color: #ef4444; }}
        
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 20px;
            padding: 16px;
            background: #111;
            border-radius: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
            opacity: 1;
            transition: opacity 0.2s;
        }}
        .legend-item.disabled {{ opacity: 0.3; }}
        .legend-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        .legend-label {{ font-size: 11px; color: #d1d5db; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 class="title">💱 글로벌 환율 퍼포먼스 비교</h1>
                <p class="updated">마지막 업데이트: {last_updated}</p>
            </div>
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
                <div class="stats-title">📈 수익률 (<span id="period-label">YTD</span>)</div>
                <ul class="stats-list" id="stats-list"></ul>
            </div>
        </div>
        
        <div class="legend" id="legend"></div>
    </div>

    <script>
        const ASSETS_DATA = {assets_json};
        
        let currentPeriod = 'YTD';
        let chart = null;
        let hiddenAssets = new Set();
        let selectedAsset = null;
        
        // 티커에서 표시용 이름 추출 (EURUSD=X -> EURUSD)
        function getDisplaySymbol(ticker) {{
            return ticker.replace('=X', '');
        }}
        
        // 기간별 날짜 계산
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
        
        // 가격 데이터를 % 변화로 변환
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
        
        // 차트 생성/업데이트
        function updateChart() {{
            const startDate = getStartDate(currentPeriod);
            const datasets = [];
            
            Object.entries(ASSETS_DATA).forEach(([symbol, data]) => {{
                if (hiddenAssets.has(symbol)) return;
                
                const percentData = calculatePercentChange(data.prices, startDate);
                if (percentData.length > 0) {{
                    // 선택 상태에 따른 스타일 결정
                    let borderWidth = 2;
                    let borderColor = data.color;
                    
                    if (selectedAsset) {{
                        if (symbol === selectedAsset) {{
                            borderWidth = 4;
                            borderColor = data.color;
                        }} else {{
                            borderWidth = 1;
                            borderColor = data.color + '50'; // 30% opacity
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
                            padding: {{ right: 85 }}
                        }},
                        interaction: {{
                            mode: 'index',
                            intersect: false
                        }},
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                backgroundColor: '#1f2937',
                                titleColor: '#fff',
                                bodyColor: '#d1d5db',
                                borderColor: '#374151',
                                borderWidth: 1,
                                padding: 10,
                                bodyFont: {{ size: 11 }},
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
                                grid: {{ color: '#222' }},
                                ticks: {{ color: '#6b7280', font: {{ size: 10 }} }}
                            }},
                            y: {{
                                grid: {{ color: '#222' }},
                                ticks: {{
                                    color: '#6b7280',
                                    font: {{ size: 10 }},
                                    callback: (v) => v + '%'
                                }}
                            }}
                        }}
                    }},
                    plugins: [{{
                        id: 'endLabels',
                        afterDraw: (chart) => {{
                            const ctx = chart.ctx;
                            const chartArea = chart.chartArea;
                            
                            // Collect all end points with their y positions
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
                            
                            // Sort by y position
                            endpoints.sort((a, b) => a.y - b.y);
                            
                            // Adjust overlapping labels (minimum 14px apart)
                            const minGap = 14;
                            for (let i = 1; i < endpoints.length; i++) {{
                                const prev = endpoints[i - 1];
                                const curr = endpoints[i];
                                if (curr.y - prev.y < minGap) {{
                                    curr.y = prev.y + minGap;
                                }}
                            }}
                            
                            // Draw labels
                            ctx.save();
                            endpoints.forEach(ep => {{
                                const sign = ep.value >= 0 ? '+' : '';
                                const text = `${{ep.label}} ${{sign}}${{ep.value.toFixed(1)}}%`;
                                
                                ctx.font = 'bold 9px Inter, sans-serif';
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
        
        // Stats 박스 업데이트
        function updateStats() {{
            const list = document.getElementById('stats-list');
            const periodLabel = document.getElementById('period-label');
            periodLabel.textContent = currentPeriod;
            
            // 성과순 정렬
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
                if (isHidden) {{
                    opacity = '0.3';
                }} else if (selectedAsset && !isSelected) {{
                    opacity = '0.4';
                }}
                
                const selectedStyle = isSelected ? 'background: #1f2937; border-radius: 6px; padding-left: 8px; margin-left: -8px; padding-right: 8px; margin-right: -8px;' : '';
                
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
            
            // Stats 아이템 클릭 이벤트
            list.querySelectorAll('.stats-item').forEach(item => {{
                item.addEventListener('click', () => {{
                    const symbol = item.dataset.symbol;
                    if (selectedAsset === symbol) {{
                        selectedAsset = null; // 같은 거 클릭하면 해제
                    }} else {{
                        selectedAsset = symbol; // 새로운 거 선택
                    }}
                    updateChart();
                    updateStats();
                }});
            }});
        }}
        
        // 범례 생성
        function createLegend() {{
            const legend = document.getElementById('legend');
            
            legend.innerHTML = Object.entries(ASSETS_DATA).map(([symbol, data]) => `
                <div class="legend-item" data-symbol="${{symbol}}">
                    <div class="legend-dot" style="background: ${{data.color}}"></div>
                    <span class="legend-label">${{getDisplaySymbol(symbol)}} (${{data.name}})</span>
                </div>
            `).join('');
            
            // 클릭 이벤트
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
        
        // 기간 버튼 이벤트
        document.querySelectorAll('.period-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentPeriod = btn.dataset.period;
                updateChart();
                updateStats();
            }});
        }});
        
        // 초기화
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
