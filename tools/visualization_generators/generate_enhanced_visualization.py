#!/usr/bin/env python3
"""
生成增强版单页面可视化
结合详细细化分析的深度可视化页面
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class EnhancedVisualizationGenerator:
    """增强版可视化生成器"""
    
    def __init__(self):
        self.frontend_dir = Path("frontend")
        self.frontend_dir.mkdir(exist_ok=True)
        
        # 加载所有数据
        self.load_all_data()
    
    def load_all_data(self):
        """加载所有分析数据"""
        # 基础分析数据
        with open("outputs/analysis/comprehensive_analysis.json", 'r', encoding='utf-8') as f:
            self.analysis_data = json.load(f)
        
        # 趋势分析数据
        with open("outputs/trend_analysis/trend_analysis_report.json", 'r', encoding='utf-8') as f:
            self.trends_data = json.load(f)
        
        # 研究趋势数据
        with open("outputs/research_trends/research_trends_analysis.json", 'r', encoding='utf-8') as f:
            self.research_trends_data = json.load(f)
        
        # 详细分析数据
        with open("outputs/detailed_analysis/detailed_comprehensive_analysis.json", 'r', encoding='utf-8') as f:
            self.detailed_data = json.load(f)
    
    def generate_enhanced_visualization(self):
        """生成增强版可视化页面"""
        print("🎨 生成增强版可视化页面...")
        
        # 整合所有数据
        integrated_data = self.integrate_all_data()
        
        # 生成HTML页面
        html_content = self.create_enhanced_html(integrated_data)
        
        # 保存文件
        output_file = self.frontend_dir / "enhanced_comprehensive_analysis.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 增强版可视化页面已生成: {output_file}")
        return output_file
    
    def integrate_all_data(self) -> Dict[str, Any]:
        """整合所有数据"""
        return {
            'basic_analysis': self.analysis_data,
            'trends_analysis': self.trends_data,
            'research_trends': self.research_trends_data,
            'detailed_analysis': self.detailed_data,
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_papers': 31244,
            'years_span': "2018-2024",
            'conferences': ['NeuRIPS', 'ICLR', 'AAAI', 'ICML', 'IJCAI']
        }
    
    def create_enhanced_html(self, data: Dict[str, Any]) -> str:
        """创建增强版HTML页面"""
        return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI研究深度分析 - 增强版全景可视化</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .header h1 {{
            font-size: 2.2em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }}

        .header-stats {{
            display: flex;
            gap: 30px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #666;
        }}

        .nav-menu {{
            background: rgba(255, 255, 255, 0.9);
            padding: 15px 0;
            position: sticky;
            top: 90px;
            z-index: 999;
            border-bottom: 1px solid #e0e0e0;
        }}

        .nav-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .nav-item {{
            padding: 8px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 20px;
            font-size: 0.9em;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .nav-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}

        .section-title {{
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .subsection {{
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        .subsection-title {{
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #2c3e50;
            font-weight: 600;
        }}

        .chart-container {{
            width: 100%;
            height: 500px;
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .chart-container.large {{
            height: 600px;
        }}

        .chart-container.small {{
            height: 400px;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .insight-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }}

        .insight-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .insight-content {{
            font-size: 0.95em;
            line-height: 1.6;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .data-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}

        .data-table tr:hover {{
            background: #f8f9fa;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}

        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 0.9em;
            color: #666;
        }}

        .trend-indicator {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .trend-up {{ background: #e8f5e8; color: #2e7d32; }}
        .trend-down {{ background: #ffebee; color: #c62828; }}
        .trend-stable {{ background: #fff3e0; color: #f57c00; }}

        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }}

        @media (max-width: 768px) {{
            .header-content {{
                flex-direction: column;
                gap: 20px;
            }}

            .header-stats {{
                gap: 20px;
            }}

            .nav-content {{
                gap: 10px;
            }}

            .grid {{
                grid-template-columns: 1fr;
            }}

            .chart-container {{
                height: 400px;
            }}

            .metric-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        .fade-in {{
            animation: fadeIn 0.8s ease-in;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <!-- 头部区域 -->
    <div class="header">
        <div class="header-content">
            <h1>🔍 AI研究深度分析 - 增强版全景可视化</h1>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{data['total_papers']:,}</div>
                    <div class="stat-label">分析论文</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">5</div>
                    <div class="stat-label">顶级会议</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">7</div>
                    <div class="stat-label">年份跨度</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">4</div>
                    <div class="stat-label">分析维度</div>
                </div>
            </div>
        </div>
    </div>

    <!-- 导航菜单 -->
    <div class="nav-menu">
        <div class="nav-content">
            <a href="#overview" class="nav-item">📊 总览仪表板</a>
            <a href="#research-fields" class="nav-item">🔬 研究领域深度分析</a>
            <a href="#applications" class="nav-item">🎯 应用场景分析</a>
            <a href="#technology" class="nav-item">💻 技术发展分析</a>
            <a href="#tasks" class="nav-item">⚙️ 任务场景分析</a>
            <a href="#insights" class="nav-item">💡 深度洞察</a>
            <a href="#predictions" class="nav-item">🔮 发展预测</a>
        </div>
    </div>

    <div class="container">
        <!-- 总览仪表板 -->
        <section id="overview" class="section fade-in">
            <h2 class="section-title">📊 总览仪表板</h2>
            
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">11</div>
                    <div class="metric-label">研究领域</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">10</div>
                    <div class="metric-label">应用场景</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">8</div>
                    <div class="metric-label">技术类别</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">6</div>
                    <div class="metric-label">任务类型</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">58.5%</div>
                    <div class="metric-label">最高增长率</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">82K+</div>
                    <div class="metric-label">ML技术提及</div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🌟 核心发现</h3>
                <div class="grid">
                    <div class="insight-card">
                        <div class="insight-title">🚀 Manufacturing领域异军突起</div>
                        <div class="insight-content">年复合增长率达58.5%，展现巨大发展潜力，预计将成为AI应用的下一个爆发点。</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">👑 Educational Technology稳居领导地位</div>
                        <div class="insight-content">累计10,071篇论文，27.6%的稳定增长率，在AI教育应用领域持续主导。</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">💡 生成式AI快速发展</div>
                        <div class="insight-content">Generation Tasks重要性上升0.64%，技术成熟度快速提升，商业化应用前景广阔。</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">🔗 技术融合趋势明显</div>
                        <div class="insight-content">跨学科研究增多，AI+Vision、AI+Language等融合模式日趋成熟。</div>
                    </div>
                </div>
            </div>

            <div class="chart-container large">
                <div id="overviewSankey"></div>
            </div>
        </section>

        <!-- 研究领域深度分析 -->
        <section id="research-fields" class="section fade-in">
            <h2 class="section-title">🔬 研究领域深度分析</h2>
            
            <div class="subsection">
                <h3 class="subsection-title">📈 领域分类体系</h3>
                <div class="chart-container">
                    <div id="fieldCategoriesChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🎯 研究成熟度分析</h3>
                <div class="grid">
                    <div class="chart-container small">
                        <div id="maturityScoreChart"></div>
                    </div>
                    <div class="chart-container small">
                        <div id="innovationIndexChart"></div>
                    </div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🔗 跨学科连接分析</h3>
                <div class="chart-container">
                    <div id="interdisciplinaryChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">📊 详细数据表</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>研究领域</th>
                            <th>论文数量</th>
                            <th>CAGR</th>
                            <th>成熟度</th>
                            <th>创新指数</th>
                            <th>发展阶段</th>
                        </tr>
                    </thead>
                    <tbody id="researchFieldsTable">
                    </tbody>
                </table>
            </div>
        </section>

        <!-- 应用场景分析 -->
        <section id="applications" class="section fade-in">
            <h2 class="section-title">🎯 应用场景深度分析</h2>
            
            <div class="subsection">
                <h3 class="subsection-title">🔄 场景生命周期分析</h3>
                <div class="chart-container">
                    <div id="lifecycleChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">📊 市场渗透度与技术就绪度</h3>
                <div class="grid">
                    <div class="chart-container small">
                        <div id="marketPenetrationChart"></div>
                    </div>
                    <div class="chart-container small">
                        <div id="technicalReadinessChart"></div>
                    </div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">💼 商业影响分析</h3>
                <div class="chart-container">
                    <div id="businessImpactChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🏭 行业分布分析</h3>
                <div class="chart-container">
                    <div id="industryDistributionChart"></div>
                </div>
            </div>
        </section>

        <!-- 技术发展分析 -->
        <section id="technology" class="section fade-in">
            <h2 class="section-title">💻 技术发展深度分析</h2>
            
            <div class="subsection">
                <h3 class="subsection-title">🏗️ 技术分类体系</h3>
                <div class="chart-container">
                    <div id="techTaxonomyChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🔄 创新周期分析</h3>
                <div class="grid">
                    <div class="chart-container small">
                        <div id="innovationCycleChart"></div>
                    </div>
                    <div class="chart-container small">
                        <div id="technologyMaturityChart"></div>
                    </div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🔗 技术融合分析</h3>
                <div class="chart-container">
                    <div id="convergenceChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🔥 研究热点识别</h3>
                <div class="chart-container">
                    <div id="researchHotspotsChart"></div>
                </div>
            </div>
        </section>

        <!-- 任务场景分析 -->
        <section id="tasks" class="section fade-in">
            <h2 class="section-title">⚙️ 任务场景深度分析</h2>
            
            <div class="subsection">
                <h3 class="subsection-title">🧠 任务复杂度分析</h3>
                <div class="chart-container">
                    <div id="taskComplexityChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🤖 自动化就绪度</h3>
                <div class="grid">
                    <div class="chart-container small">
                        <div id="automationReadinessChart"></div>
                    </div>
                    <div class="chart-container small">
                        <div id="humanAiCollaborationChart"></div>
                    </div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">⚖️ 伦理考量分析</h3>
                <div class="chart-container">
                    <div id="ethicalConsiderationsChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">📈 性能指标与资源需求</h3>
                <div class="grid">
                    <div class="chart-container small">
                        <div id="performanceMetricsChart"></div>
                    </div>
                    <div class="chart-container small">
                        <div id="resourceRequirementsChart"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 深度洞察 -->
        <section id="insights" class="section fade-in">
            <h2 class="section-title">💡 深度洞察</h2>
            
            <div class="subsection">
                <h3 class="subsection-title">🎯 融合机会识别</h3>
                <div class="chart-container">
                    <div id="convergenceOpportunitiesChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🚀 创新热点预测</h3>
                <div class="grid">
                    <div class="insight-card">
                        <div class="insight-title">多模态AI融合</div>
                        <div class="insight-content">计算机视觉、自然语言处理与理解任务的深度融合，创新评分85分</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">自主系统发展</div>
                        <div class="insight-content">自动驾驶、强化学习与优化任务结合，创新评分80分</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">智能制造突破</div>
                        <div class="insight-content">制造业AI、优化技术与预测任务融合，潜力巨大</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">生成式AI应用</div>
                        <div class="insight-content">内容创作、生成模型与创作任务深度结合</div>
                    </div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">💰 投资优先级分析</h3>
                <div class="chart-container">
                    <div id="investmentPriorityChart"></div>
                </div>
            </div>
        </section>

        <!-- 发展预测 -->
        <section id="predictions" class="section fade-in">
            <h2 class="section-title">🔮 发展预测</h2>
            
            <div class="subsection">
                <h3 class="subsection-title">📅 短期趋势预测 (2024-2025)</h3>
                <div class="chart-container">
                    <div id="shortTermTrendsChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🎯 中期发展预测 (2025-2027)</h3>
                <div class="chart-container">
                    <div id="mediumTermTrendsChart"></div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">🌟 长期愿景 (2027+)</h3>
                <div class="grid">
                    <div class="insight-card">
                        <div class="insight-title">人机融合智能</div>
                        <div class="insight-content">概率40%，革命性影响，人类智能与AI深度融合</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">自我进化AI</div>
                        <div class="insight-content">概率30%，革命性影响，AI系统自主学习和进化</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">意识AI</div>
                        <div class="insight-content">概率20%，革命性影响，具备意识的人工智能系统</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">量子机器学习</div>
                        <div class="insight-content">概率45%，中等影响，量子计算与机器学习结合</div>
                    </div>
                </div>
            </div>

            <div class="subsection">
                <h3 class="subsection-title">📊 2025年领域规模预测</h3>
                <div class="chart-container">
                    <div id="prediction2025Chart"></div>
                </div>
            </div>
        </section>
    </div>

    <script>
        // 嵌入所有数据
        const allData = {json.dumps(data, ensure_ascii=False, indent=8)};
        
        // 初始化所有图表
        document.addEventListener('DOMContentLoaded', function() {{
            initializeAllCharts();
            setupNavigation();
            populateDataTables();
        }});

        function initializeAllCharts() {{
            // 总览桑基图
            initOverviewSankey();
            
            // 研究领域图表
            initFieldCategoriesChart();
            initMaturityScoreChart();
            initInnovationIndexChart();
            initInterdisciplinaryChart();
            
            // 应用场景图表
            initLifecycleChart();
            initMarketPenetrationChart();
            initTechnicalReadinessChart();
            initBusinessImpactChart();
            initIndustryDistributionChart();
            
            // 技术发展图表
            initTechTaxonomyChart();
            initInnovationCycleChart();
            initTechnologyMaturityChart();
            initConvergenceChart();
            initResearchHotspotsChart();
            
            // 任务场景图表
            initTaskComplexityChart();
            initAutomationReadinessChart();
            initHumanAiCollaborationChart();
            initEthicalConsiderationsChart();
            initPerformanceMetricsChart();
            initResourceRequirementsChart();
            
            // 深度洞察图表
            initConvergenceOpportunitiesChart();
            initInvestmentPriorityChart();
            
            // 预测图表
            initShortTermTrendsChart();
            initMediumTermTrendsChart();
            initPrediction2025Chart();
        }}

        function initOverviewSankey() {{
            const chart = echarts.init(document.getElementById('overviewSankey'));
            
            const option = {{
                title: {{
                    text: '四维度数据流向全景',
                    left: 'center',
                    textStyle: {{
                        fontSize: 18,
                        fontWeight: 'bold'
                    }}
                }},
                tooltip: {{
                    trigger: 'item',
                    triggerOn: 'mousemove'
                }},
                series: [{{
                    type: 'sankey',
                    layout: 'none',
                    emphasis: {{
                        focus: 'adjacency'
                    }},
                    data: [
                        {{name: '研究领域'}},
                        {{name: '应用场景'}},
                        {{name: '技术发展'}},
                        {{name: '任务场景'}},
                        {{name: 'Educational Technology'}},
                        {{name: 'Content Creation'}},
                        {{name: 'Machine Learning'}},
                        {{name: 'Deep Learning'}},
                        {{name: 'Classification Tasks'}},
                        {{name: 'Generation Tasks'}}
                    ],
                    links: [
                        {{source: '研究领域', target: 'Educational Technology', value: 10071}},
                        {{source: '研究领域', target: 'Content Creation', value: 8342}},
                        {{source: '应用场景', target: 'Educational Technology', value: 10071}},
                        {{source: '应用场景', target: 'Content Creation', value: 8342}},
                        {{source: '技术发展', target: 'Machine Learning', value: 82393}},
                        {{source: '技术发展', target: 'Deep Learning', value: 49199}},
                        {{source: '任务场景', target: 'Classification Tasks', value: 3694}},
                        {{source: '任务场景', target: 'Generation Tasks', value: 3677}}
                    ],
                    lineStyle: {{
                        color: 'gradient',
                        curveness: 0.5
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initFieldCategoriesChart() {{
            const chart = echarts.init(document.getElementById('fieldCategoriesChart'));
            
            const fieldCategories = allData.detailed_analysis.detailed_research_fields.field_categories;
            const data = Object.keys(fieldCategories).map(category => ({{
                name: category,
                value: fieldCategories[category].total_papers,
                growth_rate: fieldCategories[category].avg_growth_rate
            }}));

            const option = {{
                title: {{
                    text: '研究领域分类体系',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>论文数: {{c}}<br/>平均增长率: {{d}}%'
                }},
                series: [{{
                    type: 'treemap',
                    data: data.map(item => ({{
                        name: item.name,
                        value: item.value,
                        itemStyle: {{
                            color: `hsl(${{Math.random() * 360}}, 70%, 60%)`
                        }}
                    }}))
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initMaturityScoreChart() {{
            const chart = echarts.init(document.getElementById('maturityScoreChart'));
            
            const maturityData = allData.detailed_analysis.detailed_research_fields.research_maturity;
            const data = Object.keys(maturityData).map(field => ({{
                name: field,
                value: maturityData[field].maturity_score,
                level: maturityData[field].maturity_level
            }}));

            const option = {{
                title: {{
                    text: '研究成熟度评分',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>成熟度评分: {{c}}<br/>成熟度等级: {{d}}'
                }},
                xAxis: {{
                    type: 'category',
                    data: data.map(item => item.name),
                    axisLabel: {{
                        rotate: 45
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '成熟度评分'
                }},
                series: [{{
                    type: 'bar',
                    data: data.map(item => item.value),
                    itemStyle: {{
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {{offset: 0, color: '#667eea'}},
                            {{offset: 1, color: '#764ba2'}}
                        ])
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initInnovationIndexChart() {{
            const chart = echarts.init(document.getElementById('innovationIndexChart'));
            
            const innovationData = allData.detailed_analysis.detailed_research_fields.innovation_index;
            const data = Object.keys(innovationData).map(field => ({{
                name: field,
                value: innovationData[field].innovation_score,
                level: innovationData[field].innovation_level
            }}));

            const option = {{
                title: {{
                    text: '创新指数评分',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>创新指数: {{c}}<br/>创新等级: {{d}}'
                }},
                radar: {{
                    indicator: data.map(item => ({{
                        name: item.name.length > 10 ? item.name.slice(0, 10) + '...' : item.name,
                        max: 100
                    }}))
                }},
                series: [{{
                    type: 'radar',
                    data: [{{
                        value: data.map(item => item.value),
                        name: '创新指数',
                        areaStyle: {{
                            color: 'rgba(102, 126, 234, 0.3)'
                        }}
                    }}]
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initInterdisciplinaryChart() {{
            const chart = echarts.init(document.getElementById('interdisciplinaryChart'));
            
            const interdisciplinaryData = allData.detailed_analysis.detailed_research_fields.interdisciplinary_analysis;
            
            // 创建节点和边
            const nodes = Object.keys(interdisciplinaryData).map(field => ({{
                id: field,
                name: field,
                value: interdisciplinaryData[field].connection_count,
                category: 0
            }}));
            
            const links = [];
            Object.keys(interdisciplinaryData).forEach(field => {{
                interdisciplinaryData[field].connected_fields.forEach(connectedField => {{
                    links.push({{
                        source: field,
                        target: connectedField
                    }});
                }});
            }});

            const option = {{
                title: {{
                    text: '跨学科连接网络',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>连接数: {{c}}'
                }},
                series: [{{
                    type: 'graph',
                    layout: 'force',
                    data: nodes,
                    links: links,
                    categories: [{{name: '研究领域'}}],
                    roam: true,
                    force: {{
                        repulsion: 100,
                        edgeLength: 50
                    }},
                    label: {{
                        show: true,
                        position: 'right'
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        // 应用场景图表初始化函数
        function initLifecycleChart() {{
            const chart = echarts.init(document.getElementById('lifecycleChart'));
            
            const lifecycleData = allData.detailed_analysis.detailed_application_scenarios.scenario_lifecycle;
            const data = Object.keys(lifecycleData).map(scenario => ({{
                name: scenario,
                stage: lifecycleData[scenario].lifecycle_stage
            }}));

            const stageColors = {{
                '导入期': '#ff6b6b',
                '成长期': '#4ecdc4',
                '成熟期': '#45b7d1',
                '饱和期': '#96ceb4',
                '转型期': '#feca57'
            }};

            const option = {{
                title: {{
                    text: '应用场景生命周期分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>生命周期阶段: {{c}}'
                }},
                series: [{{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: Object.keys(stageColors).map(stage => ({{
                        name: stage,
                        value: data.filter(item => item.stage === stage).length,
                        itemStyle: {{
                            color: stageColors[stage]
                        }}
                    }}))
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initMarketPenetrationChart() {{
            const chart = echarts.init(document.getElementById('marketPenetrationChart'));
            
            const penetrationData = allData.detailed_analysis.detailed_application_scenarios.market_penetration;
            const data = Object.keys(penetrationData).map(scenario => ({{
                name: scenario,
                value: penetrationData[scenario].penetration_score,
                level: penetrationData[scenario].penetration_level
            }}));

            const option = {{
                title: {{
                    text: '市场渗透度分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>渗透度: {{c}}%<br/>等级: {{d}}'
                }},
                xAxis: {{
                    type: 'category',
                    data: data.map(item => item.name),
                    axisLabel: {{
                        rotate: 45
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '渗透度评分'
                }},
                series: [{{
                    type: 'bar',
                    data: data.map(item => item.value),
                    itemStyle: {{
                        color: function(params) {{
                            const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'];
                            return colors[params.dataIndex % colors.length];
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initTechnicalReadinessChart() {{
            const chart = echarts.init(document.getElementById('technicalReadinessChart'));
            
            const readinessData = allData.detailed_analysis.detailed_application_scenarios.technical_readiness;
            const data = Object.keys(readinessData).map(scenario => ({{
                name: scenario,
                value: readinessData[scenario].score,
                level: readinessData[scenario].level,
                status: readinessData[scenario].status
            }}));

            const option = {{
                title: {{
                    text: '技术就绪度评估',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>TRL评分: {{c}}<br/>状态: {{d}}'
                }},
                radar: {{
                    indicator: data.map(item => ({{
                        name: item.name.length > 8 ? item.name.slice(0, 8) + '...' : item.name,
                        max: 100
                    }}))
                }},
                series: [{{
                    type: 'radar',
                    data: [{{
                        value: data.map(item => item.value),
                        name: '技术就绪度',
                        areaStyle: {{
                            color: 'rgba(118, 75, 162, 0.3)'
                        }}
                    }}]
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initBusinessImpactChart() {{
            const chart = echarts.init(document.getElementById('businessImpactChart'));
            
            const businessData = allData.detailed_analysis.detailed_application_scenarios.business_impact;
            const data = Object.keys(businessData).map(scenario => ({{
                name: scenario,
                business_value: businessData[scenario].business_value,
                investment_attractiveness: businessData[scenario].investment_attractiveness,
                roi_potential: businessData[scenario].roi_potential
            }}));

            const valueMapping = {{'极高': 4, '高': 3, '中等': 2, '低': 1}};

            const option = {{
                title: {{
                    text: '商业影响力分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: function(params) {{
                        const item = data[params.dataIndex];
                        return `${{item.name}}<br/>商业价值: ${{item.business_value}}<br/>投资吸引力: ${{item.investment_attractiveness}}<br/>ROI潜力: ${{item.roi_potential}}`;
                    }}
                }},
                xAxis: {{
                    type: 'category',
                    data: data.map(item => item.name),
                    axisLabel: {{
                        rotate: 45
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '商业价值评分'
                }},
                series: [{{
                    type: 'bar',
                    data: data.map(item => valueMapping[item.business_value] || 2),
                    itemStyle: {{
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {{offset: 0, color: '#667eea'}},
                            {{offset: 1, color: '#764ba2'}}
                        ])
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initIndustryDistributionChart() {{
            const chart = echarts.init(document.getElementById('industryDistributionChart'));
            
            const industryData = allData.detailed_analysis.detailed_application_scenarios.industry_distribution;
            
            // 统计行业分布
            const industryCount = {{}};
            Object.keys(industryData).forEach(scenario => {{
                industryData[scenario].primary_industries.forEach(industry => {{
                    industryCount[industry] = (industryCount[industry] || 0) + 1;
                }});
            }});

            const data = Object.keys(industryCount).map(industry => ({{
                name: industry,
                value: industryCount[industry]
            }}));

            const option = {{
                title: {{
                    text: '主要应用行业分布',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}: {{c}} ({{d}}%)'
                }},
                series: [{{
                    type: 'pie',
                    radius: '60%',
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
            window.addEventListener('resize', () => chart.resize());
        }}

        // 技术发展图表
        function initTechTaxonomyChart() {{
            const chart = echarts.init(document.getElementById('techTaxonomyChart'));
            
            const taxonomyData = allData.detailed_analysis.detailed_technology_trends.technology_taxonomy;
            const data = Object.keys(taxonomyData).map(category => ({{
                name: category,
                value: taxonomyData[category].total_mentions,
                maturity: taxonomyData[category].maturity,
                adoption: taxonomyData[category].adoption_rate
            }}));

            const option = {{
                title: {{
                    text: '技术分类体系分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>提及次数: {{c}}<br/>成熟度: {{d}}'
                }},
                series: [{{
                    type: 'treemap',
                    data: data.map(item => ({{
                        name: item.name,
                        value: item.value,
                        itemStyle: {{
                            color: item.maturity === 'mature' ? '#4CAF50' : 
                                   item.maturity === 'developing' ? '#2196F3' :
                                   item.maturity === 'emerging' ? '#FF9800' : '#f44336'
                        }}
                    }}))
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initInnovationCycleChart() {{
            const chart = echarts.init(document.getElementById('innovationCycleChart'));
            
            const cycleData = allData.detailed_analysis.detailed_technology_trends.innovation_cycles;
            const data = Object.keys(cycleData).map(tech => ({{
                name: tech,
                stage: cycleData[tech].cycle_stage,
                position: cycleData[tech].cycle_position,
                potential: cycleData[tech].innovation_potential
            }}));

            const stageColors = {{
                '萌芽期': '#ff6b6b',
                '发展期': '#4ecdc4', 
                '增长期': '#45b7d1',
                '成熟期': '#96ceb4'
            }};

            const option = {{
                title: {{
                    text: '技术创新周期分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>周期阶段: {{c}}<br/>创新潜力: {{d}}%'
                }},
                series: [{{
                    type: 'pie',
                    radius: ['30%', '60%'],
                    data: Object.keys(stageColors).map(stage => ({{
                        name: stage,
                        value: data.filter(item => item.stage === stage).length,
                        itemStyle: {{
                            color: stageColors[stage]
                        }}
                    }}))
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initTechnologyMaturityChart() {{
            const chart = echarts.init(document.getElementById('technologyMaturityChart'));
            
            const taxonomyData = allData.detailed_analysis.detailed_technology_trends.technology_taxonomy;
            const data = [];
            
            Object.keys(taxonomyData).forEach(category => {{
                Object.keys(taxonomyData[category].technology_details).forEach(tech => {{
                    const detail = taxonomyData[category].technology_details[tech];
                    data.push({{
                        name: tech,
                        value: [detail.maturity_score, detail.application_breadth.score],
                        category: category
                    }});
                }});
            }});

            const option = {{
                title: {{
                    text: '技术成熟度 vs 应用广度',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>成熟度: {{c0}}<br/>应用广度: {{c1}}'
                }},
                xAxis: {{
                    type: 'value',
                    name: '技术成熟度',
                    max: 100
                }},
                yAxis: {{
                    type: 'value',
                    name: '应用广度',
                    max: 100
                }},
                series: [{{
                    type: 'scatter',
                    data: data.map(item => item.value),
                    symbolSize: 20,
                    itemStyle: {{
                        color: function(params) {{
                            const colors = ['#667eea', '#764ba2', '#4ecdc4', '#ff6b6b'];
                            return colors[params.dataIndex % colors.length];
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initConvergenceChart() {{
            const chart = echarts.init(document.getElementById('convergenceChart'));
            
            const convergenceData = allData.detailed_analysis.detailed_technology_trends.convergence_analysis;
            const data = Object.keys(convergenceData).map(pattern => ({{
                name: pattern,
                value: convergenceData[pattern].convergence_score,
                maturity: convergenceData[pattern].maturity,
                technologies: convergenceData[pattern].technologies
            }}));

            const option = {{
                title: {{
                    text: '技术融合模式分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: function(params) {{
                        const item = data[params.dataIndex];
                        return `${{item.name}}<br/>融合分数: ${{item.value}}<br/>成熟度: ${{item.maturity}}<br/>涉及技术: ${{item.technologies.join(', ')}}`;
                    }}
                }},
                xAxis: {{
                    type: 'category',
                    data: data.map(item => item.name),
                    axisLabel: {{
                        rotate: 0
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '融合评分'
                }},
                series: [{{
                    type: 'bar',
                    data: data.map(item => item.value),
                    itemStyle: {{
                        color: function(params) {{
                            const item = data[params.dataIndex];
                            return item.maturity === '成熟融合' ? '#4CAF50' : 
                                   item.maturity === '发展中融合' ? '#2196F3' : '#FF9800';
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initResearchHotspotsChart() {{
            const chart = echarts.init(document.getElementById('researchHotspotsChart'));
            
            const hotspotsData = allData.detailed_analysis.detailed_technology_trends.research_hotspots;
            
            // 合并所有热点
            const allHotspots = [
                ...hotspotsData.current_hotspots,
                ...hotspotsData.emerging_topics,
                ...hotspotsData.interdisciplinary_topics
            ];

            const data = allHotspots.map(hotspot => ({{
                name: hotspot.keyword,
                value: hotspot.mentions,
                category: hotspot.category
            }}));

            const option = {{
                title: {{
                    text: '研究热点分布',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>提及次数: {{c}}<br/>类别: {{d}}'
                }},
                series: [{{
                    type: 'wordCloud',
                    gridSize: 2,
                    sizeRange: [12, 50],
                    rotationRange: [-90, 90],
                    shape: 'pentagon',
                    data: data.slice(0, 30),  // 只显示前30个
                    textStyle: {{
                        color: function() {{
                            const colors = ['#667eea', '#764ba2', '#4ecdc4', '#ff6b6b', '#96ceb4'];
                            return colors[Math.floor(Math.random() * colors.length)];
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        // 任务场景图表
        function initTaskComplexityChart() {{
            const chart = echarts.init(document.getElementById('taskComplexityChart'));
            
            const complexityData = allData.detailed_analysis.detailed_task_scenarios.task_complexity_analysis;
            const data = Object.keys(complexityData).map(task => ({{
                name: task,
                value: complexityData[task].complexity_score,
                level: complexityData[task].complexity_level
            }}));

            const option = {{
                title: {{
                    text: '任务复杂度分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>复杂度评分: {{c}}<br/>复杂度等级: {{d}}'
                }},
                radar: {{
                    indicator: data.map(item => ({{
                        name: item.name.replace(' Tasks', ''),
                        max: 100
                    }}))
                }},
                series: [{{
                    type: 'radar',
                    data: [{{
                        value: data.map(item => item.value),
                        name: '任务复杂度',
                        areaStyle: {{
                            color: 'rgba(102, 126, 234, 0.3)'
                        }}
                    }}]
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initAutomationReadinessChart() {{
            const chart = echarts.init(document.getElementById('automationReadinessChart'));
            
            const automationData = allData.detailed_analysis.detailed_task_scenarios.automation_readiness;
            const data = Object.keys(automationData).map(task => ({{
                name: task.replace(' Tasks', ''),
                value: automationData[task].readiness_score,
                level: automationData[task].automation_level,
                timeline: automationData[task].timeline
            }}));

            const option = {{
                title: {{
                    text: '自动化就绪度评估',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>就绪度: {{c}}%<br/>自动化等级: {{d}}'
                }},
                xAxis: {{
                    type: 'category',
                    data: data.map(item => item.name),
                    axisLabel: {{
                        rotate: 45
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '自动化就绪度 (%)',
                    max: 100
                }},
                series: [{{
                    type: 'bar',
                    data: data.map(item => item.value),
                    itemStyle: {{
                        color: function(params) {{
                            const value = data[params.dataIndex].value;
                            if (value >= 80) return '#4CAF50';
                            if (value >= 60) return '#2196F3';
                            if (value >= 40) return '#FF9800';
                            return '#f44336';
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initHumanAiCollaborationChart() {{
            const chart = echarts.init(document.getElementById('humanAiCollaborationChart'));
            
            const collaborationData = allData.detailed_analysis.detailed_task_scenarios.human_ai_collaboration;
            
            // 统计协作模式
            const modeCount = {{}};
            Object.keys(collaborationData).forEach(task => {{
                const mode = collaborationData[task].collaboration_mode;
                modeCount[mode] = (modeCount[mode] || 0) + 1;
            }});

            const data = Object.keys(modeCount).map(mode => ({{
                name: mode,
                value: modeCount[mode]
            }}));

            const option = {{
                title: {{
                    text: '人机协作模式分布',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}: {{c}} ({{d}}%)'
                }},
                series: [{{
                    type: 'pie',
                    radius: '60%',
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
            window.addEventListener('resize', () => chart.resize());
        }}

        function initEthicalConsiderationsChart() {{
            const chart = echarts.init(document.getElementById('ethicalConsiderationsChart'));
            
            const ethicalData = allData.detailed_analysis.detailed_task_scenarios.ethical_considerations;
            
            // 统计风险等级
            const riskCount = {{}};
            Object.keys(ethicalData).forEach(task => {{
                const risk = ethicalData[task].risk_level;
                riskCount[risk] = (riskCount[risk] || 0) + 1;
            }});

            const data = Object.keys(riskCount).map(risk => ({{
                name: risk,
                value: riskCount[risk]
            }}));

            const riskColors = {{
                'Very High': '#f44336',
                'High': '#FF9800',
                'Medium': '#2196F3',
                'Low': '#4CAF50',
                'Variable': '#9C27B0'
            }};

            const option = {{
                title: {{
                    text: '伦理风险等级分布',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}: {{c}} ({{d}}%)'
                }},
                series: [{{
                    type: 'pie',
                    radius: ['30%', '60%'],
                    data: data.map(item => ({{
                        name: item.name,
                        value: item.value,
                        itemStyle: {{
                            color: riskColors[item.name] || '#ccc'
                        }}
                    }}))
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initPerformanceMetricsChart() {{
            const chart = echarts.init(document.getElementById('performanceMetricsChart'));
            
            const metricsData = allData.detailed_analysis.detailed_task_scenarios.performance_metrics;
            const data = Object.keys(metricsData).map(task => ({{
                name: task.replace(' Tasks', ''),
                threshold: metricsData[task].success_threshold,
                sota: metricsData[task].current_sota
            }}));

            const option = {{
                title: {{
                    text: '性能指标对比',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis',
                    formatter: function(params) {{
                        let result = params[0].axisValue + '<br/>';
                        params.forEach(param => {{
                            result += param.seriesName + ': ' + (param.value * 100).toFixed(1) + '%<br/>';
                        }});
                        return result;
                    }}
                }},
                legend: {{
                    data: ['成功阈值', '当前SOTA'],
                    top: 30
                }},
                xAxis: {{
                    type: 'category',
                    data: data.map(item => item.name),
                    axisLabel: {{
                        rotate: 45
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '性能指标',
                    max: 1,
                    axisLabel: {{
                        formatter: '{{value}}%'
                    }}
                }},
                series: [
                    {{
                        name: '成功阈值',
                        type: 'bar',
                        data: data.map(item => item.threshold),
                        itemStyle: {{
                            color: '#FF9800'
                        }}
                    }},
                    {{
                        name: '当前SOTA',
                        type: 'bar',
                        data: data.map(item => item.sota),
                        itemStyle: {{
                            color: '#4CAF50'
                        }}
                    }}
                ]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initResourceRequirementsChart() {{
            const chart = echarts.init(document.getElementById('resourceRequirementsChart'));
            
            const resourceData = allData.detailed_analysis.detailed_task_scenarios.resource_requirements;
            
            // 转换资源等级为数值
            const levelMapping = {{
                'very_low': 1, 'low': 2, 'medium': 3, 'high': 4, 'very_high': 5,
                'short': 1, 'medium': 3, 'long': 4, 'very_long': 5
            }};

            const data = Object.keys(resourceData).map(task => ({{
                name: task.replace(' Tasks', ''),
                computational: levelMapping[resourceData[task].computational_cost] || 3,
                memory: levelMapping[resourceData[task].memory_requirements] || 3,
                data: levelMapping[resourceData[task].data_volume_needed] || 3,
                training: levelMapping[resourceData[task].training_time] || 3
            }}));

            const option = {{
                title: {{
                    text: '资源需求分析',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis'
                }},
                legend: {{
                    data: ['计算成本', '内存需求', '数据量', '训练时间'],
                    top: 30
                }},
                radar: {{
                    indicator: data.map(item => ({{
                        name: item.name,
                        max: 5
                    }}))
                }},
                series: [
                    {{
                        type: 'radar',
                        data: [
                            {{
                                value: data.map(item => item.computational),
                                name: '计算成本',
                                areaStyle: {{color: 'rgba(255, 152, 0, 0.3)'}}
                            }},
                            {{
                                value: data.map(item => item.memory),
                                name: '内存需求',
                                areaStyle: {{color: 'rgba(33, 150, 243, 0.3)'}}
                            }},
                            {{
                                value: data.map(item => item.data),
                                name: '数据量',
                                areaStyle: {{color: 'rgba(76, 175, 80, 0.3)'}}
                            }},
                            {{
                                value: data.map(item => item.training),
                                name: '训练时间',
                                areaStyle: {{color: 'rgba(244, 67, 54, 0.3)'}}
                            }}
                        ]
                    }}
                ]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        // 深度洞察图表
        function initConvergenceOpportunitiesChart() {{
            const chart = echarts.init(document.getElementById('convergenceOpportunitiesChart'));
            
            const opportunities = allData.detailed_analysis.cross_dimensional_insights.convergence_opportunities;
            
            const data = opportunities.map(opp => ({{
                name: opp.area,
                potential: opp.potential === 'Very High' ? 5 : opp.potential === 'High' ? 4 : 3,
                timeline: opp.timeline,
                components: opp.components
            }}));

            const option = {{
                title: {{
                    text: '融合机会识别',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: function(params) {{
                        const item = data[params.dataIndex];
                        return `${{item.name}}<br/>潜力等级: ${{item.potential}}<br/>时间线: ${{item.timeline}}<br/>组成要素: ${{item.components.join(', ')}}`;
                    }}
                }},
                xAxis: {{
                    type: 'category',
                    data: data.map(item => item.name)
                }},
                yAxis: {{
                    type: 'value',
                    name: '潜力等级',
                    max: 5
                }},
                series: [{{
                    type: 'bar',
                    data: data.map(item => item.potential),
                    itemStyle: {{
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {{offset: 0, color: '#667eea'}},
                            {{offset: 1, color: '#764ba2'}}
                        ])
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initInvestmentPriorityChart() {{
            const chart = echarts.init(document.getElementById('investmentPriorityChart'));
            
            // 基于各维度数据计算投资优先级
            const researchFields = allData.trends_data.research_fields_trends;
            const priorities = Object.keys(researchFields).map(field => {{
                const data = researchFields[field];
                const growthScore = Math.min(data.growth_rate / 10, 10);  // 增长率评分
                const scaleScore = Math.min(data.total_papers / 1000, 10);  // 规模评分
                const priorityScore = (growthScore + scaleScore) / 2;
                
                return {{
                    name: field,
                    growth: data.growth_rate,
                    scale: data.total_papers,
                    priority: priorityScore
                }};
            }}).sort((a, b) => b.priority - a.priority).slice(0, 8);

            const option = {{
                title: {{
                    text: '投资优先级矩阵',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>增长率: {{c0}}%<br/>规模: {{c1}}篇<br/>优先级: {{c2}}'
                }},
                xAxis: {{
                    type: 'value',
                    name: '增长率 (%)',
                    max: 60
                }},
                yAxis: {{
                    type: 'value',
                    name: '论文规模',
                    max: 12000
                }},
                series: [{{
                    type: 'scatter',
                    data: priorities.map(item => [item.growth, item.scale, item.priority]),
                    symbolSize: function(data) {{
                        return data[2] * 5;  // 根据优先级调整气泡大小
                    }},
                    itemStyle: {{
                        color: function(params) {{
                            const priority = params.data[2];
                            if (priority >= 8) return '#4CAF50';
                            if (priority >= 6) return '#2196F3';
                            if (priority >= 4) return '#FF9800';
                            return '#f44336';
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        // 预测图表
        function initShortTermTrendsChart() {{
            const chart = echarts.init(document.getElementById('shortTermTrendsChart'));
            
            const shortTermTrends = allData.detailed_analysis.detailed_technology_trends.future_directions.short_term_trends;
            
            const data = shortTermTrends.map(trend => ({{
                name: trend.trend,
                probability: trend.probability * 100,
                impact: trend.impact === 'high' ? 3 : trend.impact === 'medium' ? 2 : 1
            }}));

            const option = {{
                title: {{
                    text: '短期趋势预测 (2024-2025)',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}<br/>概率: {{c0}}%<br/>影响程度: {{c1}}'
                }},
                xAxis: {{
                    type: 'value',
                    name: '实现概率 (%)',
                    max: 100
                }},
                yAxis: {{
                    type: 'value',
                    name: '影响程度',
                    max: 4
                }},
                series: [{{
                    type: 'scatter',
                    data: data.map(item => [item.probability, item.impact]),
                    symbolSize: function(data) {{
                        return data[0] / 2;  // 根据概率调整气泡大小
                    }},
                    itemStyle: {{
                        color: function(params) {{
                            const impact = params.data[1];
                            if (impact >= 3) return '#4CAF50';
                            if (impact >= 2) return '#2196F3';
                            return '#FF9800';
                        }}
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initMediumTermTrendsChart() {{
            const chart = echarts.init(document.getElementById('mediumTermTrendsChart'));
            
            const mediumTermTrends = allData.detailed_analysis.detailed_technology_trends.future_directions.medium_term_trends;
            
            const data = mediumTermTrends.map(trend => ({{
                name: trend.trend,
                value: trend.probability * 100
            }}));

            const option = {{
                title: {{
                    text: '中期发展预测 (2025-2027)',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}: {{c}}%'
                }},
                series: [{{
                    type: 'pie',
                    radius: ['30%', '60%'],
                    data: data,
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }},
                    label: {{
                        show: true,
                        formatter: '{{b}}\\n{{c}}%'
                    }}
                }}]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function initPrediction2025Chart() {{
            const chart = echarts.init(document.getElementById('prediction2025Chart'));
            
            // 基于历史增长率预测2025年规模
            const researchFields = allData.trends_data.research_fields_trends;
            const predictions = Object.keys(researchFields).map(field => {{
                const data = researchFields[field];
                const currentPapers = data.total_papers;
                const growthRate = data.growth_rate / 100;
                const predicted2025 = Math.round(currentPapers * Math.pow(1 + growthRate, 2));  // 假设2年增长
                
                return {{
                    name: field,
                    current: currentPapers,
                    predicted: predicted2025
                }};
            }}).sort((a, b) => b.predicted - a.predicted).slice(0, 8);

            const option = {{
                title: {{
                    text: '2025年领域规模预测',
                    left: 'center'
                }},
                tooltip: {{
                    trigger: 'axis',
                    formatter: function(params) {{
                        let result = params[0].axisValue + '<br/>';
                        params.forEach(param => {{
                            result += param.seriesName + ': ' + param.value.toLocaleString() + '篇<br/>';
                        }});
                        return result;
                    }}
                }},
                legend: {{
                    data: ['当前规模', '预测规模'],
                    top: 30
                }},
                xAxis: {{
                    type: 'category',
                    data: predictions.map(item => item.name.length > 12 ? item.name.slice(0, 12) + '...' : item.name),
                    axisLabel: {{
                        rotate: 45
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    name: '论文数量'
                }},
                series: [
                    {{
                        name: '当前规模',
                        type: 'bar',
                        data: predictions.map(item => item.current),
                        itemStyle: {{
                            color: '#2196F3'
                        }}
                    }},
                    {{
                        name: '预测规模',
                        type: 'bar',
                        data: predictions.map(item => item.predicted),
                        itemStyle: {{
                            color: '#4CAF50'
                        }}
                    }}
                ]
            }};
            
            chart.setOption(option);
            window.addEventListener('resize', () => chart.resize());
        }}

        function setupNavigation() {{
            // 平滑滚动
            document.querySelectorAll('.nav-item').forEach(item => {{
                item.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {{
                        targetElement.scrollIntoView({{
                            behavior: 'smooth'
                        }});
                    }}
                }});
            }});
        }}

        function populateDataTables() {{
            // 填充研究领域数据表
            const researchFieldsTable = document.getElementById('researchFieldsTable');
            const researchFields = allData.trends_data.research_fields_trends;
            const maturityData = allData.detailed_analysis.detailed_research_fields.research_maturity;
            const innovationData = allData.detailed_analysis.detailed_research_fields.innovation_index;
            
            Object.keys(researchFields).forEach(field => {{
                const row = researchFieldsTable.insertRow();
                const fieldData = researchFields[field];
                const maturity = maturityData[field] || {{}};
                const innovation = innovationData[field] || {{}};
                
                row.innerHTML = `
                    <td>${{field}}</td>
                    <td>${{fieldData.total_papers.toLocaleString()}}</td>
                    <td><span class="trend-up">${{fieldData.growth_rate.toFixed(1)}}%</span></td>
                    <td>${{maturity.maturity_level || 'N/A'}}</td>
                    <td>${{innovation.innovation_level || 'N/A'}}</td>
                    <td>${{fieldData.trend_type || 'N/A'}}</td>
                `;
            }});
        }}
    </script>
</body>
</html>"""

def main():
    """主函数"""
    print("🚀 启动增强版可视化生成...")
    
    generator = EnhancedVisualizationGenerator()
    output_file = generator.generate_enhanced_visualization()
    
    print("\n" + "="*60)
    print("🎨 增强版可视化页面生成完成！")
    print(f"📁 文件位置: {output_file}")
    print("🌐 在浏览器中打开该文件即可查看完整的深度分析可视化")
    
    return output_file

if __name__ == "__main__":
    main()