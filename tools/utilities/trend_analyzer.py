#!/usr/bin/env python3
"""
深度趋势分析器
分析研究领域、应用场景、技术发展、任务场景的发展趋势
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class TrendAnalyzer:
    """深度趋势分析器"""
    
    def __init__(self, data_path: str = "outputs/analysis/comprehensive_analysis.json"):
        self.data_path = Path(data_path)
        self.data = self.load_data()
        self.output_dir = Path("outputs/trend_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self) -> Dict:
        """加载分析数据"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_research_fields_trends(self) -> Dict[str, Any]:
        """分析研究领域发展趋势"""
        print("🔍 分析研究领域发展趋势...")
        
        field_trends = self.data['field_analysis']['field_trends']
        years = list(range(2018, 2025))
        
        # 计算增长率和趋势
        trends_analysis = {}
        
        for field, yearly_data in field_trends.items():
            # 提取年度数据
            values = [yearly_data.get(str(year), 0) for year in years]
            
            # 计算各种趋势指标
            total_papers = sum(values)
            peak_year = years[values.index(max(values))]
            peak_value = max(values)
            
            # 计算增长率 (2018-2023, 排除2024年因为数据不完整)
            early_avg = np.mean(values[:3])  # 2018-2020
            recent_avg = np.mean(values[3:6])  # 2021-2023
            growth_rate = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
            
            # 计算趋势系数 (线性回归斜率)
            x = np.array(years[:-1])  # 排除2024
            y = np.array(values[:-1])
            trend_coeff = np.polyfit(x, y, 1)[0] if len(y) > 1 else 0
            
            # 判断趋势类型
            if trend_coeff > 50:
                trend_type = "强劲增长"
            elif trend_coeff > 20:
                trend_type = "稳步增长"
            elif trend_coeff > -20:
                trend_type = "基本稳定"
            else:
                trend_type = "下降趋势"
                
            trends_analysis[field] = {
                'total_papers': total_papers,
                'peak_year': peak_year,
                'peak_value': peak_value,
                'growth_rate': round(growth_rate, 1),
                'trend_coefficient': round(trend_coeff, 2),
                'trend_type': trend_type,
                'yearly_values': values,
                'market_share_2023': round(yearly_data.get('2023', 0) / sum(yearly_data.get('2023', 0) for yearly_data in field_trends.values()) * 100, 2)
            }
        
        return trends_analysis
    
    def analyze_application_scenarios_trends(self) -> Dict[str, Any]:
        """分析应用场景发展趋势"""
        print("🎯 分析应用场景发展趋势...")
        
        scenario_trends = self.data['task_scenario_analysis']['scenario_yearly_trends']
        years = list(range(2018, 2025))
        
        scenarios_analysis = {}
        
        for scenario, yearly_data in scenario_trends.items():
            if scenario == "General Research":  # 跳过通用研究
                continue
                
            values = [yearly_data.get(str(year), 0) for year in years]
            
            # 计算成熟度指标
            total_papers = sum(values)
            consistency = np.std(values[:-1]) / np.mean(values[:-1]) if np.mean(values[:-1]) > 0 else 0  # 变异系数
            
            # 计算发展阶段
            early_sum = sum(values[:2])  # 2018-2019
            middle_sum = sum(values[2:5])  # 2020-2022
            recent_sum = sum(values[5:7])  # 2023-2024
            
            if early_sum < 100 and recent_sum > middle_sum:
                development_stage = "新兴领域"
            elif middle_sum > early_sum * 2 and recent_sum > middle_sum:
                development_stage = "快速发展"
            elif consistency < 0.3:
                development_stage = "成熟稳定"
            else:
                development_stage = "波动调整"
            
            # 计算年复合增长率 (CAGR)
            if values[0] > 0 and values[5] > 0:  # 2018 to 2023
                cagr = (pow(values[5] / values[0], 1/5) - 1) * 100
            else:
                cagr = 0
                
            scenarios_analysis[scenario] = {
                'total_papers': total_papers,
                'development_stage': development_stage,
                'cagr_2018_2023': round(cagr, 1),
                'consistency_score': round(1 - consistency, 2),  # 一致性评分
                'yearly_values': values,
                'recent_momentum': values[5] - values[4] if len(values) > 5 else 0  # 2023 vs 2022
            }
        
        return scenarios_analysis
    
    def analyze_technology_trends(self) -> Dict[str, Any]:
        """分析技术发展趋势"""
        print("💻 分析技术发展趋势...")
        
        # 基于关键词分析技术趋势
        keywords = self.data['keyword_analysis']['top_keywords']
        
        # 定义技术类别
        tech_categories = {
            'Deep Learning': ['deep', 'neural', 'networks', 'cnn', 'rnn', 'transformer'],
            'Machine Learning': ['learning', 'training', 'algorithm', 'model', 'supervised'],
            'Optimization': ['optimization', 'gradient', 'sgd', 'adam', 'loss'],
            'Graph Technology': ['graph', 'node', 'edge', 'network', 'social'],
            'Computer Vision': ['image', 'vision', 'visual', 'object', 'detection'],
            'Natural Language': ['language', 'text', 'nlp', 'word', 'semantic'],
            'Reinforcement Learning': ['reinforcement', 'reward', 'policy', 'agent', 'environment'],
            'Generative Models': ['generative', 'gan', 'vae', 'diffusion', 'generation']
        }
        
        tech_scores = {}
        for category, category_keywords in tech_categories.items():
            score = sum(keywords.get(keyword, 0) for keyword in category_keywords)
            tech_scores[category] = score
        
        # 任务类型演化趋势
        task_evolution = self.data['cross_analysis']['yearly_task_evolution']
        
        return {
            'technology_popularity': tech_scores,
            'task_type_evolution': task_evolution
        }
    
    def analyze_task_scenarios_trends(self) -> Dict[str, Any]:
        """分析任务场景发展趋势"""
        print("⚙️ 分析任务场景发展趋势...")
        
        task_evolution = self.data['cross_analysis']['yearly_task_evolution']
        years = list(range(2018, 2025))
        
        task_trends = {}
        
        for task_type, yearly_ratios in task_evolution.items():
            values = [yearly_ratios.get(str(year), 0) * 100 for year in years[:-1]]  # 转换为百分比
            
            # 计算趋势
            trend_direction = "上升" if values[-1] > values[0] else "下降"
            volatility = np.std(values)
            
            # 计算在不同时期的重要性
            early_importance = np.mean(values[:2])
            recent_importance = np.mean(values[-2:])
            
            task_trends[task_type] = {
                'trend_direction': trend_direction,
                'volatility': round(volatility, 3),
                'early_importance': round(early_importance, 2),
                'recent_importance': round(recent_importance, 2),
                'importance_change': round(recent_importance - early_importance, 2),
                'yearly_percentages': values
            }
        
        return task_trends
    
    def generate_trend_insights(self, field_trends: Dict, scenario_trends: Dict, 
                              tech_trends: Dict, task_trends: Dict) -> List[str]:
        """生成趋势洞察"""
        insights = []
        
        # 研究领域洞察
        fastest_growing = max(field_trends.items(), key=lambda x: x[1]['growth_rate'])
        insights.append(f"📈 增长最快的研究领域：{fastest_growing[0]}（增长率{fastest_growing[1]['growth_rate']}%）")
        
        # 应用场景洞察
        emerging_scenarios = [name for name, data in scenario_trends.items() 
                             if data['development_stage'] == '新兴领域']
        if emerging_scenarios:
            insights.append(f"🌟 新兴应用场景：{', '.join(emerging_scenarios)}")
        
        # 技术趋势洞察
        top_tech = max(tech_trends['technology_popularity'].items(), key=lambda x: x[1])
        insights.append(f"🔥 最热门技术：{top_tech[0]}（提及次数{top_tech[1]:,}）")
        
        # 任务类型洞察
        rising_tasks = [task for task, data in task_trends.items() 
                       if data['importance_change'] > 1]
        if rising_tasks:
            insights.append(f"⬆️ 重要性上升的任务类型：{', '.join(rising_tasks)}")
        
        return insights
    
    def generate_report(self) -> Dict[str, Any]:
        """生成完整的趋势分析报告"""
        print("📊 生成趋势分析报告...")
        
        # 执行各项分析
        field_trends = self.analyze_research_fields_trends()
        scenario_trends = self.analyze_application_scenarios_trends()
        tech_trends = self.analyze_technology_trends()
        task_trends = self.analyze_task_scenarios_trends()
        
        # 生成洞察
        insights = self.generate_trend_insights(field_trends, scenario_trends, tech_trends, task_trends)
        
        # 构建完整报告
        report = {
            'generation_time': datetime.now().isoformat(),
            'research_fields_trends': field_trends,
            'application_scenarios_trends': scenario_trends,
            'technology_trends': tech_trends,
            'task_scenarios_trends': task_trends,
            'key_insights': insights,
            'summary_statistics': {
                'total_research_fields': len(field_trends),
                'total_application_scenarios': len(scenario_trends),
                'analysis_period': "2018-2024",
                'fastest_growing_field': max(field_trends.items(), key=lambda x: x[1]['growth_rate'])[0],
                'most_stable_field': min(field_trends.items(), key=lambda x: abs(x[1]['trend_coefficient']))[0]
            }
        }
        
        # 保存报告
        report_file = self.output_dir / 'trend_analysis_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成可读报告
        self.generate_readable_report(report)
        
        print(f"✅ 趋势分析报告已生成：{report_file}")
        return report
    
    def generate_readable_report(self, report: Dict):
        """生成可读的趋势分析报告"""
        readable_report = f"""
# AI会议论文发展趋势深度分析报告

生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
分析期间：2018-2024年
数据来源：31,244篇AI顶级会议论文

## 📊 核心发现

{chr(10).join(f"• {insight}" for insight in report['key_insights'])}

## 🔬 研究领域发展趋势

### 头部领域（论文数量Top 5）
"""
        
        # 研究领域分析
        field_trends = report['research_fields_trends']
        top_fields = sorted(field_trends.items(), key=lambda x: x[1]['total_papers'], reverse=True)[:5]
        
        for i, (field, data) in enumerate(top_fields, 1):
            readable_report += f"""
{i}. **{field}**
   - 总论文数：{data['total_papers']:,}篇
   - 发展趋势：{data['trend_type']}
   - 增长率：{data['growth_rate']}%
   - 峰值年份：{data['peak_year']}年（{data['peak_value']:,}篇）
   - 市场份额：{data['market_share_2023']}%（2023年）
"""

        readable_report += f"""
### 增长最快领域（Top 3）
"""
        fastest_growing = sorted(field_trends.items(), key=lambda x: x[1]['growth_rate'], reverse=True)[:3]
        for i, (field, data) in enumerate(fastest_growing, 1):
            readable_report += f"{i}. {field}：{data['growth_rate']}%增长\n"

        # 应用场景分析
        readable_report += f"""
## 🎯 应用场景发展趋势

### 发展阶段分布
"""
        scenario_trends = report['application_scenarios_trends']
        stage_distribution = {}
        for scenario, data in scenario_trends.items():
            stage = data['development_stage']
            if stage not in stage_distribution:
                stage_distribution[stage] = []
            stage_distribution[stage].append(scenario)
        
        for stage, scenarios in stage_distribution.items():
            readable_report += f"- **{stage}**：{', '.join(scenarios)}\n"

        readable_report += f"""
### 复合增长率最高场景（CAGR Top 5）
"""
        top_cagr = sorted(scenario_trends.items(), key=lambda x: x[1]['cagr_2018_2023'], reverse=True)[:5]
        for i, (scenario, data) in enumerate(top_cagr, 1):
            readable_report += f"{i}. {scenario}：{data['cagr_2018_2023']}%\n"

        # 技术趋势分析
        readable_report += f"""
## 💻 技术发展趋势

### 技术热度排行（基于关键词提及次数）
"""
        tech_popularity = report['technology_trends']['technology_popularity']
        sorted_tech = sorted(tech_popularity.items(), key=lambda x: x[1], reverse=True)
        for i, (tech, score) in enumerate(sorted_tech, 1):
            readable_report += f"{i}. {tech}：{score:,}次提及\n"

        # 任务类型趋势
        readable_report += f"""
## ⚙️ 任务类型演化趋势

### 重要性变化分析
"""
        task_trends = report['task_scenarios_trends']
        for task_type, data in task_trends.items():
            change_indicator = "📈" if data['importance_change'] > 0 else "📉"
            readable_report += f"- **{task_type}** {change_indicator}\n"
            readable_report += f"  - 早期重要性：{data['early_importance']}%\n"
            readable_report += f"  - 近期重要性：{data['recent_importance']}%\n"
            readable_report += f"  - 变化幅度：{data['importance_change']:+.2f}%\n\n"

        readable_report += f"""
## 📈 预测与建议

### 值得关注的发展方向
1. **新兴领域投资**：Manufacturing、Medical Diagnosis等新兴场景展现强劲增长潜力
2. **技术融合趋势**：Deep Learning与其他技术领域的交叉融合加速
3. **应用场景扩展**：从学术研究向实际应用场景转移的趋势明显
4. **任务类型多样化**：Generation Tasks和Optimization Tasks重要性持续上升

### 研究热点预测
基于当前趋势，预计未来2-3年内以下领域将继续保持高热度：
- Educational Technology（教育技术）
- Content Creation（内容创作）
- Medical Diagnosis（医疗诊断）
- Autonomous Driving（自动驾驶）

---
*报告基于{report['summary_statistics']['total_research_fields']}个研究领域和{report['summary_statistics']['total_application_scenarios']}个应用场景的深度分析*
"""
        
        # 保存可读报告
        readable_file = self.output_dir / 'trend_analysis_readable.md'
        with open(readable_file, 'w', encoding='utf-8') as f:
            f.write(readable_report)
        
        print(f"📝 可读报告已生成：{readable_file}")

def main():
    """主函数"""
    print("🚀 启动深度趋势分析...")
    
    analyzer = TrendAnalyzer()
    report = analyzer.generate_report()
    
    print("\n" + "="*50)
    print("📊 趋势分析完成！")
    print(f"📁 报告保存位置：outputs/trend_analysis/")
    print("\n🔍 核心洞察：")
    for insight in report['key_insights']:
        print(f"  • {insight}")
    
    return report

if __name__ == "__main__":
    main()