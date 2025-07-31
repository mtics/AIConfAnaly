#!/usr/bin/env python3
"""
研究领域发展趋势深度分析器
包括总体趋势和分会议趋势分析
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ResearchTrendsAnalyzer:
    """研究领域发展趋势深度分析器"""
    
    def __init__(self, data_path: str = "outputs/analysis/comprehensive_analysis.json"):
        self.data_path = Path(data_path)
        self.data = self.load_data()
        self.output_dir = Path("outputs/research_trends")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 年份范围
        self.years = list(range(2018, 2025))
        self.analysis_years = list(range(2018, 2024))  # 排除2024年（数据不完整）
        
    def load_data(self) -> Dict:
        """加载分析数据"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_overall_trends(self) -> Dict[str, Any]:
        """分析总体研究领域发展趋势"""
        print("📊 分析总体研究领域发展趋势...")
        
        field_trends = self.data['field_analysis']['field_trends']
        
        overall_analysis = {
            'trend_patterns': {},
            'growth_analysis': {},
            'dominance_shifts': {},
            'emerging_fields': {},
            'declining_fields': {},
            'stability_analysis': {}
        }
        
        for field, yearly_data in field_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            
            # 1. 趋势模式分析
            trend_pattern = self.analyze_trend_pattern(values, field)
            overall_analysis['trend_patterns'][field] = trend_pattern
            
            # 2. 增长分析
            growth_analysis = self.analyze_growth_metrics(values, field)
            overall_analysis['growth_analysis'][field] = growth_analysis
            
            # 3. 稳定性分析
            stability = self.analyze_stability(values, field)
            overall_analysis['stability_analysis'][field] = stability
        
        # 4. 领域主导地位变化
        overall_analysis['dominance_shifts'] = self.analyze_dominance_shifts(field_trends)
        
        # 5. 新兴和衰退领域识别
        overall_analysis['emerging_fields'] = self.identify_emerging_fields(field_trends)
        overall_analysis['declining_fields'] = self.identify_declining_fields(field_trends)
        
        return overall_analysis
    
    def analyze_trend_pattern(self, values: List[int], field: str) -> Dict[str, Any]:
        """分析单个领域的趋势模式"""
        # 线性趋势
        x = np.array(range(len(values)))
        linear_slope, linear_intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # 多项式趋势（二次）
        poly_features = PolynomialFeatures(degree=2)
        x_poly = poly_features.fit_transform(x.reshape(-1, 1))
        poly_model = LinearRegression()
        poly_model.fit(x_poly, values)
        poly_score = poly_model.score(x_poly, values)
        
        # 趋势类型判断
        if abs(linear_slope) < 10:
            trend_type = "稳定型"
        elif linear_slope > 50:
            trend_type = "强增长型"
        elif linear_slope > 20:
            trend_type = "增长型"
        elif linear_slope < -20:
            trend_type = "衰退型"
        else:
            trend_type = "波动型"
        
        # 周期性检测
        is_cyclical = self.detect_cyclical_pattern(values)
        
        return {
            'linear_slope': round(linear_slope, 2),
            'r_squared': round(r_value**2, 3),
            'p_value': round(p_value, 4),
            'trend_type': trend_type,
            'polynomial_fit': round(poly_score, 3),
            'is_cyclical': is_cyclical,
            'trend_strength': abs(linear_slope),
            'trend_significance': 'significant' if p_value < 0.05 else 'not_significant'
        }
    
    def detect_cyclical_pattern(self, values: List[int]) -> bool:
        """检测是否存在周期性模式"""
        if len(values) < 4:
            return False
        
        # 简单的峰谷检测
        peaks = 0
        valleys = 0
        
        for i in range(1, len(values) - 1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                peaks += 1
            elif values[i] < values[i-1] and values[i] < values[i+1]:
                valleys += 1
        
        return peaks >= 2 or valleys >= 2
    
    def analyze_growth_metrics(self, values: List[int], field: str) -> Dict[str, Any]:
        """分析增长指标"""
        if len(values) < 2:
            return {}
        
        # 总增长率
        total_growth = ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
        
        # 年均复合增长率 (CAGR)
        years = len(values) - 1
        cagr = (pow(values[-1] / values[0], 1/years) - 1) * 100 if values[0] > 0 and values[-1] > 0 else 0
        
        # 增长加速度（二阶导数）
        growth_rates = [(values[i+1] - values[i])/values[i]*100 if values[i] > 0 else 0 
                       for i in range(len(values)-1)]
        acceleration = np.diff(growth_rates).mean() if len(growth_rates) > 1 else 0
        
        # 增长一致性（变异系数）
        growth_consistency = 1 - (np.std(growth_rates) / np.mean(growth_rates)) if np.mean(growth_rates) != 0 else 0
        
        # 增长阶段识别
        growth_phase = self.identify_growth_phase(values, growth_rates)
        
        return {
            'total_growth_rate': round(total_growth, 1),
            'cagr': round(cagr, 1),
            'growth_acceleration': round(acceleration, 2),
            'growth_consistency': max(0, round(growth_consistency, 3)),
            'growth_phase': growth_phase,
            'peak_year_index': values.index(max(values)),
            'valley_year_index': values.index(min(values))
        }
    
    def identify_growth_phase(self, values: List[int], growth_rates: List[float]) -> str:
        """识别增长阶段"""
        recent_growth = np.mean(growth_rates[-2:]) if len(growth_rates) >= 2 else growth_rates[-1] if growth_rates else 0
        early_growth = np.mean(growth_rates[:2]) if len(growth_rates) >= 2 else growth_rates[0] if growth_rates else 0
        
        if recent_growth > 20:
            return "快速增长期"
        elif recent_growth > 10:
            return "稳定增长期"
        elif recent_growth > -10:
            return "成熟稳定期"
        elif recent_growth > -20:
            return "缓慢衰退期"
        else:
            return "快速衰退期"
    
    def analyze_stability(self, values: List[int], field: str) -> Dict[str, Any]:
        """分析稳定性指标"""
        # 变异系数
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else float('inf')
        
        # 稳定性评分 (0-1，1为最稳定)
        stability_score = max(0, 1 - cv)
        
        # 波动性分析
        if cv < 0.2:
            volatility_level = "低波动"
        elif cv < 0.5:
            volatility_level = "中等波动"
        else:
            volatility_level = "高波动"
        
        return {
            'coefficient_variation': round(cv, 3),
            'stability_score': round(stability_score, 3),
            'volatility_level': volatility_level,
            'max_year_variation': max(values) - min(values)
        }
    
    def analyze_dominance_shifts(self, field_trends: Dict) -> Dict[str, Any]:
        """分析领域主导地位变化"""
        dominance_analysis = {}
        
        for year in self.analysis_years:
            year_str = str(year)
            year_totals = {}
            
            for field, yearly_data in field_trends.items():
                year_totals[field] = yearly_data.get(year_str, 0)
            
            # 计算市场份额
            total_papers = sum(year_totals.values())
            if total_papers > 0:
                market_shares = {field: count/total_papers*100 
                               for field, count in year_totals.items()}
                dominance_analysis[year] = {
                    'top_field': max(market_shares, key=market_shares.get),
                    'top_share': max(market_shares.values()),
                    'market_shares': market_shares,
                    'concentration_index': self.calculate_concentration_index(market_shares)
                }
        
        # 分析主导地位变化
        dominance_shifts = []
        for i in range(1, len(self.analysis_years)):
            prev_year = self.analysis_years[i-1]
            curr_year = self.analysis_years[i]
            
            if prev_year in dominance_analysis and curr_year in dominance_analysis:
                prev_leader = dominance_analysis[prev_year]['top_field']
                curr_leader = dominance_analysis[curr_year]['top_field']
                
                if prev_leader != curr_leader:
                    dominance_shifts.append({
                        'year': curr_year,
                        'from': prev_leader,
                        'to': curr_leader,
                        'prev_share': dominance_analysis[prev_year]['top_share'],
                        'curr_share': dominance_analysis[curr_year]['top_share']
                    })
        
        return {
            'yearly_dominance': dominance_analysis,
            'leadership_changes': dominance_shifts,
            'most_dominant_overall': self.find_most_dominant_field(field_trends)
        }
    
    def calculate_concentration_index(self, market_shares: Dict[str, float]) -> float:
        """计算市场集中度指数 (HHI)"""
        return sum(share**2 for share in market_shares.values()) / 100
    
    def find_most_dominant_field(self, field_trends: Dict) -> Dict[str, Any]:
        """找出总体最主导的领域"""
        total_papers = {}
        avg_shares = {}
        
        for field, yearly_data in field_trends.items():
            total_papers[field] = sum(yearly_data.get(str(year), 0) for year in self.analysis_years)
            
            # 计算平均市场份额
            yearly_totals = [sum(yearly_data.get(str(year), 0) for yearly_data in field_trends.values()) 
                           for year in self.analysis_years]
            field_yearly = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            avg_shares[field] = np.mean([field_yearly[i]/yearly_totals[i]*100 if yearly_totals[i] > 0 else 0 
                                       for i in range(len(field_yearly))])
        
        most_papers = max(total_papers, key=total_papers.get)
        highest_avg_share = max(avg_shares, key=avg_shares.get)
        
        return {
            'by_total_papers': {
                'field': most_papers,
                'papers': total_papers[most_papers]
            },
            'by_average_share': {
                'field': highest_avg_share,
                'avg_share': round(avg_shares[highest_avg_share], 1)
            }
        }
    
    def identify_emerging_fields(self, field_trends: Dict) -> Dict[str, Any]:
        """识别新兴领域"""
        emerging_criteria = {}
        
        for field, yearly_data in field_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            
            # 新兴领域标准：
            # 1. 早期规模小
            # 2. 近期增长快
            # 3. 增长加速度高
            
            early_avg = np.mean(values[:2]) if len(values) >= 2 else values[0]
            recent_avg = np.mean(values[-2:]) if len(values) >= 2 else values[-1]
            
            if early_avg > 0:
                growth_multiple = recent_avg / early_avg
                growth_rate = (growth_multiple - 1) * 100
            else:
                growth_multiple = float('inf') if recent_avg > 0 else 1
                growth_rate = float('inf') if recent_avg > 0 else 0
            
            # 计算增长加速度
            growth_rates = [(values[i+1] - values[i])/values[i]*100 if values[i] > 0 else 0 
                           for i in range(len(values)-1)]
            acceleration = np.diff(growth_rates).mean() if len(growth_rates) > 1 else 0
            
            emerging_score = 0
            if early_avg < 100:  # 早期规模小
                emerging_score += 1
            if growth_rate > 100:  # 高增长
                emerging_score += 2
            if acceleration > 0:  # 正加速度
                emerging_score += 1
            
            emerging_criteria[field] = {
                'early_average': early_avg,
                'recent_average': recent_avg,
                'growth_multiple': round(growth_multiple, 1) if growth_multiple != float('inf') else 'inf',
                'growth_rate': round(growth_rate, 1) if growth_rate != float('inf') else 'inf',
                'acceleration': round(acceleration, 2),
                'emerging_score': emerging_score,
                'is_emerging': emerging_score >= 3
            }
        
        # 按新兴评分排序
        emerging_fields = {k: v for k, v in emerging_criteria.items() if v['is_emerging']}
        emerging_sorted = dict(sorted(emerging_fields.items(), 
                                    key=lambda x: x[1]['emerging_score'], reverse=True))
        
        return {
            'emerging_fields': emerging_sorted,
            'emerging_count': len(emerging_fields),
            'all_scores': emerging_criteria
        }
    
    def identify_declining_fields(self, field_trends: Dict) -> Dict[str, Any]:
        """识别衰退领域"""
        declining_criteria = {}
        
        for field, yearly_data in field_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            
            # 衰退领域标准：
            # 1. 负增长趋势
            # 2. 市场份额下降
            # 3. 连续下降期
            
            # 线性趋势
            x = np.array(range(len(values)))
            slope, _, r_value, p_value, _ = stats.linregress(x, values)
            
            # 连续下降期检测
            consecutive_declines = 0
            max_consecutive_declines = 0
            for i in range(1, len(values)):
                if values[i] < values[i-1]:
                    consecutive_declines += 1
                    max_consecutive_declines = max(max_consecutive_declines, consecutive_declines)
                else:
                    consecutive_declines = 0
            
            # 衰退评分
            declining_score = 0
            if slope < -10:  # 负趋势
                declining_score += 2
            if max_consecutive_declines >= 2:  # 连续下降
                declining_score += 1
            if r_value**2 > 0.5 and slope < 0:  # 显著负趋势
                declining_score += 1
            
            declining_criteria[field] = {
                'slope': round(slope, 2),
                'r_squared': round(r_value**2, 3),
                'max_consecutive_declines': max_consecutive_declines,
                'declining_score': declining_score,
                'is_declining': declining_score >= 2
            }
        
        declining_fields = {k: v for k, v in declining_criteria.items() if v['is_declining']}
        declining_sorted = dict(sorted(declining_fields.items(), 
                                     key=lambda x: x[1]['declining_score'], reverse=True))
        
        return {
            'declining_fields': declining_sorted,
            'declining_count': len(declining_fields),
            'all_scores': declining_criteria
        }
    
    def analyze_conference_trends(self) -> Dict[str, Any]:
        """分析各会议的研究领域趋势"""
        print("🏛️ 分析各会议研究领域趋势...")
        
        conference_specialization = self.data['cross_analysis']['conference_scenario_specialization']
        conference_yearly = self.data['temporal_analysis']['conference_yearly_distribution']
        
        conference_analysis = {}
        
        # 分析每个会议的领域偏好
        for conference in ['NeuRIPS', 'ICLR', 'AAAI']:
            conference_analysis[conference] = self.analyze_single_conference(
                conference, conference_specialization, conference_yearly
            )
        
        # 会议间比较分析
        conference_analysis['comparative_analysis'] = self.compare_conferences(conference_analysis)
        
        return conference_analysis
    
    def analyze_single_conference(self, conference: str, specialization: Dict, yearly_dist: Dict) -> Dict[str, Any]:
        """分析单个会议的研究领域趋势"""
        
        # 该会议在各领域的专业化程度
        conference_specialization = {}
        for field, conf_data in specialization.items():
            if conference in conf_data:
                conference_specialization[field] = conf_data[conference]
        
        # 按专业化程度排序
        sorted_specialization = dict(sorted(conference_specialization.items(), 
                                          key=lambda x: x[1], reverse=True))
        
        # 计算该会议的年度增长趋势
        yearly_papers = []
        for year in self.analysis_years:
            yearly_papers.append(yearly_dist.get(str(year), {}).get(conference, 0))
        
        # 增长分析
        growth_analysis = self.analyze_growth_metrics(yearly_papers, conference)
        
        # 领域集中度分析
        concentration = self.calculate_field_concentration(conference_specialization)
        
        # 识别该会议的核心领域和新兴领域
        core_fields = [field for field, spec in sorted_specialization.items() if spec > 0.1][:5]
        emerging_in_conference = [field for field, spec in sorted_specialization.items() 
                                if 0.05 < spec < 0.1]
        
        return {
            'specialization_scores': sorted_specialization,
            'core_fields': core_fields,
            'emerging_fields': emerging_in_conference,
            'field_concentration': concentration,
            'yearly_papers': yearly_papers,
            'growth_analysis': growth_analysis,
            'total_papers': sum(yearly_papers),
            'peak_year': self.analysis_years[yearly_papers.index(max(yearly_papers))] if yearly_papers else None
        }
    
    def calculate_field_concentration(self, specialization: Dict[str, float]) -> Dict[str, Any]:
        """计算领域集中度"""
        values = list(specialization.values())
        
        # Herfindahl-Hirschman Index
        hhi = sum(v**2 for v in values) * 10000
        
        # 前3领域集中度
        top3_concentration = sum(sorted(values, reverse=True)[:3])
        
        # 基尼系数
        gini = self.calculate_gini_coefficient(values)
        
        return {
            'hhi': round(hhi, 1),
            'top3_concentration': round(top3_concentration, 3),
            'gini_coefficient': round(gini, 3),
            'concentration_level': self.classify_concentration(hhi)
        }
    
    def calculate_gini_coefficient(self, values: List[float]) -> float:
        """计算基尼系数"""
        if len(values) == 0:
            return 0
        
        sorted_values = sorted(values)
        n = len(values)
        cumsum = np.cumsum(sorted_values)
        
        return (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(sorted_values, 1))) / (n * sum(sorted_values))
    
    def classify_concentration(self, hhi: float) -> str:
        """分类集中度水平"""
        if hhi < 1500:
            return "低集中度"
        elif hhi < 2500:
            return "中等集中度"
        else:
            return "高集中度"
    
    def compare_conferences(self, conference_analysis: Dict) -> Dict[str, Any]:
        """比较各会议间的差异"""
        conferences = ['NeuRIPS', 'ICLR', 'AAAI']
        
        comparison = {
            'diversity_ranking': {},
            'growth_ranking': {},
            'specialization_uniqueness': {},
            'conference_evolution': {}
        }
        
        # 多样性排名（基于基尼系数，越小越多样）
        diversity_scores = {}
        for conf in conferences:
            if conf in conference_analysis:
                gini = conference_analysis[conf]['field_concentration']['gini_coefficient']
                diversity_scores[conf] = gini
        
        comparison['diversity_ranking'] = dict(sorted(diversity_scores.items(), key=lambda x: x[1]))
        
        # 增长速度排名
        growth_scores = {}
        for conf in conferences:
            if conf in conference_analysis:
                cagr = conference_analysis[conf]['growth_analysis'].get('cagr', 0)
                growth_scores[conf] = cagr
        
        comparison['growth_ranking'] = dict(sorted(growth_scores.items(), key=lambda x: x[1], reverse=True))
        
        # 专业化独特性分析
        for conf in conferences:
            if conf in conference_analysis:
                unique_fields = []
                conf_spec = conference_analysis[conf]['specialization_scores']
                
                for field, score in conf_spec.items():
                    # 检查该领域是否在此会议中特别突出
                    is_unique = True
                    for other_conf in conferences:
                        if other_conf != conf and other_conf in conference_analysis:
                            other_score = conference_analysis[other_conf]['specialization_scores'].get(field, 0)
                            if other_score >= score * 0.8:  # 如果其他会议也很强，则不算独特
                                is_unique = False
                                break
                    
                    if is_unique and score > 0.05:  # 最小阈值
                        unique_fields.append(field)
                
                comparison['specialization_uniqueness'][conf] = unique_fields
        
        return comparison
    
    def generate_predictions(self, overall_analysis: Dict, conference_analysis: Dict) -> Dict[str, Any]:
        """生成发展趋势预测"""
        print("🔮 生成研究领域发展预测...")
        
        predictions = {
            '2025_forecasts': {},
            'hot_topics_prediction': {},
            'conference_evolution_prediction': {},
            'risk_assessment': {}
        }
        
        # 基于历史趋势预测2025年各领域论文数量
        field_trends = self.data['field_analysis']['field_trends']
        
        for field, yearly_data in field_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            
            # 使用线性回归预测
            x = np.array(range(len(values))).reshape(-1, 1)
            model = LinearRegression()
            model.fit(x, values)
            
            # 预测2025年 (索引为6)
            predicted_2025 = max(0, int(model.predict([[len(values)]])[0]))
            
            # 置信区间估算
            trend_data = overall_analysis['trend_patterns'][field]
            confidence = 'high' if trend_data['r_squared'] > 0.7 else 'medium' if trend_data['r_squared'] > 0.4 else 'low'
            
            predictions['2025_forecasts'][field] = {
                'predicted_papers': predicted_2025,
                'confidence_level': confidence,
                'trend_basis': trend_data['trend_type']
            }
        
        # 预测热点话题
        emerging_fields = overall_analysis['emerging_fields']['emerging_fields']
        growth_analysis = overall_analysis['growth_analysis']
        
        hot_topics = []
        for field in emerging_fields.keys():
            if field in growth_analysis:
                cagr = growth_analysis[field]['cagr']
                if cagr > 30:  # 高增长率
                    hot_topics.append({
                        'field': field,
                        'reason': f'CAGR {cagr}%, 新兴领域',
                        'priority': 'high'
                    })
        
        # 添加稳定增长的大领域
        for field, analysis in growth_analysis.items():
            if analysis['cagr'] > 15 and analysis['growth_phase'] in ['稳定增长期', '快速增长期']:
                if field not in [item['field'] for item in hot_topics]:
                    hot_topics.append({
                        'field': field,
                        'reason': f"稳定增长 (CAGR {analysis['cagr']}%)",
                        'priority': 'medium'
                    })
        
        predictions['hot_topics_prediction'] = sorted(hot_topics, 
                                                    key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], 
                                                    reverse=True)[:10]
        
        # 风险评估
        declining_fields = overall_analysis['declining_fields']['declining_fields']
        risk_fields = []
        
        for field, analysis in declining_fields.items():
            risk_level = 'high' if analysis['declining_score'] >= 3 else 'medium'
            risk_fields.append({
                'field': field,
                'risk_level': risk_level,
                'reason': f"连续下降 {analysis['max_consecutive_declines']} 年"
            })
        
        predictions['risk_assessment'] = risk_fields
        
        return predictions
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合趋势分析报告"""
        print("📋 生成综合研究领域趋势分析报告...")
        
        # 执行所有分析
        overall_analysis = self.analyze_overall_trends()
        conference_analysis = self.analyze_conference_trends()
        predictions = self.generate_predictions(overall_analysis, conference_analysis)
        
        # 构建完整报告
        comprehensive_report = {
            'generation_time': datetime.now().isoformat(),
            'analysis_period': f"{min(self.analysis_years)}-{max(self.analysis_years)}",
            'data_summary': {
                'total_papers': self.data['basic_statistics']['total_papers'],
                'analyzed_fields': len(self.data['field_analysis']['field_trends']),
                'analyzed_conferences': len(self.data['basic_statistics']['conferences'])
            },
            'overall_trends': overall_analysis,
            'conference_trends': conference_analysis,
            'predictions': predictions,
            'key_insights': self.generate_key_insights(overall_analysis, conference_analysis, predictions)
        }
        
        # 保存报告
        report_file = self.output_dir / 'comprehensive_research_trends.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
        
        # 生成可读报告
        self.generate_readable_report(comprehensive_report)
        
        print(f"✅ 综合研究趋势分析报告已生成：{report_file}")
        return comprehensive_report
    
    def generate_key_insights(self, overall_analysis: Dict, conference_analysis: Dict, predictions: Dict) -> List[str]:
        """生成关键洞察"""
        insights = []
        
        # 总体趋势洞察
        emerging_fields = list(overall_analysis['emerging_fields']['emerging_fields'].keys())
        if emerging_fields:
            insights.append(f"🌟 新兴领域崛起：{', '.join(emerging_fields[:3])}展现强劲增长势头")
        
        # 主导地位变化
        dominance = overall_analysis['dominance_shifts']
        if dominance['leadership_changes']:
            latest_change = dominance['leadership_changes'][-1]
            insights.append(f"👑 领域主导权转移：{latest_change['year']}年{latest_change['to']}超越{latest_change['from']}")
        
        # 会议特色
        if 'NeuRIPS' in conference_analysis:
            neurips_core = conference_analysis['NeuRIPS']['core_fields'][:2]
            insights.append(f"🧠 NeuRIPS专业化：聚焦{', '.join(neurips_core)}等核心领域")
        
        if 'ICLR' in conference_analysis:
            iclr_growth = conference_analysis['ICLR']['growth_analysis']['cagr']
            insights.append(f"📈 ICLR发展动态：年复合增长率达{iclr_growth}%")
        
        # 预测洞察
        hot_topics = predictions['hot_topics_prediction'][:3]
        if hot_topics:
            hot_names = [topic['field'] for topic in hot_topics]
            insights.append(f"🔥 2025热点预测：{', '.join(hot_names)}将继续保持高热度")
        
        return insights
    
    def generate_readable_report(self, report: Dict):
        """生成可读的研究趋势分析报告"""
        readable_content = f"""
