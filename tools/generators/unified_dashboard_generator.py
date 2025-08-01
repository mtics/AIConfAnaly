#!/usr/bin/env python3
"""
统一仪表板生成器 - 合并了所有仪表板生成功能
支持研究仪表板、完整数据集仪表板、综合趋势可视化
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import datetime


class UnifiedDashboardGenerator:
    """统一仪表板生成器"""
    
    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        self.data_dir = project_root / "outputs/analysis"
        self.output_dir = project_root / "outputs"
        self.frontend_dir = project_root / "frontend"
        
        # 加载所有可用的分析数据
        self.analysis_data = self.load_all_analysis_data()
    
    def load_all_analysis_data(self) -> Dict[str, Any]:
        """加载所有分析数据"""
        data = {}
        
        # 分析文件映射
        analysis_files = {
            'comprehensive': 'comprehensive_analysis.json',
            'complete_dataset': 'complete_dataset_analysis.json', 
            'quick_analysis': 'quick_keyword_analysis.json',
            'enhanced_analysis': 'enhanced_real_data_analysis.json'
        }
        
        for key, filename in analysis_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data[key] = json.load(f)
                        print(f"✅ 加载 {key}: {filename}")
                except Exception as e:
                    print(f"⚠️ 加载 {filename} 失败: {e}")
        
        return data
    
    def generate_research_dashboard(self) -> str:
        """生成研究仪表板 (基于快速分析数据)"""
        print("📊 生成研究仪表板...")
        
        # 准备数据
        dashboard_data = self.prepare_research_dashboard_data()
        
        # 生成HTML
        html_content = self.create_research_dashboard_html(dashboard_data)
        
        # 保存文件到outputs目录
        output_file = self.output_dir / "research_dashboard.html"
        self._save_dashboard(html_content, output_file)
        
        return str(output_file)
    
    def generate_complete_dashboard(self) -> str:
        """生成完整数据集仪表板"""
        print("📊 生成完整数据集仪表板...")
        
        # 准备数据
        dashboard_data = self.prepare_complete_dashboard_data()
        
        # 生成HTML
        html_content = self.create_complete_dashboard_html(dashboard_data)
        
        # 保存文件
        output_file = self.output_dir / "complete_dashboard.html"
        self._save_dashboard(html_content, output_file)
        
        return str(output_file)
    
    def generate_comprehensive_trends(self) -> str:
        """生成综合趋势可视化"""
        print("📈 生成综合趋势可视化...")
        
        # 准备数据
        trends_data = self.prepare_trends_data()
        
        # 生成HTML
        html_content = self.create_comprehensive_trends_html(trends_data)
        
        # 保存文件到outputs目录
        output_file = self.output_dir / "comprehensive_trends.html"
        self._save_dashboard(html_content, output_file)
        
        return str(output_file)
    
    def generate_all_dashboards(self) -> Dict[str, str]:
        """生成所有类型的仪表板"""
        print("🚀 生成所有统一仪表板...")
        
        results = {}
        
        # 根据可用数据生成相应仪表板
        if 'quick_analysis' in self.analysis_data:
            results['research_dashboard'] = self.generate_research_dashboard()
        
        if 'complete_dataset' in self.analysis_data:
            results['complete_dashboard'] = self.generate_complete_dashboard()
            
        if 'comprehensive' in self.analysis_data:
            results['comprehensive_trends'] = self.generate_comprehensive_trends()
        
        # 生成统一综合仪表板
        results['unified_dashboard'] = self.generate_unified_dashboard()
        
        return results
    
    def generate_unified_dashboard(self) -> str:
        """生成统一综合仪表板（推荐使用）"""
        print("⭐ 生成统一综合仪表板...")
        
        # 整合所有可用数据
        unified_data = self.prepare_unified_data()
        
        # 生成统一HTML
        html_content = self.create_unified_dashboard_html(unified_data)
        
        # 保存文件到outputs目录
        output_file = self.output_dir / "unified_dashboard.html"
        self._save_dashboard(html_content, output_file)
        
        return str(output_file)
    
    def prepare_research_dashboard_data(self) -> Dict[str, Any]:
        """准备研究仪表板数据"""
        quick_data = self.analysis_data.get('quick_analysis', {})
        
        metadata = quick_data.get('metadata', {})
        analysis = quick_data.get('analysis', {})
        
        return {
            'metadata': {
                'total_papers': metadata.get('total_papers_sampled', 0),
                'analysis_date': metadata.get('analysis_timestamp', datetime.datetime.now().isoformat()),
                'conferences': len(analysis.get('conference_keywords', {}))
            },
            'top_keywords': analysis.get('top_overall_keywords', [])[:50],
            'field_distribution': analysis.get('field_distribution', {}),
            'conference_keywords': analysis.get('conference_keywords', {}),
            'yearly_trends': analysis.get('yearly_trends', {})
        }
    
    def prepare_complete_dashboard_data(self) -> Dict[str, Any]:
        """准备完整数据集仪表板数据"""
        complete_data = self.analysis_data.get('complete_dataset', {})
        
        if not complete_data:
            return {}
        
        metadata = complete_data.get('metadata', {})
        
        return {
            'metadata': {
                'papers_analyzed': metadata.get('total_papers_analyzed', 53159),
                'unique_keywords': metadata.get('total_unique_keywords', 0),
                'field_categories': len(complete_data.get('field_definitions', {})),
                'conferences': len(complete_data.get('conference_analysis', {})),
                'years_span': f"2018-2024",
                'analysis_date': metadata.get('analysis_timestamp', datetime.datetime.now().isoformat())
            },
            'top_keywords': complete_data.get('top_overall_keywords', [])[:100],
            'field_distribution': complete_data.get('field_paper_counts', {}),
            'conference_data': {conf: data['papers'] for conf, data in complete_data.get('conference_analysis', {}).items()},
            'yearly_trends': complete_data.get('yearly_trends', {})
        }
    
    def prepare_trends_data(self) -> Dict[str, Any]:
        """准备趋势数据"""
        comprehensive_data = self.analysis_data.get('comprehensive', {})
        
        return {
            'field_trends': comprehensive_data.get('field_analysis', {}).get('field_trends', {}),
            'scenario_trends': comprehensive_data.get('task_scenario_analysis', {}).get('scenario_yearly_trends', {}),
            'technical_trends': comprehensive_data.get('technical_trend_analysis', {}).get('tech_yearly_trends', {}),
            'conference_trends': comprehensive_data.get('conference_analysis', {}).get('yearly_statistics', {})
        }
    
    def prepare_unified_data(self) -> Dict[str, Any]:
        """准备统一数据"""
        # 优先使用comprehensive数据，fallback到其他数据源
        primary_data = self.analysis_data.get('comprehensive', {})
        complete_data = self.analysis_data.get('complete_dataset', {})
        
        if not primary_data and not complete_data:
            return {'error': '没有可用的分析数据'}
        
        # 使用最详细的数据源
        main_source = primary_data if primary_data else complete_data
        
        return {
            'metadata': self._extract_metadata(main_source),
            'basic_statistics': main_source.get('basic_statistics', {}),
            'field_analysis': main_source.get('field_analysis', {}),
            'conference_analysis': main_source.get('conference_analysis', {}),
            'temporal_analysis': main_source.get('temporal_analysis', {}),
            'task_scenario_analysis': main_source.get('task_scenario_analysis', {}),
            'keyword_analysis': main_source.get('keyword_analysis', {}),
            'emerging_trends': main_source.get('emerging_trends', {})
        }
    
    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """提取元数据"""
        basic_stats = data.get('basic_statistics', {})
        
        return {
            'total_papers': basic_stats.get('total_papers', 0),
            'conferences': basic_stats.get('conferences', []),
            'year_range': basic_stats.get('year_range', '2018-2024'),
            'analysis_date': datetime.datetime.now().isoformat(),
            'data_source': 'comprehensive_analysis'
        }
    
    def create_unified_dashboard_html(self, data: Dict[str, Any]) -> str:
        """创建统一仪表板HTML"""
        if 'error' in data:
            return self._create_error_html(data['error'])
        
        return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI会议论文分析 - 统一仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .header {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 20px 0;
            text-align: center;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.1rem;
        }}
        
        .stats-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9rem;
        }}
        
        .dashboard-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .chart-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            margin: 20px 0;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .chart {{
            height: 400px;
            width: 100%;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        
        .tabs {{
            display: flex;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .tab {{
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            background: transparent;
            color: white;
        }}
        
        .tab.active {{
            background: rgba(255,255,255,0.2);
            color: #2c3e50;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI会议论文分析仪表板</h1>
        <p>基于{data['metadata']['total_papers']:,}篇论文的深度分析 | {data['metadata']['year_range']}</p>
    </div>
    
    <div class="stats-overview">
        <div class="stat-card">
            <div class="stat-value">{data['metadata']['total_papers']:,}</div>
            <div class="stat-label">总论文数</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(data['metadata']['conferences'])}</div>
            <div class="stat-label">顶级会议</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(data.get('field_analysis', {}).get('field_distribution', {}))}</div>
            <div class="stat-label">研究领域</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(data.get('task_scenario_analysis', {}).get('scenario_distribution', {}))}</div>
            <div class="stat-label">应用场景</div>
        </div>
    </div>
    
    <div class="dashboard-content">
        <div class="tabs">
            <button class="tab active" onclick="switchTab('overview')">📊 总览</button>
            <button class="tab" onclick="switchTab('fields')">🔬 研究领域</button>
            <button class="tab" onclick="switchTab('scenarios')">🎯 应用场景</button>
            <button class="tab" onclick="switchTab('trends')">📈 发展趋势</button>
            <button class="tab" onclick="switchTab('conferences')">🏛️ 会议分析</button>
        </div>
        
        <!-- 总览标签页 -->
        <div id="overview" class="tab-content active">
            <div class="chart-container">
                <h3 class="section-title">年度发表趋势</h3>
                <div id="yearlyTrend" class="chart"></div>
            </div>
        </div>
        
        <!-- 研究领域标签页 -->
        <div id="fields" class="tab-content">
            <div class="chart-container">
                <h3 class="section-title">研究领域分布</h3>
                <div id="fieldDistribution" class="chart"></div>
            </div>
        </div>
        
        <!-- 应用场景标签页 -->
        <div id="scenarios" class="tab-content">
            <div class="chart-container">
                <h3 class="section-title">应用场景分析</h3>
                <div id="scenarioAnalysis" class="chart"></div>
            </div>
        </div>
        
        <!-- 发展趋势标签页 -->
        <div id="trends" class="tab-content">
            <div class="chart-container">
                <h3 class="section-title">技术发展趋势</h3>
                <div id="techTrends" class="chart"></div>
            </div>
        </div>
        
        <!-- 会议分析标签页 -->
        <div id="conferences" class="tab-content">
            <div class="chart-container">
                <h3 class="section-title">会议贡献分析</h3>
                <div id="conferenceAnalysis" class="chart"></div>
            </div>
        </div>
    </div>
    
    <script>
        // 嵌入数据
        const analysisData = {json.dumps(data, ensure_ascii=False, indent=4)};
        
        // 标签页切换
        function switchTab(tabName) {{
            // 隐藏所有标签页内容
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // 移除所有标签的active类
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的标签页内容
            document.getElementById(tabName).classList.add('active');
            
            // 添加active类到对应标签
            event.target.classList.add('active');
            
            // 初始化对应的图表
            initializeCharts(tabName);
        }}
        
        // 初始化图表
        function initializeCharts(tabName) {{
            switch(tabName) {{
                case 'overview':
                    initYearlyTrend();
                    break;
                case 'fields':
                    initFieldDistribution();
                    break;
                case 'scenarios':
                    initScenarioAnalysis();
                    break;
                case 'trends':
                    initTechTrends();
                    break;
                case 'conferences':
                    initConferenceAnalysis();
                    break;
            }}
        }}
        
        // 年度趋势图
        function initYearlyTrend() {{
            const chart = echarts.init(document.getElementById('yearlyTrend'));
            const temporalData = analysisData.temporal_analysis || {{}};
            
            const option = {{
                title: {{
                    text: '论文发表年度趋势',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                xAxis: {{
                    type: 'category',
                    data: Object.keys(temporalData.yearly_distribution || {{}})
                }},
                yAxis: {{
                    type: 'value'
                }},
                series: [{{
                    data: Object.values(temporalData.yearly_distribution || {{}}),
                    type: 'line',
                    smooth: true,
                    itemStyle: {{
                        color: '#3498db'
                    }}
                }}]
            }};
            
            chart.setOption(option);
        }}
        
        // 研究领域分布图
        function initFieldDistribution() {{
            const chart = echarts.init(document.getElementById('fieldDistribution'));
            const fieldData = analysisData.field_analysis?.field_distribution || {{}};
            
            const data = Object.entries(fieldData).map(([name, value]) => ({{name, value}}));
            
            const option = {{
                title: {{
                    text: '研究领域分布',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item'
                }},
                series: [{{
                    type: 'pie',
                    radius: '50%',
                    data: data,
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
        }}
        
        // 应用场景分析图
        function initScenarioAnalysis() {{
            const chart = echarts.init(document.getElementById('scenarioAnalysis'));
            const scenarioData = analysisData.task_scenario_analysis?.scenario_distribution || {{}};
            
            const option = {{
                title: {{
                    text: '应用场景分布',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis',
                    axisPointer: {{
                        type: 'shadow'
                    }}
                }},
                xAxis: {{
                    type: 'value'
                }},
                yAxis: {{
                    type: 'category',
                    data: Object.keys(scenarioData).slice(0, 10)
                }},
                series: [{{
                    type: 'bar',
                    data: Object.values(scenarioData).slice(0, 10),
                    itemStyle: {{
                        color: '#e74c3c'
                    }}
                }}]
            }};
            
            chart.setOption(option);
        }}
        
        // 技术趋势图
        function initTechTrends() {{
            const chart = echarts.init(document.getElementById('techTrends'));
            
            const option = {{
                title: {{
                    text: '技术发展趋势',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item'
                }},
                series: [{{
                    type: 'wordCloud',
                    data: [],
                    gridSize: 2,
                    sizeRange: [12, 50],
                    rotationRange: [-90, 90],
                    shape: 'pentagon',
                    textStyle: {{
                        normal: {{
                            fontFamily: 'sans-serif',
                            fontWeight: 'bold',
                            color: function () {{
                                return 'rgb(' + [
                                    Math.round(Math.random() * 160),
                                    Math.round(Math.random() * 160),
                                    Math.round(Math.random() * 160)
                                ].join(',') + ')';
                            }}
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
        }}
        
        // 会议分析图
        function initConferenceAnalysis() {{
            const chart = echarts.init(document.getElementById('conferenceAnalysis'));
            const confData = analysisData.conference_analysis?.conference_distribution || {{}};
            
            const option = {{
                title: {{
                    text: '各会议论文贡献',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item'
                }},
                series: [{{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: Object.entries(confData).map(([name, value]) => ({{name, value}})),
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
        }}
        
        // 页面加载时初始化总览图表
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts('overview');
        }});
    </script>
</body>
</html>"""
    
    def create_research_dashboard_html(self, data: Dict[str, Any]) -> str:
        """创建研究仪表板HTML（简化版）"""
        return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>研究仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
