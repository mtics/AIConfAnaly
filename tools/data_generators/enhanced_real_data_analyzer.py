#!/usr/bin/env python3
"""
增强的真实数据分析器 - 基于实际论文数据进行深度分析
结合outputs/data和Milvus数据进行全面关键词提取和洞察分析
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# 简化的关键词提取，不依赖外部库
try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Warning: pandas/numpy not available, using basic alternatives")
    pd = None
    np = None


class EnhancedRealDataAnalyzer:
    """基于真实数据的增强分析器"""
    
    def __init__(self, data_dir: str = "outputs/data"):
        """初始化分析器"""
        self.data_dir = Path(data_dir)
        self.raw_data_dir = self.data_dir / "raw"
        self.papers_data = []
        self.total_papers = 0
        
        # 初始化停用词（内置列表）
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
            'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will',
            'with', 'the', 'this', 'but', 'they', 'have', 'had', 'what', 'said', 'each',
            'which', 'she', 'do', 'how', 'their', 'if', 'up', 'out', 'many', 'then', 'them',
            'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'time',
            'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call',
            'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get', 'come', 'made',
            'may', 'part',
            # 研究论文常见停用词
            'paper', 'approach', 'method', 'algorithm', 'model', 'based', 'using',
            'propose', 'proposed', 'show', 'shown', 'result', 'results', 'new',
            'novel', 'present', 'study', 'work', 'research', 'analysis', 'evaluate',
            'evaluation', 'experimental', 'experiments', 'performance', 'achieve',
            'achieved', 'effective', 'efficient', 'technique', 'techniques', 'we',
            'our', 'can', 'also', 'used', 'use', 'one', 'two', 'three', 'first',
            'second', 'third', 'different', 'various', 'several', 'multiple'
        }
        
        # 真实关键词分类
        self.real_keywords = defaultdict(set)
        self.keyword_frequency = Counter()
        self.conference_keywords = defaultdict(lambda: defaultdict(int))
        self.year_keywords = defaultdict(lambda: defaultdict(int))
        
    def load_real_data(self) -> bool:
        """加载所有真实论文数据"""
        print("🔍 加载真实论文数据...")
        
        if not self.raw_data_dir.exists():
            print(f"❌ 数据目录不存在: {self.raw_data_dir}")
            return False
        
        json_files = list(self.raw_data_dir.glob("*.json"))
        if not json_files:
            print(f"❌ 未找到JSON数据文件")
            return False
        
        total_loaded = 0
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.papers_data.extend(data)
                        total_loaded += len(data)
                        print(f"✅ 加载 {json_file.name}: {len(data)} 篇论文")
                    else:
                        print(f"⚠️  跳过非列表格式文件: {json_file.name}")
            except Exception as e:
                print(f"❌ 加载文件失败 {json_file.name}: {e}")
        
        self.total_papers = len(self.papers_data)
        print(f"📊 总计加载 {self.total_papers} 篇论文数据")
        return self.total_papers > 0
    
    def extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        if not text or not isinstance(text, str):
            return []
        
        # 清理文本
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 简单分词（按空格分割）
        words = text.split()
        
        # 过滤停用词和短词
        keywords = []
        for word in words:
            if (len(word) > 2 and 
                word not in self.stop_words and 
                word.isalpha() and
                not word.isdigit()):
                keywords.append(word)
        
        return keywords
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """提取技术术语"""
        if not text:
            return []
        
        # 常见技术术语模式
        tech_patterns = [
            # AI/ML技术
            r'\b(?:deep|neural|machine|reinforcement|supervised|unsupervised|semi-supervised)\s+(?:learning|network|networks)\b',
            r'\b(?:convolutional|recurrent|transformer|attention|bert|gpt|lstm|gru|cnn|rnn)\b',
            r'\b(?:gan|vae|autoencoder|encoder|decoder)\b',
            
            # 应用领域
            r'\b(?:computer|machine)\s+vision\b',
            r'\b(?:natural|speech)\s+(?:language|processing|recognition)\b',
            r'\b(?:object|face|image|text|sentiment|emotion)\s+(?:detection|recognition|analysis|classification)\b',
            
            # 技术方法
            r'\b(?:graph|knowledge|recommendation|prediction|optimization|clustering)\b',
            r'\b(?:classification|regression|segmentation|generation|synthesis)\b',
            r'\b(?:adversarial|federated|transfer|multi-task|few-shot|zero-shot)\b',
            
            # 应用场景
            r'\b(?:autonomous|self-driving|medical|healthcare|financial|robotic)\b',
            r'\b(?:social|recommendation|search|dialogue|question\s+answering)\b'
        ]
        
        terms = []
        text_lower = text.lower()
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower)
            terms.extend(matches)
        
        return list(set(terms))
    
    def analyze_real_research_fields(self) -> Dict[str, Any]:
        """基于真实数据分析研究领域"""
        print("🔬 分析真实研究领域...")
        
        field_keywords = defaultdict(Counter)
        field_papers = defaultdict(list)
        
        # 定义真实研究领域关键词（基于实际论文标题和摘要）
        field_definitions = {
            'Computer Vision': {
                'keywords': ['vision', 'image', 'visual', 'object', 'detection', 'recognition', 
                           'segmentation', 'cnn', 'convolutional', 'face', 'video', 'camera'],
                'patterns': [r'\bcomputer\s+vision\b', r'\bobject\s+detection\b', r'\bimage\s+classification\b']
            },
            'Natural Language Processing': {
                'keywords': ['language', 'text', 'nlp', 'bert', 'transformer', 'word', 'sentence',
                           'translation', 'dialogue', 'question', 'answering', 'sentiment'],
                'patterns': [r'\bnatural\s+language\b', r'\btext\s+processing\b', r'\bmachine\s+translation\b']
            },
            'Deep Learning': {
                'keywords': ['deep', 'neural', 'network', 'learning', 'cnn', 'rnn', 'lstm',
                           'attention', 'transformer', 'embedding', 'layer'],
                'patterns': [r'\bdeep\s+learning\b', r'\bneural\s+network\b']
            },
            'Machine Learning': {
                'keywords': ['learning', 'classification', 'regression', 'clustering', 'supervised',
                           'unsupervised', 'training', 'model', 'algorithm'],
                'patterns': [r'\bmachine\s+learning\b', r'\bsupervised\s+learning\b']
            },
            'Reinforcement Learning': {
                'keywords': ['reinforcement', 'reward', 'policy', 'agent', 'environment', 'q-learning',
                           'actor', 'critic', 'markov', 'decision'],
                'patterns': [r'\breinforcement\s+learning\b', r'\bq-learning\b']
            },
            'Graph Neural Networks': {
                'keywords': ['graph', 'node', 'edge', 'gnn', 'gcn', 'network', 'social', 'knowledge'],
                'patterns': [r'\bgraph\s+neural\b', r'\bgraph\s+convolution\b']
            },
            'Generative AI': {
                'keywords': ['generative', 'generation', 'gan', 'vae', 'diffusion', 'synthesis',
                           'creative', 'generate', 'autoencoder'],
                'patterns': [r'\bgenerative\s+adversarial\b', r'\btext\s+generation\b']
            },
            'Multimodal Learning': {
                'keywords': ['multimodal', 'multi-modal', 'vision-language', 'cross-modal',
                           'audio-visual', 'text-image'],
                'patterns': [r'\bmultimodal\s+learning\b', r'\bcross-modal\b']
            }
        }
        
        for paper in self.papers_data:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            full_text = f"{title} {abstract}"
            
            # 为每个研究领域计算匹配分数
            for field, definition in field_definitions.items():
                score = 0
                matched_keywords = []
                
                # 关键词匹配
                for keyword in definition['keywords']:
                    if keyword in full_text:
                        score += full_text.count(keyword)
                        matched_keywords.append(keyword)
                
                # 模式匹配
                for pattern in definition['patterns']:
                    matches = len(re.findall(pattern, full_text))
                    if matches > 0:
                        score += matches * 2  # 模式匹配权重更高
                
                if score > 0:
                    field_papers[field].append({
                        'paper': paper,
                        'score': score,
                        'matched_keywords': matched_keywords
                    })
                    
                    # 更新关键词计数
                    for keyword in matched_keywords:
                        field_keywords[field][keyword] += 1
        
        # 整理结果
        field_analysis = {}
        for field, papers in field_papers.items():
            if papers:
                # 按分数排序
                papers.sort(key=lambda x: x['score'], reverse=True)
                
                field_analysis[field] = {
                    'paper_count': len(papers),
                    'percentage': len(papers) / self.total_papers * 100,
                    'top_keywords': dict(field_keywords[field].most_common(10)),
                    'representative_papers': [
                        {
                            'title': p['paper']['title'],
                            'year': p['paper']['year'],
                            'conference': p['paper']['conference'],
                            'score': p['score']
                        }
                        for p in papers[:5]
                    ],
                    'year_distribution': self._get_year_distribution([p['paper'] for p in papers]),
                    'conference_distribution': self._get_conference_distribution([p['paper'] for p in papers])
                }
        
        return field_analysis
    
    def analyze_real_application_scenarios(self) -> Dict[str, Any]:
        """基于真实数据分析应用场景"""
        print("🎯 分析真实应用场景...")
        
        scenario_keywords = defaultdict(Counter)
        scenario_papers = defaultdict(list)
        
        # 定义真实应用场景（基于实际论文内容）
        scenario_definitions = {
            'Medical & Healthcare': {
                'keywords': ['medical', 'health', 'healthcare', 'clinical', 'disease', 'patient',
                           'diagnosis', 'drug', 'therapy', 'surgery', 'radiology', 'pathology'],
                'patterns': [r'\bmedical\s+imaging\b', r'\bdrug\s+discovery\b', r'\bclinical\s+decision\b']
            },
            'Autonomous Vehicles': {
                'keywords': ['autonomous', 'self-driving', 'vehicle', 'driving', 'navigation',
                           'traffic', 'road', 'car', 'automotive', 'lidar'],
                'patterns': [r'\bautonomous\s+vehicle\b', r'\bself-driving\b']
            },
            'Financial Technology': {
                'keywords': ['financial', 'finance', 'trading', 'investment', 'risk', 'fraud',
                           'banking', 'payment', 'blockchain', 'cryptocurrency'],
                'patterns': [r'\bfinancial\s+analysis\b', r'\bfraud\s+detection\b']
            },
            'Social Media & Networks': {
                'keywords': ['social', 'network', 'community', 'influence', 'viral', 'recommendation',
                           'user', 'behavior', 'engagement', 'platform'],
                'patterns': [r'\bsocial\s+network\b', r'\buser\s+behavior\b']
            },
            'Robotics & Automation': {
                'keywords': ['robot', 'robotics', 'manipulation', 'control', 'motion', 'planning',
                           'grasping', 'navigation', 'automation', 'actuator'],
                'patterns': [r'\brobot\s+control\b', r'\bmotion\s+planning\b']
            },
            'Education & E-Learning': {
                'keywords': ['education', 'learning', 'student', 'teaching', 'tutoring', 'mooc',
                           'adaptive', 'personalized', 'assessment', 'curriculum'],
                'patterns': [r'\badaptive\s+learning\b', r'\be-learning\b']
            },
            'Entertainment & Gaming': {
                'keywords': ['game', 'gaming', 'entertainment', 'virtual', 'augmented', 'reality',
                           'character', 'narrative', 'interactive', 'player'],
                'patterns': [r'\bvirtual\s+reality\b', r'\bgame\s+ai\b']
            },
            'Smart Cities & IoT': {
                'keywords': ['smart', 'city', 'urban', 'iot', 'sensor', 'infrastructure',
                           'energy', 'environment', 'sustainable', 'monitoring'],
                'patterns': [r'\bsmart\s+city\b', r'\biot\s+device\b']
            },
            'Cybersecurity': {
                'keywords': ['security', 'cyber', 'attack', 'defense', 'intrusion', 'malware',
                           'privacy', 'encryption', 'vulnerability', 'threat'],
                'patterns': [r'\bcyber\s+security\b', r'\bintrusion\s+detection\b']
            },
            'Manufacturing & Industry': {
                'keywords': ['manufacturing', 'industrial', 'production', 'quality', 'supply',
                           'chain', 'factory', 'process', 'automation', 'maintenance'],
                'patterns': [r'\bindustrial\s+automation\b', r'\bsupply\s+chain\b']
            }
        }
        
        for paper in self.papers_data:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            full_text = f"{title} {abstract}"
            
            # 为每个应用场景计算匹配分数
            for scenario, definition in scenario_definitions.items():
                score = 0
                matched_keywords = []
                
                # 关键词匹配
                for keyword in definition['keywords']:
                    if keyword in full_text:
                        score += full_text.count(keyword)
                        matched_keywords.append(keyword)
                
                # 模式匹配
                for pattern in definition['patterns']:
                    matches = len(re.findall(pattern, full_text))
                    if matches > 0:
                        score += matches * 2
                
                if score > 0:
                    scenario_papers[scenario].append({
                        'paper': paper,
                        'score': score,
                        'matched_keywords': matched_keywords
                    })
                    
                    for keyword in matched_keywords:
                        scenario_keywords[scenario][keyword] += 1
        
        # 整理结果
        scenario_analysis = {}
        for scenario, papers in scenario_papers.items():
            if papers:
                papers.sort(key=lambda x: x['score'], reverse=True)
                
                scenario_analysis[scenario] = {
                    'paper_count': len(papers),
                    'percentage': len(papers) / self.total_papers * 100,
                    'top_keywords': dict(scenario_keywords[scenario].most_common(10)),
                    'representative_papers': [
                        {
                            'title': p['paper']['title'],
                            'year': p['paper']['year'],
                            'conference': p['paper']['conference'],
                            'score': p['score']
                        }
                        for p in papers[:5]
                    ],
                    'growth_trend': self._calculate_growth_trend([p['paper'] for p in papers]),
                    'conference_distribution': self._get_conference_distribution([p['paper'] for p in papers])
                }
        
        return scenario_analysis
    
    def extract_all_keywords(self) -> Dict[str, Any]:
        """提取所有关键词并分析"""
        print("🔎 提取所有关键词...")
        
        all_keywords = Counter()
        title_keywords = Counter()
        abstract_keywords = Counter()
        technical_terms = Counter()
        
        for paper in self.papers_data:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            
            # 提取标题关键词
            title_kw = self.extract_keywords_from_text(title)
            title_keywords.update(title_kw)
            all_keywords.update(title_kw)
            
            # 提取摘要关键词
            abstract_kw = self.extract_keywords_from_text(abstract)
            abstract_keywords.update(abstract_kw)
            all_keywords.update(abstract_kw)
            
            # 提取技术术语
            tech_terms = self.extract_technical_terms(f"{title} {abstract}")
            technical_terms.update(tech_terms)
        
        return {
            'total_unique_keywords': len(all_keywords),
            'most_common_keywords': dict(all_keywords.most_common(100)),
            'title_keywords': dict(title_keywords.most_common(50)),
            'abstract_keywords': dict(abstract_keywords.most_common(50)),
            'technical_terms': dict(technical_terms.most_common(50)),
            'keyword_statistics': {
                'average_keywords_per_paper': sum(all_keywords.values()) / self.total_papers,
                'median_keyword_frequency': sorted(list(all_keywords.values()))[len(all_keywords)//2] if all_keywords else 0,
                'keywords_appearing_once': sum(1 for count in all_keywords.values() if count == 1)
            }
        }
    
    def analyze_temporal_trends(self) -> Dict[str, Any]:
        """分析时间趋势"""
        print("📈 分析时间趋势...")
        
        year_stats = defaultdict(lambda: {
            'papers': 0, 'conferences': set(), 'keywords': Counter()
        })
        
        for paper in self.papers_data:
            year = paper.get('year')
            if year:
                year_stats[year]['papers'] += 1
                year_stats[year]['conferences'].add(paper.get('conference', ''))
                
                # 提取该论文的关键词
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                keywords = self.extract_keywords_from_text(text)
                year_stats[year]['keywords'].update(keywords)
        
        # 整理年度趋势
        temporal_analysis = {}
        sorted_years = sorted(year_stats.keys())
        
        for year in sorted_years:
            stats = year_stats[year]
            temporal_analysis[year] = {
                'paper_count': stats['papers'],
                'conference_count': len(stats['conferences']),
                'conferences': list(stats['conferences']),
                'top_keywords': dict(stats['keywords'].most_common(20)),
                'growth_rate': self._calculate_year_growth_rate(year, year_stats)
            }
        
        return {
            'yearly_analysis': temporal_analysis,
            'overall_trends': {
                'total_years': len(sorted_years),
                'year_range': f"{sorted_years[0]}-{sorted_years[-1]}",
                'peak_year': max(year_stats.keys(), key=lambda y: year_stats[y]['papers']),
                'average_papers_per_year': sum(stats['papers'] for stats in year_stats.values()) / len(year_stats)
            }
        }
    
    def generate_deep_insights(self) -> Dict[str, Any]:
        """生成深度洞察分析"""
        print("💡 生成深度洞察...")
        
        # 获取所有分析结果
        field_analysis = self.analyze_real_research_fields()
        scenario_analysis = self.analyze_real_application_scenarios()
        keyword_analysis = self.extract_all_keywords()
        temporal_analysis = self.analyze_temporal_trends()
        
        # 深度洞察分析
        insights = {
            'research_maturity_analysis': self._analyze_research_maturity(field_analysis, temporal_analysis),
            'application_potential_analysis': self._analyze_application_potential(scenario_analysis),
            'technology_convergence_analysis': self._analyze_technology_convergence(field_analysis, keyword_analysis),
            'future_trend_predictions': self._predict_future_trends(temporal_analysis, keyword_analysis),
            'research_gap_identification': self._identify_research_gaps(field_analysis, scenario_analysis),
            'interdisciplinary_opportunities': self._identify_interdisciplinary_opportunities(field_analysis, scenario_analysis)
        }
        
        return insights
    
    def _analyze_research_maturity(self, field_analysis: Dict, temporal_analysis: Dict) -> Dict[str, Any]:
        """分析研究成熟度"""
        maturity_scores = {}
        
        for field, data in field_analysis.items():
            # 基于论文数量、时间跨度、增长趋势等评估成熟度
            paper_count = data['paper_count']
            percentage = data['percentage']
            
            # 计算成熟度分数
            maturity_score = min(100, (paper_count / 100) * 30 + percentage * 2)
            
            maturity_level = 'Emerging' if maturity_score < 30 else \
                           'Growing' if maturity_score < 60 else \
                           'Mature' if maturity_score < 80 else 'Established'
            
            maturity_scores[field] = {
                'score': round(maturity_score, 2),
                'level': maturity_level,
                'paper_count': paper_count,
                'market_share': round(percentage, 2)
            }
        
        return maturity_scores
    
    def _analyze_application_potential(self, scenario_analysis: Dict) -> Dict[str, Any]:
        """分析应用潜力"""
        potential_analysis = {}
        
        for scenario, data in scenario_analysis.items():
            growth_trend = data.get('growth_trend', {})
            recent_growth = growth_trend.get('recent_years_growth', 0)
            
            # 计算应用潜力分数
            potential_score = min(100, data['percentage'] * 2 + recent_growth * 10)
            
            potential_level = 'Low' if potential_score < 25 else \
                            'Medium' if potential_score < 50 else \
                            'High' if potential_score < 75 else 'Very High'
            
            potential_analysis[scenario] = {
                'potential_score': round(potential_score, 2),
                'potential_level': potential_level,
                'current_adoption': data['paper_count'],
                'growth_momentum': recent_growth
            }
        
        return potential_analysis
    
    def _analyze_technology_convergence(self, field_analysis: Dict, keyword_analysis: Dict) -> Dict[str, Any]:
        """分析技术融合趋势"""
        common_keywords = keyword_analysis['most_common_keywords']
        
        # 识别跨领域共同关键词
        convergence_keywords = {
            kw: count for kw, count in common_keywords.items() 
            if count > self.total_papers * 0.05  # 出现在5%以上论文中
        }
        
        return {
            'convergence_indicators': convergence_keywords,
            'multi_field_technologies': list(convergence_keywords.keys())[:10],
            'convergence_strength': len(convergence_keywords)
        }
    
    def _predict_future_trends(self, temporal_analysis: Dict, keyword_analysis: Dict) -> Dict[str, Any]:
        """预测未来趋势"""
        yearly_data = temporal_analysis['yearly_analysis']
        recent_years = sorted(yearly_data.keys())[-3:]  # 最近3年
        
        emerging_keywords = []
        for year in recent_years:
            year_keywords = yearly_data.get(year, {}).get('top_keywords', {})
            # 识别新兴关键词（高频但相对较新）
            for kw, count in list(year_keywords.items())[:10]:
                if count > 10:  # 足够频繁
                    emerging_keywords.append(kw)
        
        # 统计新兴关键词频率
        emerging_counter = Counter(emerging_keywords)
        
        return {
            'emerging_technologies': dict(emerging_counter.most_common(15)),
            'predicted_hot_areas': list(emerging_counter.keys())[:8],
            'trend_indicators': {
                'increasing_complexity': 'multimodal' in emerging_counter,
                'practical_applications': any(kw in emerging_counter for kw in ['practical', 'real-world', 'deployment']),
                'ai_democratization': 'accessible' in emerging_counter or 'easy' in emerging_counter
            }
        }
    
    def _identify_research_gaps(self, field_analysis: Dict, scenario_analysis: Dict) -> Dict[str, Any]:
        """识别研究空白"""
        # 识别研究不足的领域
        underrepresented_fields = {
            field: data for field, data in field_analysis.items()
            if data['percentage'] < 5  # 小于5%的研究领域
        }
        
        underrepresented_scenarios = {
            scenario: data for scenario, data in scenario_analysis.items()
            if data['percentage'] < 3  # 小于3%的应用场景
        }
        
        return {
            'underrepresented_research_fields': list(underrepresented_fields.keys()),
            'underrepresented_applications': list(underrepresented_scenarios.keys()),
            'potential_research_opportunities': [
                'Cross-modal learning applications',
                'Real-world deployment challenges',
                'Ethical AI in practice',
                'AI for social good',
                'Sustainable AI systems'
            ]
        }
    
    def _identify_interdisciplinary_opportunities(self, field_analysis: Dict, scenario_analysis: Dict) -> Dict[str, Any]:
        """识别跨学科机会"""
        opportunities = []
        
        # 识别技术与应用的交叉机会
        high_tech_fields = [f for f, d in field_analysis.items() if d['percentage'] > 10]
        high_potential_scenarios = [s for s, d in scenario_analysis.items() if d['percentage'] > 5]
        
        for tech_field in high_tech_fields:
            for scenario in high_potential_scenarios:
                opportunities.append(f"{tech_field} × {scenario}")
        
        return {
            'cross_field_opportunities': opportunities[:10],
            'high_impact_combinations': [
                'Computer Vision × Medical & Healthcare',
                'Natural Language Processing × Education & E-Learning',
                'Reinforcement Learning × Autonomous Vehicles',
                'Graph Neural Networks × Social Media & Networks'
            ]
        }
    
    def _get_year_distribution(self, papers: List[Dict]) -> Dict[int, int]:
        """获取年份分布"""
        year_count = Counter(paper.get('year') for paper in papers if paper.get('year'))
        return dict(year_count)
    
    def _get_conference_distribution(self, papers: List[Dict]) -> Dict[str, int]:
        """获取会议分布"""
        conf_count = Counter(paper.get('conference') for paper in papers if paper.get('conference'))
        return dict(conf_count)
    
    def _calculate_growth_trend(self, papers: List[Dict]) -> Dict[str, Any]:
        """计算增长趋势"""
        year_counts = self._get_year_distribution(papers)
        if len(year_counts) < 2:
            return {'recent_years_growth': 0, 'overall_trend': 'insufficient_data'}
        
        sorted_years = sorted(year_counts.keys())
        recent_years = sorted_years[-3:] if len(sorted_years) >= 3 else sorted_years
        
        if len(recent_years) >= 2:
            recent_growth = (year_counts[recent_years[-1]] - year_counts[recent_years[0]]) / year_counts[recent_years[0]] * 100
        else:
            recent_growth = 0
        
        return {
            'recent_years_growth': round(recent_growth, 2),
            'overall_trend': 'increasing' if recent_growth > 10 else 'stable' if recent_growth > -10 else 'decreasing'
        }
    
    def _calculate_year_growth_rate(self, year: int, year_stats: Dict) -> float:
        """计算年增长率"""
        if year - 1 in year_stats:
            prev_count = year_stats[year - 1]['papers']
            curr_count = year_stats[year]['papers']
            if prev_count > 0:
                return round((curr_count - prev_count) / prev_count * 100, 2)
        return 0.0
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        print("📋 生成综合分析报告...")
        
        if not self.load_real_data():
            return {'error': '无法加载数据'}
        
        # 执行所有分析
        field_analysis = self.analyze_real_research_fields()
        scenario_analysis = self.analyze_real_application_scenarios()
        keyword_analysis = self.extract_all_keywords()
        temporal_analysis = self.analyze_temporal_trends()
        deep_insights = self.generate_deep_insights()
        
        # 生成综合报告
        comprehensive_report = {
            'metadata': {
                'total_papers': self.total_papers,
                'analysis_date': '2025-07-27 ' + __import__('datetime').datetime.now().strftime('%H:%M:%S'),
                'data_sources': 'outputs/data/raw/*.json',
                'conferences_analyzed': list(set(p.get('conference') for p in self.papers_data if p.get('conference'))),
                'year_range': f"{min(p.get('year', 9999) for p in self.papers_data if p.get('year'))}-{max(p.get('year', 0) for p in self.papers_data if p.get('year'))}"
            },
            'research_fields_analysis': field_analysis,
            'application_scenarios_analysis': scenario_analysis,
            'keyword_analysis': keyword_analysis,
            'temporal_trends_analysis': temporal_analysis,
            'deep_insights': deep_insights,
            'summary_statistics': {
                'top_research_fields': sorted(field_analysis.items(), key=lambda x: x[1]['paper_count'], reverse=True)[:5],
                'top_application_scenarios': sorted(scenario_analysis.items(), key=lambda x: x[1]['paper_count'], reverse=True)[:5],
                'most_frequent_keywords': list(keyword_analysis['most_common_keywords'].keys())[:20],
                'research_diversity_index': len(field_analysis),
                'application_diversity_index': len(scenario_analysis)
            }
        }
        
        return comprehensive_report


def main():
    """主函数"""
    print("🚀 启动增强真实数据分析器")
    print("=" * 60)
    
    # 创建分析器
    analyzer = EnhancedRealDataAnalyzer()
    
    # 生成综合报告
    report = analyzer.generate_comprehensive_report()
    
    if 'error' in report:
        print(f"❌ 分析失败: {report['error']}")
        return
    
    # 保存报告
    output_dir = Path("outputs/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = output_dir / "enhanced_real_data_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 增强分析报告已保存: {report_file}")
    
    # 打印核心统计
    metadata = report['metadata']
    print(f"\n📊 分析概览:")
    print(f"   总论文数: {metadata['total_papers']:,}")
    print(f"   时间跨度: {metadata['year_range']}")
    print(f"   涵盖会议: {len(metadata['conferences_analyzed'])}个")
    
    # 打印关键发现
    summary = report['summary_statistics']
    print(f"\n🔍 关键发现:")
    print(f"   研究领域数: {summary['research_diversity_index']}")
    print(f"   应用场景数: {summary['application_diversity_index']}")
    print(f"   热门关键词: {', '.join(summary['most_frequent_keywords'][:10])}")
    
    print(f"\n🎯 顶级研究领域:")
    for field, data in summary['top_research_fields']:
        print(f"   {field}: {data['paper_count']} 篇 ({data['percentage']:.1f}%)")
    
    print(f"\n💼 顶级应用场景:")
    for scenario, data in summary['top_application_scenarios']:
        print(f"   {scenario}: {data['paper_count']} 篇 ({data['percentage']:.1f}%)")
    
    print("\n" + "=" * 60)
    print("🎉 增强真实数据分析完成！")


if __name__ == "__main__":
    main()