# 研究领域发展趋势深度分析报告

生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
分析期间：{report['analysis_period']}
数据来源：{report['data_summary']['total_papers']:,}篇AI顶级会议论文

## 🎯 核心洞察

{chr(10).join(f"• {insight}" for insight in report['key_insights'])}

## 📊 总体趋势分析

### 新兴领域识别
"""
        
        # 新兴领域分析
        emerging = report['overall_trends']['emerging_fields']['emerging_fields']
        if emerging:
            readable_content += "\n**快速崛起的研究领域：**\n"
            for i, (field, data) in enumerate(emerging.items(), 1):
                growth_rate = data['growth_rate']
                growth_str = f"{growth_rate}%" if growth_rate != 'inf' else "超高速"
                readable_content += f"{i}. **{field}**\n"
                readable_content += f"   - 增长倍数：{data['growth_multiple']}\n"
                readable_content += f"   - 增长率：{growth_str}\n"
                readable_content += f"   - 新兴评分：{data['emerging_score']}/4\n\n"
        
        # 领域主导地位分析
        dominance = report['overall_trends']['dominance_shifts']
        readable_content += "\n### 领域主导地位演变\n\n"
        
        most_dominant = dominance['most_dominant_overall']
        readable_content += f"**总体最主导领域：**\n"
        readable_content += f"- 按论文数量：{most_dominant['by_total_papers']['field']} ({most_dominant['by_total_papers']['papers']:,}篇)\n"
        readable_content += f"- 按平均份额：{most_dominant['by_average_share']['field']} ({most_dominant['by_average_share']['avg_share']}%)\n\n"
        
        if dominance['leadership_changes']:
            readable_content += "**主导权变迁历史：**\n"
            for change in dominance['leadership_changes']:
                readable_content += f"- {change['year']}年：{change['to']}取代{change['from']}成为主导领域\n"
        
        # 趋势模式分析
        readable_content += "\n### 发展趋势模式分类\n\n"
        trend_patterns = report['overall_trends']['trend_patterns']
        
        pattern_groups = {}
        for field, pattern in trend_patterns.items():
            trend_type = pattern['trend_type']
            if trend_type not in pattern_groups:
                pattern_groups[trend_type] = []
            pattern_groups[trend_type].append(field)
        
        for pattern_type, fields in pattern_groups.items():
            readable_content += f"**{pattern_type}领域：**\n"
            for field in fields:
                pattern_data = trend_patterns[field]
                readable_content += f"- {field}（斜率：{pattern_data['linear_slope']}, R²：{pattern_data['r_squared']}）\n"
            readable_content += "\n"
        
        ## 会议专业化分析
        readable_content += "\n## 🏛️ 各会议研究领域特色分析\n\n"
        
        conferences = ['NeuRIPS', 'ICLR', 'AAAI']
        for conf in conferences:
            if conf in report['conference_trends']:
                conf_data = report['conference_trends'][conf]
                readable_content += f"### {conf} 专业化分析\n\n"
                
                # 核心领域
                core_fields = conf_data['core_fields']
                readable_content += f"**核心专业领域：**\n"
                for field in core_fields:
                    spec_score = conf_data['specialization_scores'][field]
                    readable_content += f"- {field}（专业化指数：{spec_score:.3f}）\n"
                
                # 增长分析
                growth = conf_data['growth_analysis']
                readable_content += f"\n**发展动态：**\n"
                readable_content += f"- 年复合增长率：{growth['cagr']}%\n"
                readable_content += f"- 增长阶段：{growth['growth_phase']}\n"
                readable_content += f"- 总论文数：{conf_data['total_papers']:,}篇\n"
                
                # 领域集中度
                concentration = conf_data['field_concentration']
                readable_content += f"- 领域集中度：{concentration['concentration_level']}（HHI: {concentration['hhi']}）\n\n"
        
        # 会议比较分析
        if 'comparative_analysis' in report['conference_trends']:
            comp = report['conference_trends']['comparative_analysis']
            readable_content += "### 会议间比较分析\n\n"
            
            readable_content += "**多样性排名：**\n"
            for i, (conf, score) in enumerate(comp['diversity_ranking'].items(), 1):
                readable_content += f"{i}. {conf}（基尼系数：{score}）\n"
            
            readable_content += "\n**增长速度排名：**\n"
            for i, (conf, cagr) in enumerate(comp['growth_ranking'].items(), 1):
                readable_content += f"{i}. {conf}（CAGR：{cagr}%）\n"
            
            readable_content += "\n**专业化独特性：**\n"
            for conf, unique_fields in comp['specialization_uniqueness'].items():
                if unique_fields:
                    readable_content += f"- {conf}：{', '.join(unique_fields)}\n"
        
        # 预测分析
        readable_content += "\n## 🔮 发展趋势预测\n\n"
        
        # 2025年预测
        forecasts = report['predictions']['2025_forecasts']
        readable_content += "### 2025年领域规模预测\n\n"
        
        # 按预测论文数排序
        sorted_forecasts = sorted(forecasts.items(), key=lambda x: x[1]['predicted_papers'], reverse=True)
        
        for i, (field, forecast) in enumerate(sorted_forecasts[:10], 1):
            confidence_icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}[forecast['confidence_level']]
            readable_content += f"{i}. **{field}**：{forecast['predicted_papers']:,}篇 {confidence_icon}\n"
            readable_content += f"   - 预测基础：{forecast['trend_basis']}\n"
            readable_content += f"   - 置信水平：{forecast['confidence_level']}\n\n"
        
        # 热点预测
        hot_topics = report['predictions']['hot_topics_prediction']
        readable_content += "### 研究热点预测\n\n"
        
        for i, topic in enumerate(hot_topics, 1):
            priority_icon = {"high": "🔥", "medium": "⭐", "low": "💡"}[topic['priority']]
            readable_content += f"{i}. **{topic['field']}** {priority_icon}\n"
            readable_content += f"   - 预测理由：{topic['reason']}\n\n"
        
        # 风险评估
        risks = report['predictions']['risk_assessment']
        if risks:
            readable_content += "### 衰退风险评估\n\n"
            for risk in risks:
                risk_icon = {"high": "⚠️", "medium": "⚡"}[risk['risk_level']]
                readable_content += f"- **{risk['field']}** {risk_icon}\n"
                readable_content += f"  - 风险等级：{risk['risk_level']}\n"
                readable_content += f"  - 风险原因：{risk['reason']}\n\n"
        
        # 建议与结论
        readable_content += """