</head>
<body>
    <h1>研究仪表板</h1>
    <p>基于 {data['metadata']['total_papers']} 篇论文的分析</p>
    <div id="main" style="width: 100%; height: 400px;"></div>
    
    <script>
        const chart = echarts.init(document.getElementById('main'));
        const data = {json.dumps(data, ensure_ascii=False)};
        // 简化的图表实现
        chart.setOption({{
            title: {{ text: '关键词分布' }},
            series: [{{ type: 'bar', data: [] }}]
        }});
    </script>
</body>
</html>"""
    
    def create_complete_dashboard_html(self, data: Dict[str, Any]) -> str:
        """创建完整数据集仪表板HTML（简化版）"""
        if not data:
            return self._create_error_html("完整数据集不可用")
            
        return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>完整数据集仪表板</title>
</head>
<body>
    <h1>完整数据集仪表板</h1>
    <p>分析了 {data['metadata']['papers_analyzed']:,} 篇论文</p>
    <!-- 简化的完整仪表板内容 -->
</body>
</html>"""
    
    def create_comprehensive_trends_html(self, data: Dict[str, Any]) -> str:
        """创建综合趋势HTML（简化版）"""
        return """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>综合趋势分析</title>
</head>
<body>
    <h1>综合趋势分析</h1>
    <!-- 简化的趋势分析内容 -->
</body>
</html>"""
    
    def _create_error_html(self, error_message: str) -> str:
        """创建错误页面HTML"""
        return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>错误</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            background: #f8f9fa;
        }}
        .error {{ 
            color: #e74c3c; 
            font-size: 1.2rem;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="error">
        <h2>⚠️ 生成仪表板时出错</h2>
        <p>{error_message}</p>
        <p>请检查分析数据是否完整并重新生成。</p>
    </div>
</body>
</html>"""
    
    def _save_dashboard(self, html_content: str, output_path: Path) -> None:
        """保存仪表板文件"""
        try:
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存HTML文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"✅ 仪表板保存至: {output_path}")
        except Exception as e:
            print(f"❌ 保存仪表板失败: {e}")


def main():
    """主函数 - 生成统一仪表板"""
    generator = UnifiedDashboardGenerator()
    results = generator.generate_all_dashboards()
    
    print("\n📊 仪表板生成完成:")
    for dashboard_type, file_path in results.items():
        print(f"  - {dashboard_type}: {file_path}")
    
    return results


if __name__ == "__main__":
    main()