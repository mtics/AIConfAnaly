#!/usr/bin/env python3
"""
统一趋势分析器 - 合并了研究领域和应用场景的深度趋势分析
包括总体趋势、分会议趋势、应用场景和技术发展趋势分析
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


class UnifiedTrendAnalyzer:
    """统一趋势分析器 - 综合研究领域、应用场景、技术发展趋势分析"""
    
    def __init__(self, data_path: str = "outputs/analysis/comprehensive_analysis.json"):
        self.data_path = Path(data_path)
        self.data = self.load_data()
        self.output_dir = Path("outputs/trend_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 年份范围
        self.years = list(range(2018, 2025))
        self.analysis_years = list(range(2018, 2024))  # 排除2024年（数据不完整）
        
    def load_data(self) -> Dict:
        """加载分析数据"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """运行综合趋势分析"""
        print("🔍 启动统一趋势分析器...")
        
        comprehensive_results = {
            'metadata': {
                'analysis_time': datetime.now().isoformat(),
                'data_source': str(self.data_path),
                'analysis_years': self.analysis_years
            },
            'research_fields_analysis': self.analyze_research_fields_trends(),
            'application_scenarios_analysis': self.analyze_application_scenarios_trends(),
            'technical_trends_analysis': self.analyze_technical_trends(),
            'conference_analysis': self.analyze_conference_trends(),
            'cross_domain_analysis': self.perform_cross_domain_analysis(),
            'prediction_insights': self.generate_prediction_insights()
        }
        
        # 保存分析结果
        output_file = self.output_dir / "unified_trends_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 统一趋势分析完成，结果保存至: {output_file}")
        return comprehensive_results
    
    def analyze_research_fields_trends(self) -> Dict[str, Any]:
        """分析研究领域发展趋势（增强版）"""
        print("📊 分析研究领域发展趋势...")
        
        field_trends = self.data['field_analysis']['field_trends']
        
        analysis_results = {
            'overall_trends': {},
            'trend_patterns': {},
            'growth_analysis': {},
            'dominance_shifts': {},
            'emerging_fields': {},
            'declining_fields': {},
            'stability_analysis': {}
        }
        
        for field, yearly_data in field_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            
            # 基础统计
            total_papers = sum(values)
            peak_year = self.analysis_years[values.index(max(values))] if values else 2018
            peak_value = max(values) if values else 0
            
            # 增长率计算
            early_avg = np.mean(values[:3]) if len(values) >= 3 else np.mean(values)
            recent_avg = np.mean(values[3:6]) if len(values) >= 6 else np.mean(values[3:])
            growth_rate = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
            
            # 趋势模式分析
            trend_pattern = self.analyze_trend_pattern(values, field)
            
            # 增长分析
            growth_metrics = self.analyze_growth_metrics(values, field)
            
            # 稳定性分析
            stability = self.analyze_stability(values, field)
            
            analysis_results['overall_trends'][field] = {
                'total_papers': total_papers,
                'peak_year': peak_year,
                'peak_value': peak_value,
                'growth_rate': round(growth_rate, 1),
                'trend_coefficient': trend_pattern.get('linear_slope', 0),
                'trend_type': trend_pattern.get('trend_type', '未知'),
                'yearly_values': values
            }
            
            analysis_results['trend_patterns'][field] = trend_pattern
            analysis_results['growth_analysis'][field] = growth_metrics
            analysis_results['stability_analysis'][field] = stability
        
        # 领域主导地位变化
        analysis_results['dominance_shifts'] = self.analyze_dominance_shifts(field_trends)
        
        # 新兴和衰退领域识别
        analysis_results['emerging_fields'] = self.identify_emerging_fields(field_trends)
        analysis_results['declining_fields'] = self.identify_declining_fields(field_trends)
        
        return analysis_results
    
    def analyze_trend_pattern(self, values: List[int], field: str) -> Dict[str, Any]:
        """分析单个领域的趋势模式"""
        if not values or len(values) < 2:
            return {'trend_type': '数据不足', 'linear_slope': 0}
            
        # 线性趋势
        x = np.array(range(len(values)))
        linear_slope, linear_intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # 多项式趋势（二次）
        try:
            poly_features = PolynomialFeatures(degree=2)
            x_poly = poly_features.fit_transform(x.reshape(-1, 1))
            poly_model = LinearRegression()
            poly_model.fit(x_poly, values)
            poly_score = poly_model.score(x_poly, values)
        except:
            poly_score = 0
        
        # 趋势类型判断
        if abs(linear_slope) < 10:
            trend_type = "稳定型"
        elif linear_slope > 50:
            trend_type = "强增长型"
        elif linear_slope > 20:
            trend_type = "增长型"
        elif linear_slope > -20:
            trend_type = "缓慢增长型"
        else:
            trend_type = "下降型"
        
        return {
            'linear_slope': round(linear_slope, 2),
            'linear_intercept': round(linear_intercept, 2),
            'r_squared': round(r_value**2, 3),
            'p_value': round(p_value, 4),
            'poly_score': round(poly_score, 3),
            'trend_type': trend_type,
            'trend_strength': 'strong' if abs(linear_slope) > 30 else 'moderate' if abs(linear_slope) > 10 else 'weak'
        }
    
    def analyze_growth_metrics(self, values: List[int], field: str) -> Dict[str, Any]:
        """分析增长指标"""
        if not values or len(values) < 2:
            return {'growth_type': '数据不足'}
            
        # 年均增长率 (CAGR)
        start_value = values[0] if values[0] > 0 else 1
        end_value = values[-1] if values[-1] > 0 else 1
        years_span = len(values) - 1
        cagr = ((end_value / start_value) ** (1/years_span) - 1) * 100 if years_span > 0 else 0
        
        # 波动性 (标准差)
        volatility = np.std(values) / np.mean(values) * 100 if np.mean(values) > 0 else 0
        
        # 增长加速度
        if len(values) >= 3:
            early_growth = (values[1] - values[0]) / values[0] * 100 if values[0] > 0 else 0
            recent_growth = (values[-1] - values[-2]) / values[-2] * 100 if values[-2] > 0 else 0
            acceleration = recent_growth - early_growth
        else:
            acceleration = 0
        
        return {
            'cagr': round(cagr, 2),
            'volatility': round(volatility, 2),
            'acceleration': round(acceleration, 2),
            'growth_consistency': 'high' if volatility < 20 else 'medium' if volatility < 50 else 'low'
        }
    
    def analyze_stability(self, values: List[int], field: str) -> Dict[str, Any]:
        """分析稳定性指标"""
        if not values:
            return {'stability_score': 0}
            
        # 变异系数
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else float('inf')
        
        # 稳定性评分 (0-100)
        stability_score = max(0, 100 - cv * 100)
        
        return {
            'coefficient_of_variation': round(cv, 3),
            'stability_score': round(stability_score, 1),
            'stability_level': 'high' if stability_score > 70 else 'medium' if stability_score > 40 else 'low'
        }
    
    def analyze_application_scenarios_trends(self) -> Dict[str, Any]:
        """分析应用场景发展趋势"""
        print("🎯 分析应用场景发展趋势...")
        
        scenario_trends = self.data['task_scenario_analysis']['scenario_yearly_trends']
        scenarios_analysis = {}
        
        for scenario, yearly_data in scenario_trends.items():
            if scenario == "General Research":  # 跳过通用研究
                continue
                
            values = [yearly_data.get(str(year), 0) for year in self.years]
            
            # 基础分析
            total_applications = sum(values)
            if total_applications == 0:
                continue
                
            # 趋势分析
            trend_pattern = self.analyze_trend_pattern(values, scenario)
            growth_metrics = self.analyze_growth_metrics(values, scenario)
            
            scenarios_analysis[scenario] = {
                'total_applications': total_applications,
                'trend_pattern': trend_pattern,
                'growth_metrics': growth_metrics,
                'yearly_values': values,
                'market_share_latest': round(values[-1] / sum(values) * 100, 2) if sum(values) > 0 else 0
            }
        
        return scenarios_analysis
    
    def analyze_technical_trends(self) -> Dict[str, Any]:
        """分析技术发展趋势"""
        print("🔬 分析技术发展趋势...")
        
        technical_trends = self.data.get('technical_trend_analysis', {})
        if not technical_trends:
            return {'error': '技术趋势数据不可用'}
        
        trends_analysis = {}
        
        for tech, yearly_data in technical_trends.get('tech_yearly_trends', {}).items():
            values = [yearly_data.get(str(year), 0) for year in self.years]
            
            if sum(values) == 0:
                continue
                
            trend_pattern = self.analyze_trend_pattern(values, tech)
            growth_metrics = self.analyze_growth_metrics(values, tech)
            
            trends_analysis[tech] = {
                'trend_pattern': trend_pattern,
                'growth_metrics': growth_metrics,
                'yearly_values': values,
                'adoption_rate': round(sum(values) / len(values), 1)
            }
        
        return trends_analysis
    
    def analyze_conference_trends(self) -> Dict[str, Any]:
        """分析会议发展趋势"""
        print("🏛️ 分析会议发展趋势...")
        
        conference_analysis = self.data.get('conference_analysis', {})
        yearly_stats = conference_analysis.get('yearly_statistics', {})
        
        conf_trends = {}
        
        for year, year_data in yearly_stats.items():
            for conf, count in year_data.items():
                if conf not in conf_trends:
                    conf_trends[conf] = {}
                conf_trends[conf][year] = count
        
        # 分析每个会议的趋势
        conference_trend_analysis = {}
        for conf, yearly_data in conf_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.years]
            
            trend_pattern = self.analyze_trend_pattern(values, conf)
            growth_metrics = self.analyze_growth_metrics(values, conf)
            
            conference_trend_analysis[conf] = {
                'trend_pattern': trend_pattern,
                'growth_metrics': growth_metrics,
                'yearly_values': values,
                'total_papers': sum(values)
            }
        
        return conference_trend_analysis
    
    def analyze_dominance_shifts(self, field_trends: Dict) -> Dict[str, Any]:
        """分析领域主导地位变化"""
        dominance_shifts = {}
        
        for year in self.analysis_years:
            year_str = str(year)
            year_totals = {field: data.get(year_str, 0) for field, data in field_trends.items()}
            total_papers = sum(year_totals.values())
            
            if total_papers > 0:
                year_percentages = {field: count/total_papers*100 for field, count in year_totals.items()}
                dominance_shifts[year_str] = year_percentages
        
        return dominance_shifts
    
    def identify_emerging_fields(self, field_trends: Dict) -> Dict[str, Any]:
        """识别新兴领域"""
        emerging_fields = {}
        
        for field, yearly_data in field_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            
            # 新兴领域判断：后期增长显著大于前期
            if len(values) >= 4:
                early_sum = sum(values[:2])
                recent_sum = sum(values[-2:])
                
                if early_sum < 50 and recent_sum > early_sum * 3:  # 前期基数小，后期增长3倍以上
                    growth_factor = recent_sum / max(early_sum, 1)
                    emerging_fields[field] = {
                        'growth_factor': round(growth_factor, 2),
                        'early_sum': early_sum,
                        'recent_sum': recent_sum,
                        'emerging_score': round(growth_factor * recent_sum / 100, 2)
                    }
        
        return emerging_fields
    
    def identify_declining_fields(self, field_trends: Dict) -> Dict[str, Any]:
        """识别衰退领域"""
        declining_fields = {}
        
        for field, yearly_data in field_trends.items():
            values = [yearly_data.get(str(year), 0) for year in self.analysis_years]
            
            # 衰退领域判断：显著下降趋势
            if len(values) >= 4:
                early_avg = np.mean(values[:3])
                recent_avg = np.mean(values[-3:])
                
                if early_avg > 20 and recent_avg < early_avg * 0.7:  # 前期有一定规模，后期下降30%以上
                    decline_rate = (early_avg - recent_avg) / early_avg * 100
                    declining_fields[field] = {
                        'decline_rate': round(decline_rate, 2),
                        'early_avg': round(early_avg, 1),
                        'recent_avg': round(recent_avg, 1),
                        'decline_severity': 'severe' if decline_rate > 50 else 'moderate'
                    }
        
        return declining_fields
    
    def perform_cross_domain_analysis(self) -> Dict[str, Any]:
        """执行跨域分析"""
        print("🔗 执行跨域分析...")
        
        # 研究领域与应用场景的关联分析
        field_scenario_correlation = {}
        
        # 技术趋势与会议的关联分析
        tech_conference_correlation = {}
        
        return {
            'field_scenario_correlation': field_scenario_correlation,
            'tech_conference_correlation': tech_conference_correlation,
            'interdisciplinary_trends': {}
        }
    
    def generate_prediction_insights(self) -> Dict[str, Any]:
        """生成预测洞察"""
        print("🔮 生成预测洞察...")
        
        predictions = {
            'next_year_predictions': {},
            'trend_continuity_analysis': {},
            'potential_breakthrough_areas': {},
            'investment_recommendations': {}
        }
        
        return predictions


def main():
    """主函数 - 运行统一趋势分析"""
    analyzer = UnifiedTrendAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    print("\n📋 分析摘要:")
    print(f"- 研究领域分析: {len(results['research_fields_analysis']['overall_trends'])} 个领域")
    print(f"- 应用场景分析: {len(results['application_scenarios_analysis'])} 个场景")
    print(f"- 会议趋势分析: {len(results['conference_analysis'])} 个会议")
    
    return results


if __name__ == "__main__":
    main()