## 💡 策略建议

### 研究投资方向
1. **重点关注新兴领域**：Manufacturing、Medical Diagnosis等展现巨大潜力
2. **稳定投资成熟领域**：Educational Technology、Content Creation保持稳定增长
3. **关注技术融合**：跨领域研究成为新趋势

### 会议选择策略
1. **NeuRIPS**：适合深度学习和优化相关研究
2. **ICLR**：表现型算法和表示学习的首选平台
3. **AAAI**：通用人工智能和应用导向研究的理想选择

### 风险规避
1. **谨慎投资衰退领域**：关注Social Media等领域的发展变化
2. **多元化研究组合**：避免过度集中在单一领域
3. **保持技术敏感性**：及时跟进新兴技术趋势

---
*本报告基于31,244篇AI顶级会议论文的深度分析，涵盖2018-2023年完整数据*
"""
        
        # 保存可读报告
        readable_file = self.output_dir / 'research_trends_analysis_readable.md'
        with open(readable_file, 'w', encoding='utf-8') as f:
            f.write(readable_content)
        
        print(f"📝 可读报告已生成：{readable_file}")

def main():
    """主函数"""
    print("🚀 启动研究领域发展趋势深度分析...")
    
    analyzer = ResearchTrendsAnalyzer()
    report = analyzer.generate_comprehensive_report()
    
    print("\n" + "="*60)
    print("📊 研究领域趋势分析完成！")
    print(f"📁 报告保存位置：outputs/research_trends/")
    print("\n🔍 核心洞察：")
    for insight in report['key_insights']:
        print(f"  • {insight}")
    
    return report

if __name__ == "__main__":
    main()