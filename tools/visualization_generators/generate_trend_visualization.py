#!/usr/bin/env python3
"""
生成集成真实趋势数据的可视化页面
"""

import json
from pathlib import Path

def generate_trend_visualization():
    """生成包含真实数据的趋势可视化页面"""
    
    # 读取趋势分析数据
    trend_file = Path("outputs/trend_analysis/trend_analysis_report.json")
    with open(trend_file, 'r', encoding='utf-8') as f:
        trend_data = json.load(f)
    
    # 读取基础分析数据
    analysis_file = Path("outputs/analysis/comprehensive_analysis.json") 
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 读取HTML模板
    template_file = Path("frontend/trend_visualization.html")
    with open(template_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 构建完整的数据对象
    complete_data = {
        'trendAnalysis': trend_data,
        'analysisData': analysis_data,
        'generationTime': trend_data['generation_time']
    }
    
    # 将数据嵌入到HTML中
    data_script = f"""
    <script>
        // 完整的趋势分析数据
        const fullTrendData = {json.dumps(complete_data, ensure_ascii=False, indent=8)};
        
        // 提取关键数据用于可视化
        const researchFieldsData = fullTrendData.trendAnalysis.research_fields_trends;
        const technologyData = fullTrendData.trendAnalysis.technology_trends.technology_popularity;
        const applicationScenariosData = fullTrendData.trendAnalysis.application_scenarios_trends;
        const taskTypesData = fullTrendData.trendAnalysis.task_scenarios_trends;
        const keywordData = fullTrendData.analysisData.keyword_analysis.top_keywords;
        
        console.log('趋势数据已加载:', fullTrendData);
    </script>
    """
    
    # 在</head>之前插入数据脚本
    html_content = html_content.replace('</head>', f'{data_script}\n</head>')
    
    # 更新JavaScript代码以使用真实数据
    js_update = """
        // 使用真实数据更新 trendData 对象
        const trendData = {
            researchFields: researchFieldsData,
            technology: technologyData,
            applicationScenarios: applicationScenariosData,
            taskTypes: taskTypesData,
            keywords: keywordData
        };
    """
    
    # 在initCharts函数之前插入数据更新
    html_content = html_content.replace(
        '// 初始化图表\n        function initCharts() {',
        js_update + '\n\n        // 初始化图表\n        function initCharts() {'
    )
    
    # 保存增强的HTML文件
    output_file = Path("frontend/trend_visualization_enhanced.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 增强版趋势可视化页面已生成: {output_file}")
    
    # 同时创建一个简化的自包含版本
    create_standalone_version(complete_data)

def create_standalone_version(data):
    """创建完全自包含的可视化页面"""
    
    html_content = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI会议论文趋势关键词完整可视化</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }

        .header {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 30px 0;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            font-size: 1.1em;
            color: #666;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .section {
            background: rgba(255,255,255,0.95);
            margin-bottom: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .section-header {
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
        }

        .section-content {
            padding: 30px;
        }

        .chart-container {
            width: 100%;
            height: 500px;
            margin-bottom: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .chart-large {
            height: 600px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border-left: 5px solid #3498db;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .stat-label {
            color: #666;
            font-size: 1em;
            font-weight: 500;
        }

        .keyword-cloud {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 25px 0;
        }

        .keyword-tag {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 10px 18px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }

        .keyword-tag:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        }

        .keyword-tag.hot {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
        }

        .keyword-tag.medium {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
        }

        .keyword-tag.emerging {
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
        }

        .legend {
            display: flex;
            gap: 20px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255,255,255,0.8);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .legend-color {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        @media (max-width: 768px) {
            .container {
                padding: 0 15px;
            }
            
            .chart-container {
                height: 350px;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🔍 AI会议论文趋势关键词完整可视化</h1>
            <p>基于31,244篇顶级AI会议论文的深度趋势关键词分析（2018-2024）</p>
        </div>
    </div>

    <div class="container">
        <!-- 概览统计 -->
        <div class="section">
            <div class="section-header">📊 关键词趋势概览</div>
            <div class="section-content">
                <div class="stats-grid" id="statsGrid">
                    <!-- 统计卡片将通过JavaScript动态生成 -->
                </div>
            </div>
        </div>

        <!-- 研究领域关键词 -->
        <div class="section">
            <div class="section-header">🔬 研究领域趋势关键词</div>
            <div class="section-content">
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);"></div>
                        <span>强劲增长 (>100%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);"></div>
                        <span>稳步增长 (50-100%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);"></div>
                        <span>基本稳定 (<50%)</span>
                    </div>
                </div>
                
                <div class="chart-container chart-large" id="researchFieldsChart"></div>
                <div class="keyword-cloud" id="researchFieldsKeywords"></div>
            </div>
        </div>

        <!-- 技术趋势关键词 -->
        <div class="section">
            <div class="section-header">💻 技术发展趋势关键词</div>
            <div class="section-content">
                <div class="chart-container" id="technologyChart"></div>
                <div class="keyword-cloud" id="technologyKeywords"></div>
            </div>
        </div>

        <!-- 应用场景趋势关键词 -->
        <div class="section">
            <div class="section-header">🎯 应用场景趋势关键词</div>
            <div class="section-content">
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%);"></div>
                        <span>新兴领域</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);"></div>
                        <span>波动调整</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);"></div>
                        <span>成熟稳定</span>
                    </div>
                </div>
                
                <div class="chart-container" id="applicationScenariosChart"></div>
                <div class="keyword-cloud" id="applicationScenariosKeywords"></div>
            </div>
        </div>

        <!-- 任务类型演化趋势 -->
        <div class="section">
            <div class="section-header">⚙️ 任务类型演化趋势关键词</div>
            <div class="section-content">
                <div class="chart-container" id="taskTypesChart"></div>
                <div class="keyword-cloud" id="taskTypesKeywords"></div>
            </div>
        </div>

        <!-- 关键词词云热力图 -->
        <div class="section">
            <div class="section-header">🌟 研究热词云图</div>
            <div class="section-content">
                <div class="chart-container chart-large" id="wordCloudChart"></div>
            </div>
        </div>
    </div>

    <script>
        // 嵌入完整的趋势数据
        const fullData = """ + json.dumps(data, ensure_ascii=False, indent=8) + """;

        // 提取各类数据
        const researchFields = fullData.trendAnalysis.research_fields_trends;
        const technologies = fullData.trendAnalysis.technology_trends.technology_popularity;
        const applications = fullData.trendAnalysis.application_scenarios_trends;
        const taskTypes = fullData.trendAnalysis.task_scenarios_trends;
        const topKeywords = fullData.analysisData.keyword_analysis.top_keywords;

        // 颜色主题
        const colorThemes = {
            强劲增长: ['#e74c3c', '#c0392b'],
            稳步增长: ['#f39c12', '#e67e22'], 
            基本稳定: ['#3498db', '#2980b9'],
            新兴领域: ['#27ae60', '#229954'],
            波动调整: ['#3498db', '#2980b9'],
            成熟稳定: ['#95a5a6', '#7f8c8d']
        };

        // 生成统计卡片
        function generateStatsCards() {
            const statsGrid = document.getElementById('statsGrid');
            const stats = [
                { number: Object.keys(topKeywords).length.toLocaleString(), label: '分析关键词总数' },
                { number: Object.keys(researchFields).length, label: '研究领域' },
                { number: Object.keys(technologies).filter(t => technologies[t] > 0).length, label: '技术类别' },
                { number: Object.keys(applications).length, label: '应用场景' },
                { number: Object.keys(taskTypes).length, label: '任务类型' },
                { number: fullData.analysisData.basic_statistics.total_papers.toLocaleString(), label: '分析论文总数' }
            ];

            stats.forEach(stat => {
                const card = document.createElement('div');
                card.className = 'stat-card';
                card.innerHTML = `
                    <div class="stat-number">${stat.number}</div>
                    <div class="stat-label">${stat.label}</div>
                `;
                statsGrid.appendChild(card);
            });
        }

        // 初始化所有图表
        function initializeCharts() {
            // 研究领域矩阵树图
            const researchChart = echarts.init(document.getElementById('researchFieldsChart'));
            const researchData = Object.entries(researchFields).map(([name, data]) => ({
                name,
                value: data.total_papers,
                growth: data.growth_rate,
                trend: data.trend_type
            }));

            researchChart.setOption({
                title: {
                    text: '研究领域发展趋势矩阵',
                    left: 'center',
                    textStyle: { fontSize: 18, fontWeight: 'bold' }
                },
                tooltip: {
                    trigger: 'item',
                    formatter: function(params) {
                        return `${params.name}<br/>
                                论文数量: ${params.value.toLocaleString()}<br/>
                                增长率: ${params.data.growth}%<br/>
                                发展趋势: ${params.data.trend}`;
                    }
                },
                series: [{
                    type: 'treemap',
                    data: researchData.map(item => ({
                        ...item,
                        itemStyle: {
                            color: item.growth > 100 ? '#e74c3c' : item.growth > 50 ? '#f39c12' : '#3498db'
                        }
                    })),
                    roam: false,
                    label: {
                        show: true,
                        formatter: '{b}\\n{c}'
                    }
                }]
            });

            // 技术热度条形图
            const techChart = echarts.init(document.getElementById('technologyChart'));
            const techData = Object.entries(technologies)
                .filter(([_, value]) => value > 0)
                .sort(([,a], [,b]) => b - a);

            techChart.setOption({
                title: {
                    text: '技术关键词热度排行',
                    left: 'center',
                    textStyle: { fontSize: 18, fontWeight: 'bold' }
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function(params) {
                        return `${params[0].name}<br/>提及次数: ${params[0].value.toLocaleString()}`;
                    }
                },
                grid: {
                    left: '15%',
                    right: '10%',
                    bottom: '15%'
                },
                xAxis: {
                    type: 'category',
                    data: techData.map(([name]) => name),
                    axisLabel: { rotate: 45, interval: 0 }
                },
                yAxis: {
                    type: 'value',
                    name: '提及次数'
                },
                series: [{
                    type: 'bar',
                    data: techData.map(([_, value]) => value),
                    itemStyle: {
                        color: function(params) {
                            const colors = ['#e74c3c', '#f39c12', '#3498db', '#27ae60', '#9b59b6', '#1abc9c'];
                            return colors[params.dataIndex % colors.length];
                        }
                    }
                }]
            });

            // 应用场景雷达图
            const appChart = echarts.init(document.getElementById('applicationScenariosChart'));
            const appData = Object.entries(applications);
            
            appChart.setOption({
                title: {
                    text: '应用场景发展雷达图',
                    left: 'center',
                    textStyle: { fontSize: 18, fontWeight: 'bold' }
                },
                tooltip: {},
                radar: {
                    indicator: appData.map(([name, data]) => ({
                        name: name,
                        max: 70
                    }))
                },
                series: [{
                    type: 'radar',
                    data: [{
                        value: appData.map(([_, data]) => data.cagr_2018_2023),
                        name: 'CAGR增长率',
                        itemStyle: { color: '#3498db' }
                    }]
                }]
            });

            // 任务类型变化图
            const taskChart = echarts.init(document.getElementById('taskTypesChart'));
            const taskData = Object.entries(taskTypes);
            
            taskChart.setOption({
                title: {
                    text: '任务类型重要性变化趋势',
                    left: 'center',
                    textStyle: { fontSize: 18, fontWeight: 'bold' }
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function(params) {
                        const value = params[0].value;
                        const trend = value > 0 ? '上升' : value < 0 ? '下降' : '稳定';
                        return `${params[0].name}<br/>变化: ${value > 0 ? '+' : ''}${value.toFixed(2)}% (${trend})`;
                    }
                },
                xAxis: {
                    type: 'category',
                    data: taskData.map(([name]) => name.replace(' Tasks', '')),
                    axisLabel: { rotate: 30, interval: 0 }
                },
                yAxis: {
                    type: 'value',
                    name: '重要性变化 (%)'
                },
                series: [{
                    type: 'line',
                    data: taskData.map(([_, data]) => data.importance_change),
                    itemStyle: {
                        color: function(params) {
                            return params.value > 0 ? '#27ae60' : '#e74c3c';
                        }
                    },
                    lineStyle: { width: 3 },
                    symbolSize: 8
                }]
            });

            // 关键词词云
            const wordCloudChart = echarts.init(document.getElementById('wordCloudChart'));
            const cloudData = Object.entries(topKeywords)
                .slice(0, 100)
                .map(([word, count]) => ({
                    name: word,
                    value: count
                }));

            wordCloudChart.setOption({
                title: {
                    text: '研究热词云图 (Top 100)',
                    left: 'center',
                    textStyle: { fontSize: 18, fontWeight: 'bold' }
                },
                tooltip: {
                    formatter: function(params) {
                        return `${params.name}: ${params.value.toLocaleString()} 次`;
                    }
                },
                series: [{
                    type: 'wordCloud',
                    gridSize: 2,
                    sizeRange: [12, 60],
                    rotationRange: [-90, 90],
                    shape: 'pentagon',
                    width: '90%',
                    height: '80%',
                    drawOutOfBound: true,
                    textStyle: {
                        fontFamily: 'sans-serif',
                        fontWeight: 'bold',
                        color: function () {
                            const colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6', '#1abc9c'];
                            return colors[Math.floor(Math.random() * colors.length)];
                        }
                    },
                    emphasis: {
                        textStyle: {
                            shadowBlur: 10,
                            shadowColor: '#333'
                        }
                    },
                    data: cloudData
                }]
            });
        }

        // 生成关键词标签
        function generateKeywordTags() {
            // 研究领域关键词
            const researchContainer = document.getElementById('researchFieldsKeywords');
            Object.entries(researchFields).forEach(([name, data]) => {
                const tag = document.createElement('span');
                tag.className = `keyword-tag ${data.growth_rate > 100 ? 'hot' : data.growth_rate > 50 ? 'medium' : ''}`;
                tag.textContent = `${name} (${data.growth_rate}%)`;
                tag.title = `论文数: ${data.total_papers.toLocaleString()}, 趋势: ${data.trend_type}`;
                researchContainer.appendChild(tag);
            });

            // 技术关键词
            const techContainer = document.getElementById('technologyKeywords');
            Object.entries(technologies)
                .filter(([_, value]) => value > 0)
                .sort(([,a], [,b]) => b - a)
                .forEach(([name, value]) => {
                    const tag = document.createElement('span');
                    tag.className = `keyword-tag ${value > 50000 ? 'hot' : value > 20000 ? 'medium' : ''}`;
                    tag.textContent = `${name} (${value.toLocaleString()})`;
                    techContainer.appendChild(tag);
                });

            // 应用场景关键词
            const appContainer = document.getElementById('applicationScenariosKeywords');
            Object.entries(applications).forEach(([name, data]) => {
                const tag = document.createElement('span');
                tag.className = `keyword-tag ${data.development_stage === '新兴领域' ? 'emerging' : 'medium'}`;
                tag.textContent = `${name} (CAGR: ${data.cagr_2018_2023}%)`;
                tag.title = `发展阶段: ${data.development_stage}`;
                appContainer.appendChild(tag);
            });

            // 任务类型关键词
            const taskContainer = document.getElementById('taskTypesKeywords');
            Object.entries(taskTypes).forEach(([name, data]) => {
                const tag = document.createElement('span');
                const change = data.importance_change;
                tag.className = `keyword-tag ${change > 1 ? 'emerging' : change < -1 ? 'hot' : 'medium'}`;
                const trend = change > 0 ? '↗' : change < 0 ? '↘' : '→';
                tag.innerHTML = `${name.replace(' Tasks', '')} ${trend} (${change > 0 ? '+' : ''}${change.toFixed(1)}%)`;
                taskContainer.appendChild(tag);
            });
        }

        // 页面初始化
        document.addEventListener('DOMContentLoaded', function() {
            generateStatsCards();
            initializeCharts();
            generateKeywordTags();
            
            // 响应式处理
            window.addEventListener('resize', function() {
                const charts = ['researchFieldsChart', 'technologyChart', 'applicationScenariosChart', 
                               'taskTypesChart', 'wordCloudChart'];
                charts.forEach(chartId => {
                    const chart = echarts.getInstanceByDom(document.getElementById(chartId));
                    if (chart) chart.resize();
                });
            });
            
            console.log('趋势可视化页面初始化完成');
        });
    </script>
</body>
</html>"""
    
    # 保存自包含版本
    standalone_file = Path("frontend/keywords_visualization.html")
    with open(standalone_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 自包含关键词可视化页面已生成: {standalone_file}")

if __name__ == "__main__":
    generate_trend_visualization()