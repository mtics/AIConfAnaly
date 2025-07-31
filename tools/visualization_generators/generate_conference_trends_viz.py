#!/usr/bin/env python3
"""
生成分会议研究领域趋势可视化页面
"""

import json
from pathlib import Path

def generate_conference_trends_visualization():
    """生成分会议趋势可视化页面"""
    
    # 读取研究趋势分析数据
    trends_file = Path("outputs/research_trends/research_trends_analysis.json")
    with open(trends_file, 'r', encoding='utf-8') as f:
        trends_data = json.load(f)
    
    # 读取基础分析数据
    analysis_file = Path("outputs/analysis/comprehensive_analysis.json")
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 创建HTML页面
    html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>分会议研究领域发展趋势分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}

        .header {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 40px 0;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header p {{
            font-size: 1.2em;
            color: #666;
            margin-bottom: 10px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        .section {{
            background: rgba(255,255,255,0.95);
            margin-bottom: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}

        .section-header {{
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
            color: white;
            padding: 25px;
            font-size: 1.4em;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-content {{
            padding: 30px;
        }}

        .chart-container {{
            width: 100%;
            height: 500px;
            margin-bottom: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .chart-large {{
            height: 600px;
        }}

        .chart-medium {{
            height: 400px;
        }}

        .conference-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .conference-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #3498db;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .conference-card:hover {{
            transform: translateY(-5px);
        }}

        .conference-card h3 {{
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #2c3e50;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }}

        .metric:last-child {{
            border-bottom: none;
        }}

        .metric-label {{
            font-weight: 500;
            color: #666;
        }}

        .metric-value {{
            font-weight: bold;
            color: #2c3e50;
        }}

        .field-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }}

        .field-tag {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
        }}

        .field-tag.core {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
        }}

        .field-tag.emerging {{
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .comparison-table th {{
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .comparison-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}

        .comparison-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        .trend-arrow {{
            font-size: 1.2em;
            font-weight: bold;
        }}

        .trend-up {{
            color: #27ae60;
        }}

        .trend-down {{
            color: #e74c3c;
        }}

        .trend-stable {{
            color: #f39c12;
        }}

        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .insight-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #3498db;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .insight-card h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .insight-card p {{
            color: #666;
            font-size: 0.95em;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 0 15px;
            }}
            
            .chart-container {{
                height: 350px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .conference-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🏛️ 分会议研究领域发展趋势分析</h1>
            <p>深度解析NeuRIPS、ICLR、AAAI三大顶级AI会议的研究重点与发展轨迹</p>
            <p>基于{trends_data['data_summary']['total_papers']:,}篇论文 | 分析期间：{trends_data['analysis_period']}</p>
        </div>
    </div>

    <div class="container">
        <!-- 会议概览对比 -->
        <div class="section">
            <div class="section-header">
                <span>📊</span>
                <span>会议发展概览对比</span>
            </div>
            <div class="section-content">
                <div class="conference-grid" id="conferenceOverview">
                    <!-- 会议卡片将通过JavaScript动态生成 -->
                </div>
                
                <div class="chart-container" id="conferenceComparisonChart"></div>
            </div>
        </div>

        <!-- 研究领域专业化分析 -->
        <div class="section">
            <div class="section-header">
                <span>🎯</span>
                <span>研究领域专业化程度分析</span>
            </div>
            <div class="section-content">
                <div class="chart-container chart-large" id="specializationChart"></div>
                
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>会议</th>
                            <th>核心专业领域</th>
                            <th>新兴关注领域</th>
                            <th>专业化水平</th>
                        </tr>
                    </thead>
                    <tbody id="specializationTable">
                        <!-- 表格内容将通过JavaScript生成 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 时间序列发展趋势 -->
        <div class="section">
            <div class="section-header">
                <span>📈</span>
                <span>时间序列发展趋势</span>
            </div>
            <div class="section-content">
                <div class="chart-container chart-large" id="timeSeriesChart"></div>
                
                <div class="chart-container" id="growthRateChart"></div>
            </div>
        </div>

        <!-- 领域竞争格局 -->
        <div class="section">
            <div class="section-header">
                <span>🏆</span>
                <span>研究领域竞争格局</span>
            </div>
            <div class="section-content">
                <div class="chart-container" id="competitionChart"></div>
                
                <div class="insights-grid" id="competitionInsights">
                    <!-- 竞争洞察将通过JavaScript生成 -->
                </div>
            </div>
        </div>

        <!-- 未来发展预测 -->
        <div class="section">
            <div class="section-header">
                <span>🔮</span>
                <span>会议发展趋势预测</span>
            </div>
            <div class="section-content">
                <div class="chart-container" id="predictionChart"></div>
                
                <div class="insights-grid" id="predictionInsights">
                    <!-- 预测洞察将通过JavaScript生成 -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // 嵌入完整数据
        const trendsData = {json.dumps(trends_data, ensure_ascii=False, indent=8)};
        const analysisData = {json.dumps(analysis_data, ensure_ascii=False, indent=8)};

        // 提取会议数据
        const conferenceData = trendsData.conference_analysis;
        const conferences = ['NeuRIPS', 'ICLR', 'AAAI'];

        // 生成会议概览卡片
        function generateConferenceOverview() {{
            const container = document.getElementById('conferenceOverview');
            
            conferences.forEach(conf => {{
                if (conferenceData[conf]) {{
                    const data = conferenceData[conf];
                    const card = document.createElement('div');
                    card.className = 'conference-card';
                    
                    const growthIcon = data.cagr > 20 ? '🚀' : data.cagr > 10 ? '📈' : '📊';
                    
                    card.innerHTML = `
                        <h3>${{conf}} ${{growthIcon}}</h3>
                        <div class="metric">
                            <span class="metric-label">总论文数</span>
                            <span class="metric-value">${{data.total_papers.toLocaleString()}}篇</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">年复合增长率</span>
                            <span class="metric-value">${{data.cagr}}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">峰值年份</span>
                            <span class="metric-value">${{data.peak_year}}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">专业化程度</span>
                            <span class="metric-value">${{data.concentration_level}}</span>
                        </div>
                        <div class="field-tags">
                            ${{data.core_fields.slice(0, 3).map(field => 
                                `<span class="field-tag core">${{field}}</span>`
                            ).join('')}}
                            ${{data.emerging_focus_areas.slice(0, 2).map(field => 
                                `<span class="field-tag emerging">${{field}}</span>`
                            ).join('')}}
                        </div>
                    `;
                    
                    container.appendChild(card);
                }}
            }});
        }}

        // 初始化所有图表
        function initializeCharts() {{
            // 会议对比雷达图
            const comparisonChart = echarts.init(document.getElementById('conferenceComparisonChart'));
            
            const radarData = conferences.map(conf => {{
                const data = conferenceData[conf];
                return {{
                    name: conf,
                    value: [
                        data.total_papers / 100, // 规模指数
                        data.cagr, // 增长率
                        data.concentration_index / 100, // 专业化指数
                        data.core_fields.length * 20, // 多样性指数
                        Math.max(...Object.values(data.specialization_scores)) * 1000 // 影响力指数
                    ]
                }};
            }});

            comparisonChart.setOption({{
                title: {{
                    text: '会议综合实力雷达图',
                    left: 'center',
                    textStyle: {{ fontSize: 18, fontWeight: 'bold' }}
                }},
                tooltip: {{}},
                legend: {{
                    data: conferences,
                    bottom: 20
                }},
                radar: {{
                    indicator: [
                        {{ name: '规模指数', max: 200 }},
                        {{ name: '增长率%', max: 50 }},
                        {{ name: '专业化指数', max: 50 }},
                        {{ name: '多样性指数', max: 100 }},
                        {{ name: '影响力指数', max: 300 }}
                    ],
                    radius: '70%'
                }},
                series: [{{
                    type: 'radar',
                    data: radarData
                }}]
            }});

            // 专业化热力图
            const specializationChart = echarts.init(document.getElementById('specializationChart'));
            
            const fields = Object.keys(conferenceData.NeuRIPS.specialization_scores);
            const heatmapData = [];
            
            conferences.forEach((conf, confIndex) => {{
                fields.forEach((field, fieldIndex) => {{
                    const value = conferenceData[conf].specialization_scores[field] || 0;
                    heatmapData.push([confIndex, fieldIndex, Math.round(value * 1000)]);
                }});
            }});

            specializationChart.setOption({{
                title: {{
                    text: '会议-领域专业化热力图',
                    left: 'center',
                    textStyle: {{ fontSize: 18, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    position: 'top',
                    formatter: function(params) {{
                        return `${{conferences[params.value[0]]}}<br/>
                                ${{fields[params.value[1]]}}<br/>
                                专业化指数: ${{(params.value[2] / 1000).toFixed(3)}}`;
                    }}
                }},
                grid: {{
                    height: '60%',
                    top: '10%'
                }},
                xAxis: {{
                    type: 'category',
                    data: conferences,
                    splitArea: {{ show: true }}
                }},
                yAxis: {{
                    type: 'category',
                    data: fields,
                    splitArea: {{ show: true }}
                }},
                visualMap: {{
                    min: 0,
                    max: 300,
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '5%',
                    inRange: {{
                        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', 
                               '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
                    }}
                }},
                series: [{{
                    name: '专业化程度',
                    type: 'heatmap',
                    data: heatmapData,
                    label: {{ show: false }},
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }}
                }}]
            }});

            // 时间序列趋势
            const timeSeriesChart = echarts.init(document.getElementById('timeSeriesChart'));
            const years = [2018, 2019, 2020, 2021, 2022, 2023];
            
            const seriesData = conferences.map(conf => ({{
                name: conf,
                type: 'line',
                data: conferenceData[conf].yearly_papers.slice(0, 6),
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: {{ width: 3 }}
            }}));

            timeSeriesChart.setOption({{
                title: {{
                    text: '各会议论文数量时间序列',
                    left: 'center',
                    textStyle: {{ fontSize: 18, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                legend: {{
                    data: conferences,
                    bottom: 20
                }},
                grid: {{
                    left: '3%',
                    right: '4%',
                    bottom: '15%',
                    containLabel: true
                }},
                xAxis: {{
                    type: 'category',
                    data: years,
                    name: '年份'
                }},
                yAxis: {{
                    type: 'value',
                    name: '论文数量'
                }},
                series: seriesData
            }});

            // 增长率对比
            const growthChart = echarts.init(document.getElementById('growthRateChart'));
            
            growthChart.setOption({{
                title: {{
                    text: '会议年复合增长率对比',
                    left: 'center',
                    textStyle: {{ fontSize: 18, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis',
                    formatter: function(params) {{
                        return `${{params[0].name}}<br/>CAGR: ${{params[0].value}}%`;
                    }}
                }},
                xAxis: {{
                    type: 'category',
                    data: conferences
                }},
                yAxis: {{
                    type: 'value',
                    name: 'CAGR (%)'
                }},
                series: [{{
                    type: 'bar',
                    data: conferences.map(conf => conferenceData[conf].cagr),
                    itemStyle: {{
                        color: function(params) {{
                            const colors = ['#3498db', '#e74c3c', '#27ae60'];
                            return colors[params.dataIndex];
                        }}
                    }}
                }}]
            }});

            // 竞争格局分析
            const competitionChart = echarts.init(document.getElementById('competitionChart'));
            
            // 构建竞争数据：规模 vs 增长率
            const competitionData = conferences.map(conf => {{
                const data = conferenceData[conf];
                return {{
                    name: conf,
                    value: [data.total_papers, data.cagr, data.concentration_index]
                }};
            }});

            competitionChart.setOption({{
                title: {{
                    text: '会议竞争格局：规模 vs 增长率',
                    left: 'center',
                    textStyle: {{ fontSize: 18, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: function(params) {{
                        return `${{params.name}}<br/>
                                总论文数: ${{params.value[0].toLocaleString()}}<br/>
                                CAGR: ${{params.value[1]}}%<br/>
                                专业化指数: ${{params.value[2]}}`;
                    }}
                }},
                xAxis: {{
                    type: 'value',
                    name: '总论文数',
                    nameLocation: 'middle',
                    nameGap: 30
                }},
                yAxis: {{
                    type: 'value',
                    name: 'CAGR (%)',
                    nameLocation: 'middle',
                    nameGap: 50
                }},
                series: [{{
                    type: 'scatter',
                    symbolSize: function(data) {{
                        return Math.sqrt(data[2]) * 3;
                    }},
                    data: competitionData,
                    label: {{
                        show: true,
                        position: 'top',
                        formatter: function(params) {{
                            return params.name;
                        }}
                    }}
                }}]
            }});

            // 预测图表
            const predictionChart = echarts.init(document.getElementById('predictionChart'));
            const allYears = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
            
            const predictionSeries = conferences.map(conf => {{
                const historicalData = conferenceData[conf].yearly_papers.slice(0, 6);
                const prediction = trendsData.predictions.conference_evolution[conf];
                const predicted2025 = prediction.predicted_2025_papers;
                
                // 估算2024年数据（线性插值）
                const estimated2024 = Math.round((historicalData[5] + predicted2025) / 2);
                
                const fullData = [...historicalData, estimated2024, predicted2025];
                
                return {{
                    name: conf,
                    type: 'line',
                    data: fullData,
                    markLine: {{
                        data: [{{ xAxis: 6 }}],
                        lineStyle: {{ type: 'dashed', color: '#999' }},
                        label: {{ formatter: '预测线' }}
                    }}
                }};
            }});

            predictionChart.setOption({{
                title: {{
                    text: '会议发展趋势预测（2018-2025）',
                    left: 'center',
                    textStyle: {{ fontSize: 18, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                legend: {{
                    data: conferences,
                    bottom: 20
                }},
                grid: {{
                    left: '3%',
                    right: '4%',
                    bottom: '15%',
                    containLabel: true
                }},
                xAxis: {{
                    type: 'category',
                    data: allYears,
                    name: '年份'
                }},
                yAxis: {{
                    type: 'value',
                    name: '论文数量'
                }},
                series: predictionSeries
            }});
        }}

        // 生成专业化表格
        function generateSpecializationTable() {{
            const tbody = document.getElementById('specializationTable');
            
            conferences.forEach(conf => {{
                if (conferenceData[conf]) {{
                    const data = conferenceData[conf];
                    const row = tbody.insertRow();
                    
                    row.innerHTML = `
                        <td><strong>${{conf}}</strong></td>
                        <td>${{data.core_fields.slice(0, 3).join(', ')}}</td>
                        <td>${{data.emerging_focus_areas.slice(0, 2).join(', ') || '无'}}</td>
                        <td>${{data.concentration_level}}</td>
                    `;
                }}
            }});
        }}

        // 生成竞争洞察
        function generateCompetitionInsights() {{
            const container = document.getElementById('competitionInsights');
            const comparison = conferenceData.inter_conference_comparison;
            
            const insights = [
                {{
                    title: '增长速度冠军',
                    content: `${{comparison.growth_speed_ranking[0][0]}}以${{comparison.growth_speed_ranking[0][1]}}%的年复合增长率领跑发展速度`,
                    icon: '🚀'
                }},
                {{
                    title: '规模霸主',
                    content: `${{comparison.size_ranking[0][0]}}以${{comparison.size_ranking[0][1].toLocaleString()}}篇论文稳居规模第一`,
                    icon: '👑'
                }},
                {{
                    title: '专业化程度',
                    content: `${{comparison.specialization_ranking[0][0]}}专业化程度最高，聚焦特定领域深耕`,
                    icon: '🎯'
                }},
                {{
                    title: '多样性分析',
                    content: `各会议在研究领域分布上呈现差异化发展格局`,
                    icon: '🌈'
                }}
            ];
            
            insights.forEach(insight => {{
                const card = document.createElement('div');
                card.className = 'insight-card';
                card.innerHTML = `
                    <h4>${{insight.icon}} ${{insight.title}}</h4>
                    <p>${{insight.content}}</p>
                `;
                container.appendChild(card);
            }});
        }}

        // 生成预测洞察
        function generatePredictionInsights() {{
            const container = document.getElementById('predictionInsights');
            const predictions = trendsData.predictions.conference_evolution;
            
            const insights = [
                {{
                    title: '整体发展态势',
                    content: '三大会议均呈现稳健增长态势，预计2025年总体规模将进一步扩大',
                    icon: '📈'
                }},
                {{
                    title: 'ICLR发展潜力',
                    content: `ICLR凭借${{conferenceData.ICLR.cagr}}%的高增长率，有望在未来几年大幅缩小与领先会议的差距`,
                    icon: '⭐'
                }},
                {{
                    title: '专业化趋势',
                    content: '各会议专业化特色日益明显，形成差异化竞争优势',
                    icon: '🎯'
                }},
                {{
                    title: '研究热点转移',
                    content: '新兴领域如Manufacturing、Medical Diagnosis将成为各会议竞争焦点',
                    icon: '🔥'
                }}
            ];
            
            insights.forEach(insight => {{
                const card = document.createElement('div');
                card.className = 'insight-card';
                card.innerHTML = `
                    <h4>${{insight.icon}} ${{insight.title}}</h4>
                    <p>${{insight.content}}</p>
                `;
                container.appendChild(card);
            }});
        }}

        // 页面初始化
        document.addEventListener('DOMContentLoaded', function() {{
            generateConferenceOverview();
            generateSpecializationTable();
            generateCompetitionInsights();
            generatePredictionInsights();
            initializeCharts();
            
            // 响应式处理
            window.addEventListener('resize', function() {{
                const chartIds = ['conferenceComparisonChart', 'specializationChart', 'timeSeriesChart', 
                                 'growthRateChart', 'competitionChart', 'predictionChart'];
                chartIds.forEach(id => {{
                    const chart = echarts.getInstanceByDom(document.getElementById(id));
                    if (chart) chart.resize();
                }});
            }});
            
            console.log('分会议趋势可视化页面初始化完成');
        }});
    </script>
</body>
</html>"""

    # 保存HTML文件
    output_file = Path("frontend/conference_trends.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 分会议趋势可视化页面已生成: {output_file}")

if __name__ == "__main__":
    generate_conference_trends_visualization()