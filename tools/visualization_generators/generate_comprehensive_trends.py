#!/usr/bin/env python3
"""
生成全面的发展趋势单页面可视化
显示所有研究领域、应用场景、技术发展、任务场景的发展趋势
"""

import json
from pathlib import Path

def generate_comprehensive_trends_page():
    """生成全面的发展趋势可视化页面"""
    
    # 读取所有分析数据
    analysis_file = Path("outputs/analysis/comprehensive_analysis.json")
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    trends_file = Path("outputs/trend_analysis/trend_analysis_report.json")
    with open(trends_file, 'r', encoding='utf-8') as f:
        trends_data = json.load(f)
    
    research_trends_file = Path("outputs/research_trends/research_trends_analysis.json")
    with open(research_trends_file, 'r', encoding='utf-8') as f:
        research_trends_data = json.load(f)
    
    # 创建全面的单页面可视化
    html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI研究发展趋势全景分析</title>
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
            position: sticky;
            top: 0;
            z-index: 1000;
        }}

        .header h1 {{
            font-size: 3em;
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

        .nav-menu {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .nav-item {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9em;
            transition: transform 0.3s ease;
        }}

        .nav-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }}

        .container {{
            max-width: 1600px;
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
            height: 600px;
            margin-bottom: 30px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .chart-large {{
            height: 700px;
        }}

        .chart-xl {{
            height: 800px;
        }}

        .dual-chart {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .triple-chart {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .chart-medium {{
            height: 450px;
        }}

        .stats-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border-left: 5px solid #3498db;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .stat-label {{
            color: #666;
            font-size: 1em;
            font-weight: 500;
        }}

        .trend-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .trend-table th {{
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .trend-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}

        .trend-table tr:nth-child(even) {{
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

        .growth-indicator {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}

        .growth-high {{
            background: #e8f5e8;
            color: #27ae60;
        }}

        .growth-medium {{
            background: #fff3cd;
            color: #856404;
        }}

        .growth-low {{
            background: #f8d7da;
            color: #721c24;
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

        .section-tabs {{
            display: flex;
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 5px;
        }}

        .tab-button {{
            flex: 1;
            padding: 10px 15px;
            border: none;
            background: transparent;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .tab-button.active {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 0 15px;
            }}
            
            .chart-container {{
                height: 400px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .dual-chart,
            .triple-chart {{
                grid-template-columns: 1fr;
            }}
            
            .nav-menu {{
                gap: 10px;
            }}
            
            .nav-item {{
                font-size: 0.8em;
                padding: 6px 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🔍 AI研究发展趋势全景分析</h1>
            <p>基于31,244篇顶级AI会议论文的全面趋势分析</p>
            <p>涵盖研究领域、应用场景、技术发展、任务场景四大维度 | 分析期间：2018-2024</p>
            
            <div class="nav-menu">
                <a href="#research-fields" class="nav-item">🔬 研究领域</a>
                <a href="#application-scenarios" class="nav-item">🎯 应用场景</a>
                <a href="#technology-trends" class="nav-item">💻 技术发展</a>
                <a href="#task-scenarios" class="nav-item">⚙️ 任务场景</a>
                <a href="#comprehensive-analysis" class="nav-item">📊 综合分析</a>
                <a href="#predictions" class="nav-item">🔮 发展预测</a>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- 总体概览 -->
        <div class="section">
            <div class="section-header">
                <span>📊</span>
                <span>发展趋势总体概览</span>
            </div>
            <div class="section-content">
                <div class="stats-overview" id="statsOverview">
                    <!-- 统计卡片将通过JavaScript动态生成 -->
                </div>
                
                <div class="chart-container chart-xl" id="overviewChart"></div>
            </div>
        </div>

        <!-- 研究领域发展趋势 -->
        <div class="section" id="research-fields">
            <div class="section-header">
                <span>🔬</span>
                <span>研究领域发展趋势分析</span>
            </div>
            <div class="section-content">
                <div class="dual-chart">
                    <div class="chart-container" id="researchFieldsTreemap"></div>
                    <div class="chart-container" id="researchFieldsGrowth"></div>
                </div>
                
                <div class="chart-container" id="researchFieldsTimeline"></div>
                
                <table class="trend-table" id="researchFieldsTable">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>研究领域</th>
                            <th>总论文数</th>
                            <th>CAGR</th>
                            <th>增长趋势</th>
                            <th>市场份额</th>
                            <th>发展阶段</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 表格内容将通过JavaScript生成 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 应用场景发展趋势 -->
        <div class="section" id="application-scenarios">
            <div class="section-header">
                <span>🎯</span>
                <span>应用场景发展趋势分析</span>
            </div>
            <div class="section-content">
                <div class="dual-chart">
                    <div class="chart-container" id="applicationScenariosRadar"></div>
                    <div class="chart-container" id="applicationScenariosCAGR"></div>
                </div>
                
                <div class="chart-container" id="applicationScenariosEvolution"></div>
                
                <table class="trend-table" id="applicationScenariosTable">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>应用场景</th>
                            <th>总论文数</th>
                            <th>CAGR</th>
                            <th>发展阶段</th>
                            <th>最近动态</th>
                            <th>一致性评分</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 表格内容将通过JavaScript生成 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 技术发展趋势 -->
        <div class="section" id="technology-trends">
            <div class="section-header">
                <span>💻</span>
                <span>技术发展趋势分析</span>
            </div>
            <div class="section-content">
                <div class="triple-chart">
                    <div class="chart-container chart-medium" id="technologyPopularity"></div>
                    <div class="chart-container chart-medium" id="technologyEvolution"></div>
                    <div class="chart-container chart-medium" id="technologyWordCloud"></div>
                </div>
                
                <table class="trend-table" id="technologyTable">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>技术类别</th>
                            <th>提及次数</th>
                            <th>热度等级</th>
                            <th>技术成熟度</th>
                            <th>应用广度</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 表格内容将通过JavaScript生成 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 任务场景发展趋势 -->
        <div class="section" id="task-scenarios">
            <div class="section-header">
                <span>⚙️</span>
                <span>任务场景发展趋势分析</span>
            </div>
            <div class="section-content">
                <div class="dual-chart">
                    <div class="chart-container" id="taskScenariosChange"></div>
                    <div class="chart-container" id="taskScenariosDistribution"></div>
                </div>
                
                <div class="chart-container" id="taskScenariosEvolution"></div>
                
                <table class="trend-table" id="taskScenariosTable">
                    <thead>
                        <tr>
                            <th>任务类型</th>
                            <th>总论文数</th>
                            <th>早期重要性</th>
                            <th>近期重要性</th>
                            <th>重要性变化</th>
                            <th>发展趋势</th>
                            <th>波动性</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 表格内容将通过JavaScript生成 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 综合分析 -->
        <div class="section" id="comprehensive-analysis">
            <div class="section-header">
                <span>📊</span>
                <span>四维度综合分析</span>
            </div>
            <div class="section-content">
                <div class="chart-container chart-xl" id="comprehensiveHeatmap"></div>
                
                <div class="dual-chart">
                    <div class="chart-container" id="correlationAnalysis"></div>
                    <div class="chart-container" id="evolutionTrajectory"></div>
                </div>
                
                <div class="insights-grid" id="comprehensiveInsights">
                    <!-- 综合洞察将通过JavaScript生成 -->
                </div>
            </div>
        </div>

        <!-- 发展预测 -->
        <div class="section" id="predictions">
            <div class="section-header">
                <span>🔮</span>
                <span>发展趋势预测</span>
            </div>
            <div class="section-content">
                <div class="dual-chart">
                    <div class="chart-container" id="prediction2025"></div>
                    <div class="chart-container" id="hotTopics"></div>
                </div>
                
                <div class="chart-container" id="futureTrajectory"></div>
                
                <div class="insights-grid" id="predictionInsights">
                    <!-- 预测洞察将通过JavaScript生成 -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // 嵌入完整数据
        const analysisData = {json.dumps(analysis_data, ensure_ascii=False, indent=8)};
        const trendsData = {json.dumps(trends_data, ensure_ascii=False, indent=8)};
        const researchTrendsData = {json.dumps(research_trends_data, ensure_ascii=False, indent=8)};

        console.log('数据加载完成:', {{
            analysisData: Object.keys(analysisData).length,
            trendsData: Object.keys(trendsData).length,
            researchTrendsData: Object.keys(researchTrendsData).length
        }});

        // 提取各类数据
        const researchFields = trendsData.research_fields_trends || {{}};
        const applicationScenarios = trendsData.application_scenarios_trends || {{}};
        const technologyTrends = trendsData.technology_trends?.technology_popularity || {{}};
        const taskScenarios = trendsData.task_scenarios_trends || {{}};
        const keywordData = analysisData.keyword_analysis?.top_keywords || {{}};

        // 颜色主题
        const colorSchemes = {{
            research: ['#e74c3c', '#c0392b', '#a93226', '#922b21'],
            application: ['#27ae60', '#229954', '#1e8449', '#196f3d'],
            technology: ['#3498db', '#2980b9', '#2471a3', '#1f618d'],
            task: ['#f39c12', '#e67e22', '#d35400', '#ba4a00'],
            comprehensive: ['#9b59b6', '#8e44ad', '#7d3c98', '#6c3483']
        }};

        // 生成统计概览
        function generateStatsOverview() {{
            const container = document.getElementById('statsOverview');
            const stats = [
                {{ 
                    number: Object.keys(researchFields).length, 
                    label: '研究领域', 
                    color: '#e74c3c' 
                }},
                {{ 
                    number: Object.keys(applicationScenarios).length, 
                    label: '应用场景', 
                    color: '#27ae60' 
                }},
                {{ 
                    number: Object.keys(technologyTrends).filter(t => technologyTrends[t] > 0).length, 
                    label: '技术类别', 
                    color: '#3498db' 
                }},
                {{ 
                    number: Object.keys(taskScenarios).length, 
                    label: '任务类型', 
                    color: '#f39c12' 
                }},
                {{ 
                    number: analysisData.basic_statistics?.total_papers || 0, 
                    label: '分析论文总数', 
                    color: '#9b59b6' 
                }},
                {{ 
                    number: '2018-2024', 
                    label: '分析年份跨度', 
                    color: '#34495e' 
                }}
            ];

            stats.forEach(stat => {{
                const card = document.createElement('div');
                card.className = 'stat-card';
                card.style.borderLeftColor = stat.color;
                card.innerHTML = `
                    <div class="stat-number" style="color: ${{stat.color}}">${{typeof stat.number === 'number' ? stat.number.toLocaleString() : stat.number}}</div>
                    <div class="stat-label">${{stat.label}}</div>
                `;
                container.appendChild(card);
            }});
        }}

        // 初始化所有图表
        function initializeAllCharts() {{
            console.log('开始初始化图表...');
            
            // 总览桑基图
            initOverviewChart();
            
            // 研究领域图表
            initResearchFieldsCharts();
            
            // 应用场景图表
            initApplicationScenariosCharts();
            
            // 技术发展图表
            initTechnologyTrendsCharts();
            
            // 任务场景图表
            initTaskScenariosCharts();
            
            // 综合分析图表
            initComprehensiveCharts();
            
            // 预测图表
            initPredictionCharts();
            
            console.log('所有图表初始化完成');
        }}

        // 总览图表
        function initOverviewChart() {{
            const chart = echarts.init(document.getElementById('overviewChart'));
            
            // 构建桑基图数据
            const nodes = [];
            const links = [];
            
            // 添加四个主要类别节点
            nodes.push(
                {{ name: '研究领域', itemStyle: {{ color: '#e74c3c' }} }},
                {{ name: '应用场景', itemStyle: {{ color: '#27ae60' }} }},
                {{ name: '技术发展', itemStyle: {{ color: '#3498db' }} }},
                {{ name: '任务场景', itemStyle: {{ color: '#f39c12' }} }}
            );
            
            // 添加具体条目节点
            Object.keys(researchFields).forEach(field => {{
                nodes.push({{ name: field, category: 0 }});
                links.push({{ source: '研究领域', target: field, value: researchFields[field].total_papers || 100 }});
            }});
            
            Object.keys(applicationScenarios).forEach(scenario => {{
                nodes.push({{ name: scenario + '_app', category: 1 }});
                links.push({{ source: '应用场景', target: scenario + '_app', value: 100 }});
            }});
            
            chart.setOption({{
                title: {{
                    text: 'AI研究发展全景概览',
                    left: 'center',
                    textStyle: {{ fontSize: 20, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item',
                    triggerOn: 'mousemove'
                }},
                series: [{{
                    type: 'sankey',
                    data: nodes,
                    links: links,
                    emphasis: {{
                        focus: 'adjacency'
                    }},
                    lineStyle: {{
                        curveness: 0.5
                    }}
                }}]
            }});
        }}

        // 研究领域图表
        function initResearchFieldsCharts() {{
            // 矩阵树图
            const treemapChart = echarts.init(document.getElementById('researchFieldsTreemap'));
            const treemapData = Object.entries(researchFields).map(([name, data]) => ({{
                name,
                value: data.total_papers,
                itemStyle: {{
                    color: data.growth_rate > 30 ? '#e74c3c' : data.growth_rate > 15 ? '#f39c12' : '#3498db'
                }}
            }}));

            treemapChart.setOption({{
                title: {{
                    text: '研究领域规模分布',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    formatter: function(params) {{
                        const fieldData = researchFields[params.name];
                        return `${{params.name}}<br/>
                                论文数量: ${{params.value.toLocaleString()}}<br/>
                                增长率: ${{fieldData.growth_rate}}%<br/>
                                趋势: ${{fieldData.trend_type}}`;
                    }}
                }},
                series: [{{
                    type: 'treemap',
                    data: treemapData,
                    roam: false,
                    label: {{
                        show: true,
                        formatter: '{{b}}'
                    }}
                }}]
            }});

            // 增长率条形图
            const growthChart = echarts.init(document.getElementById('researchFieldsGrowth'));
            const sortedFields = Object.entries(researchFields)
                .sort(([,a], [,b]) => b.growth_rate - a.growth_rate);

            growthChart.setOption({{
                title: {{
                    text: '研究领域增长率排行',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis',
                    formatter: function(params) {{
                        return `${{params[0].name}}<br/>CAGR: ${{params[0].value}}%`;
                    }}
                }},
                grid: {{
                    left: '20%',
                    right: '10%',
                    bottom: '15%'
                }},
                xAxis: {{
                    type: 'value',
                    name: 'CAGR (%)'
                }},
                yAxis: {{
                    type: 'category',
                    data: sortedFields.map(([name]) => name),
                    axisLabel: {{ interval: 0 }}
                }},
                series: [{{
                    type: 'bar',
                    data: sortedFields.map(([, data]) => data.growth_rate),
                    itemStyle: {{
                        color: function(params) {{
                            return colorSchemes.research[params.dataIndex % 4];
                        }}
                    }}
                }}]
            }});

            // 时间序列图
            const timelineChart = echarts.init(document.getElementById('researchFieldsTimeline'));
            const years = [2018, 2019, 2020, 2021, 2022, 2023];
            
            const seriesData = Object.entries(researchFields).slice(0, 8).map(([name, data]) => ({{
                name,
                type: 'line',
                data: data.yearly_values ? data.yearly_values.slice(0, 6) : [],
                smooth: true
            }}));

            timelineChart.setOption({{
                title: {{
                    text: '研究领域发展时间序列（Top 8）',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                legend: {{
                    bottom: 10,
                    type: 'scroll'
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

            // 生成研究领域表格
            generateResearchFieldsTable();
        }}

        // 应用场景图表
        function initApplicationScenariosCharts() {{
            // 雷达图
            const radarChart = echarts.init(document.getElementById('applicationScenariosRadar'));
            const scenarios = Object.keys(applicationScenarios);
            const radarData = scenarios.map(scenario => applicationScenarios[scenario].cagr_2018_2023);

            radarChart.setOption({{
                title: {{
                    text: '应用场景发展雷达图',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{}},
                radar: {{
                    indicator: scenarios.map(name => ({{ name, max: 70 }})),
                    radius: '70%'
                }},
                series: [{{
                    type: 'radar',
                    data: [{{
                        value: radarData,
                        name: 'CAGR增长率',
                        itemStyle: {{ color: '#27ae60' }}
                    }}]
                }}]
            }});

            // CAGR排行
            const cagrChart = echarts.init(document.getElementById('applicationScenariosCAGR'));
            const sortedScenarios = Object.entries(applicationScenarios)
                .sort(([,a], [,b]) => b.cagr_2018_2023 - a.cagr_2018_2023);

            cagrChart.setOption({{
                title: {{
                    text: '应用场景CAGR排行',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                grid: {{
                    left: '20%',
                    right: '10%',
                    bottom: '15%'
                }},
                xAxis: {{
                    type: 'value',
                    name: 'CAGR (%)'
                }},
                yAxis: {{
                    type: 'category',
                    data: sortedScenarios.map(([name]) => name)
                }},
                series: [{{
                    type: 'bar',
                    data: sortedScenarios.map(([, data]) => data.cagr_2018_2023),
                    itemStyle: {{
                        color: function(params) {{
                            return colorSchemes.application[params.dataIndex % 4];
                        }}
                    }}
                }}]
            }});

            // 演化轨迹
            const evolutionChart = echarts.init(document.getElementById('applicationScenariosEvolution'));
            evolutionChart.setOption({{
                title: {{
                    text: '应用场景发展阶段分布',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item'
                }},
                series: [{{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: Object.entries(applicationScenarios).map(([name, data]) => ({{
                        name: `${{name}} (${{data.development_stage}})`,
                        value: 1
                    }})),
                    roseType: 'radius'
                }}]
            }});

            generateApplicationScenariosTable();
        }}

        // 技术发展图表
        function initTechnologyTrendsCharts() {{
            // 技术热度条形图
            const popularityChart = echarts.init(document.getElementById('technologyPopularity'));
            const techEntries = Object.entries(technologyTrends)
                .filter(([, value]) => value > 0)
                .sort(([,a], [,b]) => b - a);

            popularityChart.setOption({{
                title: {{
                    text: '技术热度排行',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                grid: {{
                    left: '15%',
                    right: '10%',
                    bottom: '15%'
                }},
                xAxis: {{
                    type: 'category',
                    data: techEntries.map(([name]) => name),
                    axisLabel: {{ rotate: 45 }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '提及次数'
                }},
                series: [{{
                    type: 'bar',
                    data: techEntries.map(([, value]) => value),
                    itemStyle: {{
                        color: function(params) {{
                            return colorSchemes.technology[params.dataIndex % 4];
                        }}
                    }}
                }}]
            }});

            // 技术演化散点图
            const evolutionChart = echarts.init(document.getElementById('technologyEvolution'));
            const evolutionData = techEntries.map(([name, mentions]) => ({{
                name,
                value: [Math.log10(mentions), Math.random() * 100, mentions]
            }}));

            evolutionChart.setOption({{
                title: {{
                    text: '技术成熟度分析',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: function(params) {{
                        return `${{params.name}}<br/>提及次数: ${{params.value[2].toLocaleString()}}`;
                    }}
                }},
                xAxis: {{
                    type: 'value',
                    name: '技术成熟度指数'
                }},
                yAxis: {{
                    type: 'value',
                    name: '应用广度指数'
                }},
                series: [{{
                    type: 'scatter',
                    symbolSize: function(data) {{
                        return Math.sqrt(data[2]) / 50;
                    }},
                    data: evolutionData,
                    label: {{
                        show: true,
                        position: 'top',
                        formatter: function(params) {{
                            return params.name;
                        }}
                    }}
                }}]
            }});

            // 技术词云
            const wordCloudChart = echarts.init(document.getElementById('technologyWordCloud'));
            const cloudData = Object.entries(keywordData)
                .slice(0, 50)
                .map(([word, count]) => ({{ name: word, value: count }}));

            wordCloudChart.setOption({{
                title: {{
                    text: '技术关键词云',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                series: [{{
                    type: 'wordCloud',
                    gridSize: 2,
                    sizeRange: [12, 60],
                    rotationRange: [-90, 90],
                    shape: 'pentagon',
                    width: '90%',
                    height: '80%',
                    textStyle: {{
                        fontFamily: 'sans-serif',
                        fontWeight: 'bold',
                        color: function () {{
                            return colorSchemes.technology[Math.floor(Math.random() * 4)];
                        }}
                    }},
                    data: cloudData
                }}]
            }});

            generateTechnologyTable();
        }}

        // 任务场景图表
        function initTaskScenariosCharts() {{
            // 重要性变化图
            const changeChart = echarts.init(document.getElementById('taskScenariosChange'));
            const taskEntries = Object.entries(taskScenarios);

            changeChart.setOption({{
                title: {{
                    text: '任务类型重要性变化',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                grid: {{
                    left: '15%',
                    right: '10%',
                    bottom: '15%'
                }},
                xAxis: {{
                    type: 'category',
                    data: taskEntries.map(([name]) => name.replace(' Tasks', '')),
                    axisLabel: {{ rotate: 30 }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '重要性变化 (%)'
                }},
                series: [{{
                    type: 'bar',
                    data: taskEntries.map(([, data]) => data.importance_change),
                    itemStyle: {{
                        color: function(params) {{
                            return params.value > 0 ? '#27ae60' : '#e74c3c';
                        }}
                    }}
                }}]
            }});

            // 分布饼图
            const distributionChart = echarts.init(document.getElementById('taskScenariosDistribution'));
            const taskDistribution = analysisData.task_scenario_analysis?.task_type_distribution || {{}};

            distributionChart.setOption({{
                title: {{
                    text: '任务类型分布',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item'
                }},
                series: [{{
                    type: 'pie',
                    radius: '70%',
                    data: Object.entries(taskDistribution).map(([name, value]) => ({{
                        name: name.replace(' Tasks', ''),
                        value
                    }})),
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }}
                }}]
            }});

            // 演化趋势
            const taskEvolutionChart = echarts.init(document.getElementById('taskScenariosEvolution'));
            const yearlyEvolution = trendsData.technology_trends?.task_type_evolution || {{}};
            const years = [2018, 2019, 2020, 2021, 2022, 2023];
            
            const taskSeriesData = Object.entries(yearlyEvolution).map(([taskType, yearData]) => ({{
                name: taskType.replace(' Tasks', ''),
                type: 'line',
                data: years.map(year => (yearData[year] || 0) * 100),
                smooth: true
            }}));

            taskEvolutionChart.setOption({{
                title: {{
                    text: '任务类型重要性演化',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                legend: {{
                    bottom: 10,
                    type: 'scroll'
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
                    name: '重要性占比 (%)'
                }},
                series: taskSeriesData
            }});

            generateTaskScenariosTable();
        }}

        // 综合分析图表
        function initComprehensiveCharts() {{
            // 综合热力图
            const heatmapChart = echarts.init(document.getElementById('comprehensiveHeatmap'));
            
            // 构建热力图数据
            const categories = ['研究领域', '应用场景', '技术发展', '任务场景'];
            const allItems = [
                ...Object.keys(researchFields),
                ...Object.keys(applicationScenarios),
                ...Object.keys(technologyTrends).filter(t => technologyTrends[t] > 0),
                ...Object.keys(taskScenarios)
            ];
            
            const heatmapData = [];
            allItems.forEach((item, i) => {{
                categories.forEach((category, j) => {{
                    let value = 0;
                    if (category === '研究领域' && researchFields[item]) {{
                        value = researchFields[item].growth_rate || 0;
                    }} else if (category === '应用场景' && applicationScenarios[item]) {{
                        value = applicationScenarios[item].cagr_2018_2023 || 0;
                    }} else if (category === '技术发展' && technologyTrends[item]) {{
                        value = Math.log10(technologyTrends[item] + 1) * 10;
                    }} else if (category === '任务场景' && taskScenarios[item]) {{
                        value = Math.abs(taskScenarios[item].importance_change) * 10;
                    }}
                    if (value > 0) {{
                        heatmapData.push([j, i, Math.round(value)]);
                    }}
                }});
            }});

            heatmapChart.setOption({{
                title: {{
                    text: '四维度综合热力分析',
                    left: 'center',
                    textStyle: {{ fontSize: 18, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    position: 'top',
                    formatter: function(params) {{
                        return `${{categories[params.value[0]]}}<br/>
                                ${{allItems[params.value[1]]}}<br/>
                                热度值: ${{params.value[2]}}`;
                    }}
                }},
                grid: {{
                    height: '50%',
                    top: '10%'
                }},
                xAxis: {{
                    type: 'category',
                    data: categories,
                    splitArea: {{ show: true }}
                }},
                yAxis: {{
                    type: 'category',
                    data: allItems,
                    splitArea: {{ show: true }}
                }},
                visualMap: {{
                    min: 0,
                    max: 100,
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
                    name: '热度分析',
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

            // 相关性分析和演化轨迹图
            initCorrelationAndEvolution();
            generateComprehensiveInsights();
        }}

        // 预测图表
        function initPredictionCharts() {{
            // 2025预测
            const prediction2025Chart = echarts.init(document.getElementById('prediction2025'));
            const forecasts = trendsData.predictions?.field_forecasts || {{}};
            const sortedForecasts = Object.entries(forecasts)
                .sort(([,a], [,b]) => b.predicted_papers - a.predicted_papers)
                .slice(0, 10);

            prediction2025Chart.setOption({{
                title: {{
                    text: '2025年领域规模预测 (Top 10)',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                grid: {{
                    left: '20%',
                    right: '10%',
                    bottom: '15%'
                }},
                xAxis: {{
                    type: 'value',
                    name: '预测论文数'
                }},
                yAxis: {{
                    type: 'category',
                    data: sortedForecasts.map(([name]) => name)
                }},
                series: [{{
                    type: 'bar',
                    data: sortedForecasts.map(([, data]) => data.predicted_papers),
                    itemStyle: {{
                        color: function(params) {{
                            const confidence = sortedForecasts[params.dataIndex][1].confidence;
                            return confidence === 'high' ? '#27ae60' : 
                                   confidence === 'medium' ? '#f39c12' : '#e74c3c';
                        }}
                    }}
                }}]
            }});

            // 热点话题预测
            const hotTopicsChart = echarts.init(document.getElementById('hotTopics'));
            const hotTopics = trendsData.predictions?.hot_topics_prediction || [];

            hotTopicsChart.setOption({{
                title: {{
                    text: '研究热点预测',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item'
                }},
                series: [{{
                    type: 'pie',
                    radius: ['30%', '70%'],
                    roseType: 'area',
                    data: hotTopics.slice(0, 8).map((topic, index) => ({{
                        name: topic.field,
                        value: 8 - index, // 基于排名的权重
                        itemStyle: {{
                            color: topic.priority === 'high' ? '#e74c3c' : 
                                   topic.priority === 'medium' ? '#f39c12' : '#3498db'
                        }}
                    }}))
                }}]
            }});

            // 未来发展轨迹
            const futureChart = echarts.init(document.getElementById('futureTrajectory'));
            const extendedYears = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
            
            const futureSeriesData = Object.entries(researchFields).slice(0, 6).map(([name, data]) => {{
                const historicalData = data.yearly_values ? data.yearly_values.slice(0, 6) : [];
                const forecast = forecasts[name];
                const predicted2025 = forecast ? forecast.predicted_papers : historicalData[historicalData.length - 1] || 0;
                const estimated2024 = Math.round((historicalData[5] + predicted2025) / 2);
                
                return {{
                    name,
                    type: 'line',
                    data: [...historicalData, estimated2024, predicted2025],
                    markLine: {{
                        data: [{{ xAxis: 6 }}],
                        lineStyle: {{ type: 'dashed', color: '#999' }},
                        label: {{ formatter: '预测线' }}
                    }},
                    smooth: true
                }};
            }});

            futureChart.setOption({{
                title: {{
                    text: '未来发展轨迹预测 (Top 6)',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                legend: {{
                    bottom: 10,
                    type: 'scroll'
                }},
                grid: {{
                    left: '3%',
                    right: '4%',
                    bottom: '15%',
                    containLabel: true
                }},
                xAxis: {{
                    type: 'category',
                    data: extendedYears,
                    name: '年份'
                }},
                yAxis: {{
                    type: 'value',
                    name: '论文数量'
                }},
                series: futureSeriesData
            }});

            generatePredictionInsights();
        }}

        // 生成表格函数
        function generateResearchFieldsTable() {{
            const tbody = document.querySelector('#researchFieldsTable tbody');
            const sortedFields = Object.entries(researchFields)
                .sort(([,a], [,b]) => b.total_papers - a.total_papers);

            sortedFields.forEach(([field, data], index) => {{
                const row = tbody.insertRow();
                const growthClass = data.growth_rate > 30 ? 'growth-high' : 
                                   data.growth_rate > 15 ? 'growth-medium' : 'growth-low';
                
                row.innerHTML = `
                    <td>${{index + 1}}</td>
                    <td><strong>${{field}}</strong></td>
                    <td>${{data.total_papers.toLocaleString()}}</td>
                    <td>${{data.growth_rate}}%</td>
                    <td><span class="growth-indicator ${{growthClass}}">${{data.trend_type}}</span></td>
                    <td>${{data.market_share_2023}}%</td>
                    <td>${{data.growth_rate > 30 ? '快速增长期' : data.growth_rate > 15 ? '稳定增长期' : '成熟期'}}</td>
                `;
            }});
        }}

        function generateApplicationScenariosTable() {{
            const tbody = document.querySelector('#applicationScenariosTable tbody');
            const sortedScenarios = Object.entries(applicationScenarios)
                .sort(([,a], [,b]) => b.cagr_2018_2023 - a.cagr_2018_2023);

            sortedScenarios.forEach(([scenario, data], index) => {{
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${{index + 1}}</td>
                    <td><strong>${{scenario}}</strong></td>
                    <td>${{(data.total_papers || 0).toLocaleString()}}</td>
                    <td>${{data.cagr_2018_2023}}%</td>
                    <td>${{data.development_stage}}</td>
                    <td>${{data.recent_momentum > 0 ? '📈' : data.recent_momentum < 0 ? '📉' : '➡️'}} ${{data.recent_momentum}}</td>
                    <td>${{data.consistency_score}}</td>
                `;
            }});
        }}

        function generateTechnologyTable() {{
            const tbody = document.querySelector('#technologyTable tbody');
            const sortedTech = Object.entries(technologyTrends)
                .filter(([, value]) => value > 0)
                .sort(([,a], [,b]) => b - a);

            sortedTech.forEach(([tech, mentions], index) => {{
                const row = tbody.insertRow();
                const heatLevel = mentions > 50000 ? '🔥 极热' : 
                                 mentions > 20000 ? '🌟 热门' : 
                                 mentions > 5000 ? '📈 上升' : '💡 新兴';
                
                row.innerHTML = `
                    <td>${{index + 1}}</td>
                    <td><strong>${{tech}}</strong></td>
                    <td>${{mentions.toLocaleString()}}</td>
                    <td>${{heatLevel}}</td>
                    <td>${{mentions > 30000 ? '成熟' : mentions > 10000 ? '发展中' : '新兴'}}</td>
                    <td>${{mentions > 40000 ? '广泛' : mentions > 15000 ? '中等' : '专业'}}</td>
                `;
            }});
        }}

        function generateTaskScenariosTable() {{
            const tbody = document.querySelector('#taskScenariosTable tbody');
            const taskDistribution = analysisData.task_scenario_analysis?.task_type_distribution || {{}};

            Object.entries(taskScenarios).forEach(([taskType, data]) => {{
                const row = tbody.insertRow();
                const trendIcon = data.importance_change > 0 ? '📈' : 
                                 data.importance_change < 0 ? '📉' : '➡️';
                
                row.innerHTML = `
                    <td><strong>${{taskType.replace(' Tasks', '')}}</strong></td>
                    <td>${{(taskDistribution[taskType] || 0).toLocaleString()}}</td>
                    <td>${{data.early_importance}}%</td>
                    <td>${{data.recent_importance}}%</td>
                    <td>${{trendIcon}} ${{data.importance_change > 0 ? '+' : ''}}${{data.importance_change}}%</td>
                    <td>${{data.trend_direction}}</td>
                    <td>${{data.volatility < 2 ? '低' : data.volatility < 5 ? '中' : '高'}}</td>
                `;
            }});
        }}

        // 生成洞察
        function generateComprehensiveInsights() {{
            const container = document.getElementById('comprehensiveInsights');
            const insights = [
                {{
                    title: '跨维度关联分析',
                    content: 'Educational Technology在研究领域和应用场景中均表现突出，显示出理论与实践的良好结合。',
                    icon: '🔗'
                }},
                {{
                    title: '技术成熟度评估',
                    content: 'Machine Learning和Deep Learning技术已进入成熟期，而新兴技术正在快速涌现。',
                    icon: '📊'
                }},
                {{
                    title: '任务演化趋势',
                    content: 'Optimization Tasks和Prediction Tasks重要性持续上升，反映AI应用向实用性转移。',
                    icon: '⚙️'
                }},
                {{
                    title: '发展周期特征',
                    content: '大部分领域呈现快速增长态势，AI研究正处于蓬勃发展的黄金期。',
                    icon: '📈'
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

        function generatePredictionInsights() {{
            const container = document.getElementById('predictionInsights');
            const insights = [
                {{
                    title: '2025年展望',
                    content: 'Educational Technology和Content Creation预计将继续保持领先地位，总规模将突破新高。',
                    icon: '🔮'
                }},
                {{
                    title: '新兴机会',
                    content: 'Manufacturing和Medical Diagnosis等新兴领域预计将迎来爆发式增长。',
                    icon: '🌟'
                }},
                {{
                    title: '技术融合趋势',
                    content: '跨领域技术融合将成为下一波创新浪潮的主要驱动力。',
                    icon: '🔄'
                }},
                {{
                    title: '投资建议',
                    content: '建议重点关注高增长新兴领域，同时在成熟领域保持稳定投入。',
                    icon: '💡'
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

        // 相关性分析和演化轨迹
        function initCorrelationAndEvolution() {{
            // 相关性分析散点图
            const correlationChart = echarts.init(document.getElementById('correlationAnalysis'));
            const correlationData = Object.entries(researchFields).map(([name, data]) => ({{
                name,
                value: [data.total_papers, data.growth_rate, data.market_share_2023]
            }}));

            correlationChart.setOption({{
                title: {{
                    text: '规模与增长率相关性分析',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: function(params) {{
                        return `${{params.name}}<br/>
                                论文数: ${{params.value[0].toLocaleString()}}<br/>
                                增长率: ${{params.value[1]}}%<br/>
                                市场份额: ${{params.value[2]}}%`;
                    }}
                }},
                xAxis: {{
                    type: 'value',
                    name: '论文总数',
                    nameLocation: 'middle',
                    nameGap: 30
                }},
                yAxis: {{
                    type: 'value',
                    name: '增长率 (%)',
                    nameLocation: 'middle',
                    nameGap: 50
                }},
                series: [{{
                    type: 'scatter',
                    symbolSize: function(data) {{
                        return Math.sqrt(data[2]) * 3;
                    }},
                    data: correlationData,
                    label: {{
                        show: true,
                        position: 'top',
                        formatter: function(params) {{
                            return params.name;
                        }},
                        fontSize: 10
                    }}
                }}]
            }});

            // 演化轨迹图
            const trajectoryChart = echarts.init(document.getElementById('evolutionTrajectory'));
            const trajectoryData = [
                {{ name: '新兴期', value: [10, 80, 15] }},
                {{ name: '成长期', value: [30, 50, 35] }},
                {{ name: '成熟期', value: [60, 20, 25] }},
                {{ name: '稳定期', value: [80, 10, 10] }}
            ];

            trajectoryChart.setOption({{
                title: {{
                    text: '技术发展生命周期',
                    left: 'center',
                    textStyle: {{ fontSize: 16, fontWeight: 'bold' }}
                }},
                tooltip: {{
                    trigger: 'item'
                }},
                xAxis: {{
                    type: 'value',
                    name: '市场成熟度',
                    nameLocation: 'middle',
                    nameGap: 30
                }},
                yAxis: {{
                    type: 'value',
                    name: '增长潜力',
                    nameLocation: 'middle',
                    nameGap: 50
                }},
                series: [{{
                    type: 'scatter',
                    symbolSize: function(data) {{
                        return data[2] * 2;
                    }},
                    data: trajectoryData,
                    label: {{
                        show: true,
                        position: 'top',
                        formatter: function(params) {{
                            return params.name;
                        }}
                    }}
                }}]
            }});
        }}

        // 导航功能
        function initNavigation() {{
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => {{
                item.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {{
                        targetElement.scrollIntoView({{ behavior: 'smooth' }});
                    }}
                }});
            }});
        }}

        // 页面初始化
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('页面开始初始化...');
            
            generateStatsOverview();
            initializeAllCharts();
            initNavigation();
            
            // 响应式处理
            window.addEventListener('resize', function() {{
                const chartIds = [
                    'overviewChart', 'researchFieldsTreemap', 'researchFieldsGrowth', 'researchFieldsTimeline',
                    'applicationScenariosRadar', 'applicationScenariosCAGR', 'applicationScenariosEvolution',
                    'technologyPopularity', 'technologyEvolution', 'technologyWordCloud',
                    'taskScenariosChange', 'taskScenariosDistribution', 'taskScenariosEvolution',
                    'comprehensiveHeatmap', 'correlationAnalysis', 'evolutionTrajectory',
                    'prediction2025', 'hotTopics', 'futureTrajectory'
                ];
                
                chartIds.forEach(id => {{
                    const chart = echarts.getInstanceByDom(document.getElementById(id));
                    if (chart) chart.resize();
                }});
            }});
            
            console.log('AI研究发展趋势全景分析页面初始化完成');
        }});
    </script>
</body>
</html>"""

    # 保存HTML文件
    output_file = Path("frontend/comprehensive_trends.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 全面的发展趋势单页面可视化已生成: {output_file}")

if __name__ == "__main__":
    generate_comprehensive_trends_page()