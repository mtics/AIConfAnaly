"""
统一分析器 - 整合所有分析功能
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedAnalyzer:
    """统一分析器 - 处理所有论文数据分析与统计"""
    
    def __init__(self, data_dir: str = "outputs/data/raw"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("outputs/analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 任务场景分析器
        self.scenario_analyzer = TaskScenarioAnalyzer()
        
        logger.info("UnifiedAnalyzer initialized")
    
    def load_all_data(self) -> pd.DataFrame:
        """加载所有原始数据"""
        all_papers = []
        
        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    papers = json.load(f)
                    all_papers.extend(papers)
                    logger.info(f"Loaded {len(papers)} papers from {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        df = pd.DataFrame(all_papers)
        logger.info(f"Total papers loaded: {len(df)}")
        
        return df
    
    def perform_comprehensive_analysis(self) -> Dict[str, Any]:
        """执行综合分析"""
        logger.info("Starting comprehensive analysis...")
        
        # 1. 加载数据
        df = self.load_all_data()
        
        # 2. 数据清理和预处理
        df = self.clean_data(df)
        
        # 3. 任务场景分析
        df = self.scenario_analyzer.analyze_paper_task_scenario(df)
        
        # 4. 各种统计分析
        analysis_results = {
            'basic_statistics': self.calculate_basic_statistics(df),
            'temporal_analysis': self.analyze_temporal_trends(df),
            'conference_analysis': self.analyze_conferences(df),
            'task_scenario_analysis': self.analyze_task_scenarios(df),
            'technical_trend_analysis': self.analyze_technical_trends(df),
            'field_analysis': self.analyze_research_fields(df),
            'keyword_analysis': self.analyze_keywords(df),
            'emerging_trends': self.identify_emerging_trends(df),
            'cross_analysis': self.perform_cross_analysis(df),
            'quality_metrics': self.calculate_quality_metrics(df),
            'prediction_insights': self.generate_prediction_insights(df)
        }
        
        # 5. 保存分析结果
        self.save_analysis_results(analysis_results, df)
        
        logger.info("Comprehensive analysis completed")
        return analysis_results
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清理"""
        logger.info("Cleaning data...")
        
        # 确保必要字段存在
        required_fields = ['title', 'abstract', 'conference', 'year']
        for field in required_fields:
            if field not in df.columns:
                df[field] = ''
        
        # 清理年份数据
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year'])
        df['year'] = df['year'].astype(int)
        
        # 清理文本字段
        for field in ['title', 'abstract']:
            df[field] = df[field].fillna('').astype(str)
        
        # 过滤有效数据
        df = df[
            (df['title'].str.len() > 10) & 
            (df['abstract'].str.len() > 50) &
            (df['year'] >= 2018) & 
            (df['year'] <= 2024)
        ]
        
        logger.info(f"Data cleaned. Remaining papers: {len(df)}")
        return df
    
    def calculate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """基础统计"""
        return {
            'total_papers': len(df),
            'year_range': [int(df['year'].min()), int(df['year'].max())],
            'conferences': list(df['conference'].unique()),
            'conference_counts': df['conference'].value_counts().to_dict(),
            'yearly_counts': df['year'].value_counts().sort_index().to_dict(),
            'avg_title_length': df['title'].str.len().mean(),
            'avg_abstract_length': df['abstract'].str.len().mean(),
            'papers_per_year_avg': len(df) / df['year'].nunique()
        }
    
    def analyze_temporal_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """时间趋势分析"""
        yearly_stats = df.groupby('year').agg({
            'title': 'count',
            'conference': lambda x: x.nunique()
        }).rename(columns={'title': 'paper_count', 'conference': 'active_conferences'})
        
        # 计算增长率
        growth_rates = yearly_stats['paper_count'].pct_change().fillna(0)
        
        # 会议年度分布
        conf_yearly = df.groupby(['conference', 'year']).size().unstack(fill_value=0)
        
        return {
            'yearly_paper_counts': yearly_stats['paper_count'].to_dict(),
            'yearly_growth_rates': growth_rates.to_dict(),
            'conference_yearly_distribution': conf_yearly.to_dict(),
            'peak_year': int(yearly_stats['paper_count'].idxmax()),
            'peak_count': int(yearly_stats['paper_count'].max()),
            'total_growth_rate': (yearly_stats['paper_count'].iloc[-1] / yearly_stats['paper_count'].iloc[0] - 1) * 100
        }
    
    def analyze_conferences(self, df: pd.DataFrame) -> Dict[str, Any]:
        """会议分析"""
        conf_stats = df.groupby('conference').agg({
            'title': 'count',
            'year': ['min', 'max', 'nunique'],
            'abstract': lambda x: x.str.len().mean()
        }).round(2)
        
        conf_stats.columns = ['paper_count', 'first_year', 'last_year', 'active_years', 'avg_abstract_length']
        
        # 会议影响力评分（基于论文数量、活跃年份等）
        conf_stats['influence_score'] = (
            conf_stats['paper_count'] / conf_stats['paper_count'].max() * 0.6 +
            conf_stats['active_years'] / conf_stats['active_years'].max() * 0.4
        )
        
        return {
            'conference_statistics': conf_stats.to_dict('index'),
            'top_conferences': conf_stats.nlargest(5, 'paper_count').index.tolist(),
            'most_consistent': conf_stats.nlargest(3, 'active_years').index.tolist(),
            'conference_rankings': conf_stats.sort_values('influence_score', ascending=False).to_dict('index')
        }
    
    def analyze_task_scenarios(self, df: pd.DataFrame) -> Dict[str, Any]:
        """任务场景分析"""
        if 'application_scenario' not in df.columns:
            return {}
        
        # 应用场景分布
        scenario_dist = df['application_scenario'].value_counts()
        task_dist = df['task_type'].value_counts()
        
        # 场景-任务交叉分析
        cross_table = pd.crosstab(df['application_scenario'], df['task_type'])
        
        # 置信度分析
        conf_stats = df.groupby('application_scenario').agg({
            'scenario_confidence': ['mean', 'std', 'min', 'max'],
            'title': 'count'
        }).round(3)
        
        # 年度趋势
        scenario_trends = df.groupby(['year', 'application_scenario']).size().unstack(fill_value=0)
        
        return {
            'scenario_distribution': scenario_dist.to_dict(),
            'task_type_distribution': task_dist.to_dict(),
            'scenario_task_cross_table': cross_table.to_dict(),
            'confidence_statistics': conf_stats.to_dict(),
            'scenario_yearly_trends': scenario_trends.to_dict(),
            'top_scenarios': scenario_dist.head(10).index.tolist(),
            'emerging_scenarios': self.identify_emerging_scenarios(df)
        }
    
    def analyze_technical_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """技术趋势分析"""
        if 'technical_trend' not in df.columns:
            return {}
        
        # 技术趋势分布
        trend_dist = df['technical_trend'].value_counts()
        
        # 技术趋势年度变化
        trend_yearly = df.groupby(['year', 'technical_trend']).size().unstack(fill_value=0)
        
        # 技术趋势置信度统计
        trend_conf_stats = df.groupby('technical_trend').agg({
            'trend_confidence': ['mean', 'std', 'count'],
            'title': 'count'
        }).round(3)
        
        # 会议-技术趋势交叉分析
        conf_trend_cross = pd.crosstab(df['conference'], df['technical_trend'])
        
        # 技术成熟度分析（基于论文数量和年度分布）
        tech_maturity = {}
        for trend in trend_dist.index:
            trend_papers = df[df['technical_trend'] == trend]
            year_spread = trend_papers['year'].max() - trend_papers['year'].min()
            paper_count = len(trend_papers)
            
            # 成熟度评分：年份跨度 * 0.3 + 论文数量归一化 * 0.7
            maturity_score = (year_spread / 7) * 0.3 + (paper_count / trend_dist.max()) * 0.7
            tech_maturity[trend] = round(maturity_score, 3)
        
        # 新兴技术识别（近年来快速增长的技术）
        emerging_tech = {}
        recent_years = [2022, 2023, 2024]
        for trend in trend_dist.index:
            recent_count = len(df[(df['technical_trend'] == trend) & (df['year'].isin(recent_years))])
            if recent_count >= 5:  # 至少5篇论文
                historical_count = len(df[(df['technical_trend'] == trend) & (~df['year'].isin(recent_years))])
                growth_rate = (recent_count - historical_count) / max(historical_count, 1)
                if growth_rate > 0.3:  # 增长超过30%
                    emerging_tech[trend] = {
                        'recent_papers': recent_count,
                        'historical_papers': historical_count,
                        'growth_rate': round(growth_rate * 100, 1)
                    }
        
        return {
            'trend_distribution': trend_dist.to_dict(),
            'trend_yearly_evolution': trend_yearly.to_dict(),
            'trend_confidence_stats': trend_conf_stats.to_dict(),
            'conference_trend_specialization': conf_trend_cross.to_dict(),
            'technology_maturity_scores': tech_maturity,
            'emerging_technologies': emerging_tech,
            'top_technical_trends': trend_dist.head(10).index.tolist(),
            'trend_diversity_index': self.calculate_diversity_index(trend_dist)
        }
    
    def analyze_research_fields(self, df: pd.DataFrame) -> Dict[str, Any]:
        """研究领域分析"""
        # 基于任务场景分析来分析研究领域
        if 'application_scenario' in df.columns:
            field_dist = df['application_scenario'].value_counts()
            
            # 领域年度趋势
            field_trends = {}
            for field in field_dist.index:
                field_data = df[df['application_scenario'] == field]
                yearly_counts = field_data.groupby('year').size()
                field_trends[field] = yearly_counts.to_dict()
            
            return {
                'field_distribution': field_dist.to_dict(),
                'field_trends': field_trends,
                'field_diversity_index': self.calculate_diversity_index(field_dist),
                'top_research_fields': field_dist.head(10).to_dict()
            }
        
        return {}
    
    def analyze_keywords(self, df: pd.DataFrame) -> Dict[str, Any]:
        """关键词分析"""
        # 简化的关键词分析
        import re
        from collections import Counter
        
        all_words = []
        
        for idx, row in df.iterrows():
            text = f"{row.get('title', '')} {row.get('abstract', '')}".lower()
            # 简单的词提取
            words = re.findall(r'\b[a-z]{3,}\b', text)
            # 过滤常见停用词
            stop_words = {'the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'can', 'use', 'used', 'using', 'based', 'method', 'approach', 'paper', 'model', 'models', 'data', 'results', 'show', 'shows'}
            words = [w for w in words if w not in stop_words and len(w) > 3]
            all_words.extend(words)
        
        keyword_freq = Counter(all_words)
        
        return {
            'top_keywords': dict(keyword_freq.most_common(50)),
            'unique_keywords_count': len(keyword_freq),
            'total_word_instances': len(all_words)
        }
    
    def identify_emerging_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """识别新兴趋势"""
        recent_years = [2022, 2023, 2024]
        historical_years = [2018, 2019, 2020, 2021]
        
        recent_data = df[df['year'].isin(recent_years)]
        historical_data = df[df['year'].isin(historical_years)]
        
        emerging_trends = {}
        
        # 新兴应用场景
        if 'application_scenario' in df.columns:
            recent_scenarios = recent_data['application_scenario'].value_counts()
            historical_scenarios = historical_data['application_scenario'].value_counts()
            
            for scenario in recent_scenarios.index:
                recent_count = recent_scenarios.get(scenario, 0)
                historical_count = historical_scenarios.get(scenario, 0)
                
                if recent_count >= 10:  # 至少10篇论文
                    growth_rate = (recent_count - historical_count) / max(historical_count, 1)
                    if growth_rate > 0.5:  # 增长超过50%
                        emerging_trends[scenario] = {
                            'recent_papers': recent_count,
                            'historical_papers': historical_count,
                            'growth_rate': round(growth_rate * 100, 1)
                        }
        
        return {
            'emerging_application_scenarios': emerging_trends,
            'hot_topics': self.identify_hot_topics(recent_data),
            'technology_momentum': self.calculate_technology_momentum(df)
        }
    
    def perform_cross_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """交叉分析"""
        cross_analysis = {}
        
        # 会议-应用场景交叉
        if 'application_scenario' in df.columns:
            conf_scenario = pd.crosstab(df['conference'], df['application_scenario'], normalize='index')
            cross_analysis['conference_scenario_specialization'] = conf_scenario.to_dict()
        
        # 年份-技术趋势交叉
        if 'task_type' in df.columns:
            year_task = pd.crosstab(df['year'], df['task_type'], normalize='index')
            cross_analysis['yearly_task_evolution'] = year_task.to_dict()
        
        return cross_analysis
    
    def calculate_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """质量指标计算"""
        return {
            'data_completeness': {
                'title_complete': (df['title'].str.len() > 0).mean() * 100,
                'abstract_complete': (df['abstract'].str.len() > 0).mean() * 100,
                'year_valid': (df['year'].between(2018, 2024)).mean() * 100
            },
            'analysis_coverage': {
                'with_scenario_analysis': (df['application_scenario'].notna()).mean() * 100 if 'application_scenario' in df.columns else 0,
                'high_confidence_scenarios': (df['scenario_confidence'] > 0.7).mean() * 100 if 'scenario_confidence' in df.columns else 0
            },
            'data_quality_score': self.calculate_overall_quality_score(df)
        }
    
    def generate_prediction_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成预测洞察"""
        insights = {}
        
        if len(df) > 100:  # 确保有足够数据
            # 预测2025年论文数量
            yearly_counts = df['year'].value_counts().sort_index()
            if len(yearly_counts) >= 3:
                recent_trend = yearly_counts.tail(3).mean()
                insights['predicted_2025_papers'] = int(recent_trend * 1.1)  # 保守增长10%
            
            # 预测热门领域
            if 'application_scenario' in df.columns:
                scenario_growth = self.calculate_scenario_growth_momentum(df)
                insights['predicted_hot_scenarios'] = list(scenario_growth.keys())[:5]
        
        return insights
    
    def save_analysis_results(self, analysis_results: Dict[str, Any], df: pd.DataFrame):
        """保存分析结果"""
        # 转换tuple keys为字符串keys以便JSON序列化
        def convert_keys(obj):
            if isinstance(obj, dict):
                new_dict = {}
                for key, value in obj.items():
                    if isinstance(key, tuple):
                        new_key = str(key)
                    else:
                        new_key = key
                    new_dict[new_key] = convert_keys(value)
                return new_dict
            elif isinstance(obj, list):
                return [convert_keys(item) for item in obj]
            else:
                return obj
        
        # 转换分析结果
        serializable_results = convert_keys(analysis_results)
        
        # 保存JSON格式结果
        with open(self.output_dir / 'comprehensive_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存处理后的数据
        df.to_csv(self.output_dir / 'processed_papers.csv', index=False, encoding='utf-8')
        
        # 生成摘要报告
        self.generate_summary_report(analysis_results)
        
        logger.info(f"Analysis results saved to {self.output_dir}")
    
    def generate_summary_report(self, analysis_results: Dict[str, Any]):
        """生成摘要报告"""
        basic = analysis_results['basic_statistics']
        temporal = analysis_results['temporal_analysis']
        
        summary = f"""
# 会议论文综合分析报告

## 基础统计
- 总论文数: {basic['total_papers']:,}
- 时间跨度: {basic['year_range'][0]} - {basic['year_range'][1]}
- 涵盖会议: {len(basic['conferences'])}个
- 年均论文数: {basic['papers_per_year_avg']:.0f}

## 发展趋势
- 高峰年份: {temporal['peak_year']} ({temporal['peak_count']:,}篇)
- 整体增长率: {temporal['total_growth_rate']:.1f}%
- 顶级会议: {', '.join(analysis_results['conference_analysis']['top_conferences'][:3])}

## 研究热点
"""
        
        if 'task_scenario_analysis' in analysis_results and analysis_results['task_scenario_analysis']:
            top_scenarios = analysis_results['task_scenario_analysis']['top_scenarios'][:5]
            summary += f"- 热门应用场景: {', '.join(top_scenarios)}\n"
        
        if 'emerging_trends' in analysis_results:
            emerging = analysis_results['emerging_trends']['emerging_application_scenarios']
            if emerging:
                summary += f"- 新兴领域: {', '.join(list(emerging.keys())[:3])}\n"
        
        summary += f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        with open(self.output_dir / 'summary_report.md', 'w', encoding='utf-8') as f:
            f.write(summary)
    
    # 辅助方法
    def calculate_diversity_index(self, distribution):
        """计算多样性指数"""
        if len(distribution) <= 1:
            return 0.0
        total = distribution.sum()
        entropy = -sum((count/total) * np.log2(count/total) for count in distribution if count > 0)
        max_entropy = np.log2(len(distribution))
        return entropy / max_entropy if max_entropy > 0 else 0
    
    def identify_emerging_scenarios(self, df: pd.DataFrame) -> List[str]:
        """识别新兴场景"""
        if 'application_scenario' not in df.columns:
            return []
        
        recent_data = df[df['year'] >= 2022]
        scenario_counts = recent_data['application_scenario'].value_counts()
        
        # 返回论文数量适中但增长快的场景
        emerging = []
        for scenario, count in scenario_counts.items():
            if 5 <= count <= 50 and scenario != 'General Research':
                emerging.append(scenario)
        
        return emerging[:10]
    
    def analyze_keyword_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析关键词趋势"""
        # 简化实现
        return {"status": "keyword trends analysis would be implemented here"}
    
    def identify_hot_topics(self, recent_data: pd.DataFrame) -> List[str]:
        """识别热门话题"""
        if 'application_scenario' in recent_data.columns:
            return recent_data['application_scenario'].value_counts().head(5).index.tolist()
        return []
    
    def calculate_technology_momentum(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算技术动力"""
        # 简化实现
        if 'task_type' in df.columns:
            return df['task_type'].value_counts().head(5).to_dict()
        return {}
    
    def calculate_overall_quality_score(self, df: pd.DataFrame) -> float:
        """计算整体质量评分"""
        scores = []
        
        # 数据完整性
        scores.append((df['title'].str.len() > 10).mean())
        scores.append((df['abstract'].str.len() > 50).mean())
        scores.append((df['year'].between(2018, 2024)).mean())
        
        # 分析覆盖率
        if 'application_scenario' in df.columns:
            scores.append((df['application_scenario'].notna()).mean())
        
        return sum(scores) / len(scores) * 100
    
    def calculate_scenario_growth_momentum(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算场景增长动力"""
        if 'application_scenario' not in df.columns:
            return {}
        
        momentum = {}
        for scenario in df['application_scenario'].unique():
            if scenario and scenario != 'General Research':
                scenario_data = df[df['application_scenario'] == scenario]
                yearly_counts = scenario_data.groupby('year').size()
                
                if len(yearly_counts) >= 3:
                    # 计算增长趋势
                    recent_avg = yearly_counts.tail(2).mean()
                    historical_avg = yearly_counts.head(-2).mean() if len(yearly_counts) > 2 else yearly_counts.mean()
                    
                    if historical_avg > 0:
                        momentum[scenario] = recent_avg / historical_avg
        
        # 按动力排序
        return dict(sorted(momentum.items(), key=lambda x: x[1], reverse=True))


# 任务场景分析器简化版本
class TaskScenarioAnalyzer:
    """简化的任务场景分析器"""
    
    def __init__(self):
        self.application_scenarios = {
            # 医疗健康 - 细化为更具体的子领域
            'Medical Imaging & Radiology': ['medical imaging', 'radiology', 'ct scan', 'mri', 'x-ray', 'ultrasound', 'mammography', 'pathology imaging'],
            'Clinical Diagnosis & Decision Support': ['clinical diagnosis', 'diagnostic', 'clinical decision', 'disease detection', 'symptom analysis', 'patient assessment'],
            'Drug Discovery & Molecular Design': ['drug discovery', 'pharmaceutical', 'molecular design', 'compound', 'therapeutic', 'protein folding', 'chemical'],
            'Genomics & Precision Medicine': ['genomics', 'genetics', 'precision medicine', 'personalized medicine', 'biomarker', 'gene therapy', 'dna sequencing'],
            'Mental Health & Neuropsychology': ['mental health', 'psychology', 'neuropsychology', 'cognitive assessment', 'depression', 'anxiety', 'ptsd', 'autism'],
            'Epidemiology & Public Health': ['epidemiology', 'public health', 'disease surveillance', 'health monitoring', 'outbreak detection', 'population health'],
            'Medical Robotics & Surgery': ['medical robotics', 'surgical robotics', 'minimally invasive surgery', 'robotic surgery', 'surgical planning'],
            'Telemedicine & Remote Healthcare': ['telemedicine', 'remote healthcare', 'digital health', 'mobile health', 'telehealth', 'remote monitoring'],
            
            # 交通与自动驾驶 - 详细细分
            'Autonomous Vehicle Control': ['autonomous driving', 'self-driving', 'vehicle control', 'autonomous navigation', 'path planning', 'motion planning'],
            'Advanced Driver Assistance': ['adas', 'driver assistance', 'collision avoidance', 'lane keeping', 'adaptive cruise control', 'parking assistance'],
            'Traffic Flow Optimization': ['traffic optimization', 'traffic flow', 'traffic signal', 'congestion management', 'route optimization'],
            'Smart Transportation Infrastructure': ['intelligent transportation', 'smart roads', 'v2x communication', 'connected vehicles', 'infrastructure'],
            'Vehicle Safety & Monitoring': ['vehicle safety', 'crash detection', 'driver monitoring', 'fatigue detection', 'behavior analysis'],
            'Logistics & Supply Chain': ['logistics optimization', 'supply chain', 'delivery optimization', 'warehouse automation', 'last mile delivery'],
            
            # 金融科技 - 更细分的子领域
            'Algorithmic Trading & HFT': ['algorithmic trading', 'high frequency trading', 'market making', 'quantitative trading', 'trading algorithms'],
            'Risk Management & Compliance': ['risk management', 'financial risk', 'credit risk', 'operational risk', 'compliance', 'regulatory'],
            'Fraud Detection & AML': ['fraud detection', 'anti-money laundering', 'aml', 'financial crime', 'suspicious activity', 'transaction monitoring'],
            'Credit Scoring & Underwriting': ['credit scoring', 'credit assessment', 'loan underwriting', 'default prediction', 'creditworthiness'],
            'Robo-Advisory & Wealth Management': ['robo-advisory', 'wealth management', 'portfolio optimization', 'investment advisory', 'asset allocation'],
            'Digital Payments & Blockchain': ['digital payments', 'payment processing', 'blockchain', 'cryptocurrency', 'defi', 'digital currency'],
            'InsurTech & Claims Processing': ['insurance technology', 'insurtech', 'claims processing', 'actuarial science', 'insurance pricing'],
            
            # 智慧城市与环境 - 详细子领域
            'Smart City Infrastructure': ['smart city', 'urban planning', 'smart infrastructure', 'city management', 'urban analytics'],
            'Smart Energy & Grid Management': ['smart grid', 'energy management', 'renewable energy', 'energy optimization', 'power systems'],
            'Environmental Monitoring & Climate': ['environmental monitoring', 'air quality', 'water quality', 'climate modeling', 'pollution detection'],
            'Smart Building & IoT': ['smart building', 'building automation', 'iot sensors', 'facility management', 'energy efficiency'],
            'Urban Mobility & Public Transport': ['urban mobility', 'public transportation', 'transit optimization', 'mobility as a service', 'smart parking'],
            'Waste Management & Circular Economy': ['waste management', 'smart waste', 'recycling optimization', 'circular economy', 'resource management'],
            
            # 教育科技 - 更细化的分类
            'Adaptive Learning Systems': ['adaptive learning', 'personalized learning', 'intelligent tutoring', 'learning path optimization'],
            'Educational Assessment & Analytics': ['educational assessment', 'learning analytics', 'student performance', 'academic prediction', 'skill assessment'],
            'Educational Content & Curriculum': ['educational content', 'curriculum design', 'course generation', 'learning materials', 'educational resources'],
            'Language Learning & Translation': ['language learning', 'language education', 'translation', 'second language acquisition', 'pronunciation'],
            'STEM Education & Simulation': ['stem education', 'science education', 'math education', 'educational simulation', 'virtual labs'],
            'Special Needs & Accessibility': ['special education', 'accessibility', 'assistive technology', 'learning disabilities', 'inclusive education'],
            
            # 内容创作与媒体
            'Creative Content Generation': ['content generation', 'creative writing', 'art generation', 'design automation'],
            'Video & Image Production': ['video generation', 'image synthesis', 'visual effects', 'animation'],
            'Music & Audio Creation': ['music generation', 'audio synthesis', 'sound design'],
            
            # 工业制造
            'Industrial Automation': ['industrial automation', 'manufacturing', 'production line', 'quality control'],
            'Predictive Maintenance': ['predictive maintenance', 'equipment monitoring', 'failure prediction'],
            'Supply Chain Optimization': ['supply chain', 'inventory', 'logistics optimization'],
            
            # 网络安全
            'Cybersecurity & Threat Detection': ['cybersecurity', 'threat detection', 'intrusion detection', 'malware'],
            'Privacy Protection': ['privacy', 'data protection', 'anonymization', 'differential privacy'],
            'Network Security': ['network security', 'firewall', 'security protocols'],
            
            # 社交媒体与推荐
            'Social Media Analytics': ['social media', 'social network', 'sentiment analysis', 'opinion mining'],
            'Recommendation Systems': ['recommendation', 'collaborative filtering', 'personalization', 'content discovery'],
            'Misinformation Detection': ['misinformation', 'fake news', 'fact checking', 'disinformation'],
            
            # 科学研究
            'Scientific Discovery & Research': ['scientific discovery', 'research automation', 'hypothesis generation'],
            'Materials Science': ['materials science', 'material discovery', 'chemical properties'],
            'Climate & Earth Sciences': ['climate modeling', 'earth science', 'geological'],
            
            # 农业科技
            'Precision Agriculture': ['precision agriculture', 'crop monitoring', 'agricultural optimization'],
            'Food Safety & Quality': ['food safety', 'food quality', 'agricultural production'],
            
            # 零售与电商
            'E-commerce & Retail Analytics': ['e-commerce', 'retail', 'consumer behavior', 'market analysis'],
            'Inventory Management': ['inventory optimization', 'demand forecasting', 'retail planning'],
            
            # 人机交互
            'Human-Computer Interaction': ['human-computer interaction', 'user interface', 'user experience', 'accessibility'],
            'Virtual & Augmented Reality': ['virtual reality', 'augmented reality', 'immersive', 'metaverse'],
            
            # 游戏与娱乐
            'Game AI & Interactive Entertainment': ['game ai', 'gaming', 'interactive entertainment', 'procedural generation'],
            'Sports Analytics': ['sports analytics', 'performance analysis', 'athletic performance']
        }
        
        self.task_types = {
            # 基础AI任务
            'Classification & Recognition': ['classify', 'classification', 'recognition', 'detection', 'categorization', 'identification'],
            'Regression & Prediction': ['predict', 'prediction', 'forecast', 'estimate', 'regression', 'time series'],
            'Clustering & Segmentation': ['cluster', 'clustering', 'segmentation', 'grouping', 'unsupervised'],
            
            # 生成与创造性任务
            'Content Generation': ['generate', 'generation', 'create', 'synthesis', 'creative', 'produce'],
            'Data Augmentation': ['augmentation', 'synthetic data', 'data generation', 'sample generation'],
            'Style Transfer': ['style transfer', 'domain adaptation', 'translation', 'transformation'],
            
            # 优化与决策
            'Optimization & Search': ['optimize', 'optimization', 'search', 'planning', 'scheduling'],
            'Decision Making': ['decision', 'policy', 'strategy', 'control', 'action selection'],
            'Resource Allocation': ['allocation', 'assignment', 'matching', 'distribution'],
            
            # 理解与分析
            'Understanding & Interpretation': ['understand', 'understanding', 'interpret', 'explanation', 'reasoning'],
            'Knowledge Extraction': ['extraction', 'mining', 'discovery', 'retrieval', 'information extraction'],
            'Anomaly Detection': ['anomaly', 'outlier', 'abnormal', 'fraud', 'fault detection'],
            
            # 交互与对话
            'Conversational AI': ['conversation', 'dialogue', 'chatbot', 'question answering', 'interaction'],
            'Recommendation': ['recommend', 'recommendation', 'suggest', 'personalization', 'collaborative filtering'],
            
            # 多模态任务
            'Multimodal Learning': ['multimodal', 'cross-modal', 'vision-language', 'audio-visual'],
            'Transfer Learning': ['transfer', 'domain adaptation', 'few-shot', 'zero-shot', 'meta-learning'],
            
            # 安全与隐私
            'Privacy-Preserving': ['privacy', 'federated', 'differential privacy', 'secure'],
            'Robustness & Safety': ['robust', 'adversarial', 'safety', 'reliability', 'fairness']
        }
        
        # 技术发展趋势分类 - 更详细的技术生命周期分析
        self.technical_trends = {
            # 基础架构演进
            'Transformer Architecture Evolution': ['transformer', 'attention mechanism', 'self-attention', 'cross-attention', 'efficient transformers'],
            'Advanced CNN Architectures': ['convolutional networks', 'cnn', 'resnet', 'densenet', 'efficientnet', 'vision transformer'],
            'Graph Neural Networks': ['graph neural networks', 'gnn', 'graph convolution', 'graph attention', 'heterogeneous graphs'],
            'Generative Model Architectures': ['diffusion models', 'variational autoencoders', 'generative adversarial networks', 'flow models'],
            'Recurrent & Memory Networks': ['lstm', 'gru', 'memory networks', 'neural turing machines', 'differentiable computing'],
            
            # 学习范式创新
            'Foundation Model Paradigms': ['foundation models', 'large language models', 'vision-language models', 'multimodal foundation'],
            'Self-Supervised & Contrastive Learning': ['self-supervised learning', 'contrastive learning', 'masked modeling', 'pretext tasks'],
            'Few-Shot & Meta-Learning': ['few-shot learning', 'meta-learning', 'in-context learning', 'learning to learn', 'maml'],
            'Federated & Distributed Learning': ['federated learning', 'distributed training', 'privacy-preserving learning', 'decentralized ai'],
            'Continual & Lifelong Learning': ['continual learning', 'lifelong learning', 'catastrophic forgetting', 'incremental learning'],
            'Transfer & Domain Adaptation': ['transfer learning', 'domain adaptation', 'cross-domain learning', 'unsupervised domain adaptation'],
            
            # 优化与效率技术
            'Neural Architecture Search': ['neural architecture search', 'automl', 'differentiable architecture search', 'efficient nas'],
            'Model Compression & Efficiency': ['model compression', 'knowledge distillation', 'pruning', 'quantization', 'mobile ai'],
            'Training Optimization': ['optimization algorithms', 'learning rate scheduling', 'gradient methods', 'adaptive optimization'],
            'Hardware-Software Co-design': ['hardware acceleration', 'ai chips', 'edge computing', 'neuromorphic computing'],
            
            # 新兴技术前沿
            'Large Language Models': ['large language models', 'llm', 'chatgpt', 'instruction following', 'language model scaling'],
            'Multimodal Intelligence': ['multimodal learning', 'vision-language', 'audio-visual', 'cross-modal understanding'],
            'Retrieval-Augmented Generation': ['retrieval augmented generation', 'rag', 'knowledge retrieval', 'external memory'],
            'Advanced Prompting Techniques': ['prompt engineering', 'chain-of-thought', 'in-context learning', 'prompt optimization'],
            'AI Agents & Tool Use': ['ai agents', 'tool use', 'reasoning agents', 'multi-agent systems', 'autonomous agents'],
            'Embodied AI & Robotics': ['embodied ai', 'robotic learning', 'sim-to-real', 'robot manipulation', 'navigation'],
            
            # 特殊应用技术
            'Explainable AI & Interpretability': ['explainable ai', 'interpretability', 'attention visualization', 'model explanation'],
            'Adversarial & Robust Learning': ['adversarial training', 'robust optimization', 'certified robustness', 'defense mechanisms'],
            'Causal AI & Reasoning': ['causal inference', 'causal discovery', 'counterfactual reasoning', 'causal representation'],
            'Quantum Machine Learning': ['quantum machine learning', 'quantum algorithms', 'quantum neural networks', 'quantum computing'],
            'Neuro-Symbolic AI': ['neuro-symbolic', 'symbolic reasoning', 'knowledge graphs', 'logical reasoning'],
            'AI Safety & Alignment': ['ai safety', 'alignment', 'robustness', 'ai ethics', 'safe ai']
        }
    
    def analyze_paper_task_scenario(self, df: pd.DataFrame) -> pd.DataFrame:
        """分析论文任务场景"""
        df_copy = df.copy()
        
        # 初始化列
        df_copy['application_scenario'] = 'General Research'
        df_copy['scenario_confidence'] = 0.0
        df_copy['task_type'] = 'Other Tasks'
        df_copy['task_confidence'] = 0.0
        df_copy['technical_trend'] = 'Traditional Methods'
        df_copy['trend_confidence'] = 0.0
        
        for idx, row in df_copy.iterrows():
            text = f"{row.get('title', '')} {row.get('abstract', '')}".lower()
            
            # 分析应用场景
            best_scenario = 'General Research'
            best_scenario_score = 0
            
            for scenario, keywords in self.application_scenarios.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > best_scenario_score:
                    best_scenario_score = score
                    best_scenario = scenario
            
            df_copy.at[idx, 'application_scenario'] = best_scenario
            df_copy.at[idx, 'scenario_confidence'] = min(best_scenario_score / 10, 1.0)
            
            # 分析任务类型
            best_task = 'Other Tasks'
            best_task_score = 0
            
            for task_type, keywords in self.task_types.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > best_task_score:
                    best_task_score = score
                    best_task = task_type
            
            df_copy.at[idx, 'task_type'] = best_task
            df_copy.at[idx, 'task_confidence'] = min(best_task_score / 5, 1.0)
            
            # 分析技术趋势
            best_trend = 'Traditional Methods'
            best_trend_score = 0
            
            for trend, keywords in self.technical_trends.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > best_trend_score:
                    best_trend_score = score
                    best_trend = trend
            
            df_copy.at[idx, 'technical_trend'] = best_trend
            df_copy.at[idx, 'trend_confidence'] = min(best_trend_score / 5, 1.0)
        
        return df_copy


def main():
    """主函数"""
    analyzer = UnifiedAnalyzer()
    results = analyzer.perform_comprehensive_analysis()
    
    print("✅ 数据分析完成！")
    print(f"总论文数: {results['basic_statistics']['total_papers']:,}")
    print(f"涵盖年份: {results['basic_statistics']['year_range']}")
    print(f"分析结果已保存到: outputs/analysis/")
    
    return results


if __name__ == "__main__":
    main()