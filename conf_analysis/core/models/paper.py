"""
Paper类 - 集成论文信息和分析结果的核心数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import hashlib
import json
import numpy as np
from enum import Enum


class TaskType(Enum):
    """任务类型枚举"""
    PREDICTION = "Prediction Tasks"
    CLASSIFICATION = "Classification Tasks"
    GENERATION = "Generation Tasks"
    OPTIMIZATION = "Optimization Tasks"
    RECOMMENDATION = "Recommendation Tasks"
    CONTROL = "Control Tasks"
    UNDERSTANDING = "Understanding Tasks"
    SEARCH = "Search Tasks"
    OTHER = "Other Tasks"


class ApplicationScenario(Enum):
    """应用场景枚举"""
    MEDICAL_DIAGNOSIS = "Medical Diagnosis"
    AUTONOMOUS_DRIVING = "Autonomous Driving"
    FINANCIAL_TECHNOLOGY = "Financial Technology"
    SMART_CITY = "Smart City"
    EDUCATIONAL_TECHNOLOGY = "Educational Technology"
    CONTENT_CREATION = "Content Creation"
    SCIENTIFIC_RESEARCH = "Scientific Research"
    MANUFACTURING = "Manufacturing"
    RETAIL_ECOMMERCE = "Retail & E-commerce"
    SOCIAL_MEDIA = "Social Media"
    GAMING = "Gaming"
    CYBERSECURITY = "Cybersecurity"
    GENERAL_RESEARCH = "General Research"


@dataclass
class TaskScenarioAnalysis:
    """任务场景分析结果"""
    application_scenario: str
    scenario_confidence: float
    task_type: str
    task_confidence: float
    task_objectives: List[str] = field(default_factory=list)
    scenario_keywords: List[str] = field(default_factory=list)
    task_keywords: List[str] = field(default_factory=list)
    real_world_impact: str = ""
    target_users: List[str] = field(default_factory=list)
    social_value: str = ""


@dataclass
class PaperMetrics:
    """论文指标数据"""
    citation_count: int = 0
    influence_score: float = 0.0
    novelty_score: float = 0.0
    practical_value_score: float = 0.0
    technical_quality_score: float = 0.0
    
    # 文本统计
    title_length: int = 0
    abstract_length: int = 0
    abstract_word_count: int = 0
    keyword_count: int = 0


@dataclass
class ConferenceInfo:
    """会议信息"""
    name: str
    year: int
    venue_type: str = "conference"  # conference, journal, workshop
    ranking: str = ""  # A*, A, B, C
    field_specialization: List[str] = field(default_factory=list)
    acceptance_rate: Optional[float] = None


@dataclass
class AuthorInfo:
    """作者信息"""
    names: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    collaboration_type: str = "single"  # single, domestic, international


class Paper:
    """
    论文类 - 集成所有论文信息和分析结果的核心数据模型
    """
    
    def __init__(self, 
                 title: str,
                 abstract: str,
                 conference: str,
                 year: int,
                 url: Optional[str] = None,
                 pdf_url: Optional[str] = None,
                 paper_id: Optional[str] = None):
        """
        初始化Paper对象
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            conference: 会议名称
            year: 发表年份
            url: 论文链接
            pdf_url: PDF链接
            paper_id: 论文ID（如果未提供将自动生成）
        """
        
        # 基础信息
        self.paper_id = paper_id or self._generate_paper_id(title, conference, year)
        self.title = title
        self.abstract = abstract
        self.conference = conference
        self.year = year
        self.url = url
        self.pdf_url = pdf_url
        
        # 时间戳
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 分析结果（初始化为空，后续填充）
        self.task_scenario_analysis: Optional[TaskScenarioAnalysis] = None
        self.conference_info: Optional[ConferenceInfo] = None
        self.author_info: Optional[AuthorInfo] = None
        self.metrics: PaperMetrics = PaperMetrics()
        
        # 文本处理结果
        self.processed_text: Dict[str, Any] = {}
        self.keywords: List[str] = []
        self.bigrams: List[str] = []
        
        # 向量表示（用于Milvus存储）
        self.text_embedding: Optional[np.ndarray] = None
        self.semantic_embedding: Optional[np.ndarray] = None
        
        # 深层次分析结果
        self.insight_data: Dict[str, Any] = {}
        
        # 标签和分类
        self.tags: List[str] = []
        self.categories: List[str] = []
        
        # 质量评估
        self.quality_flags: Dict[str, bool] = {
            'has_abstract': bool(abstract and len(abstract.strip()) > 10),
            'has_complete_info': bool(title and conference and year),
            'text_quality_ok': True,
            'analysis_complete': False
        }
    
    def _generate_paper_id(self, title: str, conference: str, year: int) -> str:
        """生成唯一的论文ID"""
        content = f"{title}_{conference}_{year}".encode('utf-8')
        hash_object = hashlib.md5(content)
        return f"paper_{hash_object.hexdigest()[:12]}"
    
    def add_task_scenario_analysis(self, analysis: TaskScenarioAnalysis) -> None:
        """添加任务场景分析结果"""
        self.task_scenario_analysis = analysis
        self.updated_at = datetime.now()
        self._update_quality_flags()
    
    def add_conference_info(self, conf_info: ConferenceInfo) -> None:
        """添加会议信息"""
        self.conference_info = conf_info
        self.updated_at = datetime.now()
    
    def add_author_info(self, author_info: AuthorInfo) -> None:
        """添加作者信息"""
        self.author_info = author_info
        self.updated_at = datetime.now()
    
    def update_metrics(self, metrics: PaperMetrics) -> None:
        """更新论文指标"""
        self.metrics = metrics
        self.updated_at = datetime.now()
    
    def add_processed_text(self, processed_data: Dict[str, Any]) -> None:
        """添加文本处理结果"""
        self.processed_text = processed_data
        
        # 提取关键词和双词组
        self.keywords = processed_data.get('keywords', [])
        self.bigrams = processed_data.get('bigrams', [])
        
        # 更新文本指标
        self.metrics.title_length = len(self.title) if self.title else 0
        self.metrics.abstract_length = len(self.abstract) if self.abstract else 0
        self.metrics.abstract_word_count = len(self.abstract.split()) if self.abstract else 0
        self.metrics.keyword_count = len(self.keywords)
        
        self.updated_at = datetime.now()
    
    def set_text_vector(self, embedding: np.ndarray) -> None:
        """设置文本向量"""
        self.text_embedding = embedding
        self.updated_at = datetime.now()
    
    def set_semantic_vector(self, embedding: np.ndarray) -> None:
        """设置语义向量"""
        self.semantic_embedding = embedding
        self.updated_at = datetime.now()
    
    def add_text_embedding(self, embedding: np.ndarray, embedding_type: str = 'text') -> None:
        """添加文本向量表示"""
        if embedding_type == 'text':
            self.text_embedding = embedding
        elif embedding_type == 'semantic':
            self.semantic_embedding = embedding
        else:
            raise ValueError(f"Unknown embedding type: {embedding_type}")
        
        self.updated_at = datetime.now()
    
    def analyze_task_scenario(self) -> None:
        """分析任务场景（简化版本）"""
        if not self.title or not self.abstract:
            return
        
        # 基于标题和摘要的简单任务场景分析
        text = (self.title + " " + self.abstract).lower()
        
        # 检测应用场景
        scenario_keywords = {
            "Medical Diagnosis": ["medical", "diagnosis", "healthcare", "disease", "patient", "clinical"],
            "Autonomous Driving": ["autonomous", "driving", "vehicle", "traffic", "navigation", "road"],
            "Financial Technology": ["financial", "trading", "market", "investment", "risk", "banking"],
            "Computer Vision": ["vision", "image", "visual", "detection", "recognition", "segmentation"],
            "Natural Language Processing": ["language", "text", "nlp", "translation", "sentiment", "embedding"],
            "General Research": ["research", "method", "algorithm", "approach", "framework", "model"]
        }
        
        # 检测任务类型
        task_keywords = {
            "Classification Tasks": ["classification", "classify", "categorization", "category"],
            "Prediction Tasks": ["prediction", "predict", "forecasting", "forecast"],
            "Generation Tasks": ["generation", "generate", "synthesis", "create"],
            "Optimization Tasks": ["optimization", "optimize", "minimize", "maximize"],
        }
        
        # 找到最匹配的场景
        best_scenario = "General Research"
        best_score = 0
        for scenario, keywords in scenario_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_scenario = scenario
        
        # 找到最匹配的任务类型
        best_task = "Other Tasks"
        best_task_score = 0
        for task_type, keywords in task_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_task_score:
                best_task_score = score
                best_task = task_type
        
        # 创建任务场景分析结果
        self.task_scenario_analysis = TaskScenarioAnalysis(
            application_scenario=best_scenario,
            scenario_confidence=min(best_score / 3.0, 1.0),
            task_type=best_task,
            task_confidence=min(best_task_score / 2.0, 1.0),
            task_objectives=[],
            scenario_keywords=[],
            task_keywords=[],
            real_world_impact="",
            target_users=[],
            social_value=""
        )
        
        self.updated_at = datetime.now()
    
    def add_insight_data(self, insights: Dict[str, Any]) -> None:
        """添加深层次分析洞察数据"""
        self.insight_data = insights
        self.updated_at = datetime.now()
    
    def add_tags(self, tags: List[str]) -> None:
        """添加标签"""
        self.tags.extend(tags)
        self.tags = list(set(self.tags))  # 去重
        self.updated_at = datetime.now()
    
    def add_categories(self, categories: List[str]) -> None:
        """添加分类"""
        self.categories.extend(categories)
        self.categories = list(set(self.categories))  # 去重
        self.updated_at = datetime.now()
    
    def _update_quality_flags(self) -> None:
        """更新质量标识"""
        self.quality_flags['analysis_complete'] = (
            self.task_scenario_analysis is not None and
            self.text_embedding is not None
        )
        
        self.quality_flags['has_complete_info'] = all([
            self.title,
            self.abstract,
            self.conference,
            self.year,
            len(self.abstract.strip()) > 10 if self.abstract else False
        ])
    
    def get_search_text(self) -> str:
        """获取用于搜索的组合文本"""
        components = []
        
        if self.title:
            components.append(self.title)
        
        if self.abstract:
            components.append(self.abstract)
        
        if self.task_scenario_analysis:
            if self.task_scenario_analysis.task_objectives:
                components.extend(self.task_scenario_analysis.task_objectives)
            
            if self.task_scenario_analysis.scenario_keywords:
                components.extend(self.task_scenario_analysis.scenario_keywords)
        
        if self.keywords:
            components.extend(self.keywords[:10])  # 取前10个关键词
        
        return ' '.join(components)
    
    def get_milvus_data(self) -> Dict[str, Any]:
        """
        获取用于Milvus存储的数据格式
        
        Returns:
            包含所有字段的字典，适用于Milvus插入操作
        """
        data = {
            # 基础字段
            'paper_id': self.paper_id,
            'title': self.title or "",
            'abstract': self.abstract or "",
            'conference': self.conference,
            'year': self.year,
            'url': self.url or "",
            'pdf_url': self.pdf_url or "",
            
            # 时间戳
            'created_at': int(self.created_at.timestamp()),
            'updated_at': int(self.updated_at.timestamp()),
            
            # 任务场景分析
            'application_scenario': "",
            'scenario_confidence': 0.0,
            'task_type': "",
            'task_confidence': 0.0,
            'task_objectives': "",
            'real_world_impact': "",
            
            # 会议信息
            'venue_type': "conference",
            'ranking': "",
            
            # 指标
            'citation_count': self.metrics.citation_count,
            'influence_score': self.metrics.influence_score,
            'practical_value_score': self.metrics.practical_value_score,
            'title_length': self.metrics.title_length,
            'abstract_length': self.metrics.abstract_length,
            'keyword_count': self.metrics.keyword_count,
            
            # 文本数据
            'keywords': json.dumps(self.keywords, ensure_ascii=False),
            'tags': json.dumps(self.tags, ensure_ascii=False),
            'categories': json.dumps(self.categories, ensure_ascii=False),
            
            # 质量标识
            'has_complete_info': self.quality_flags['has_complete_info'],
            'analysis_complete': self.quality_flags['analysis_complete'],
            
            # 搜索文本
            'search_text': self.get_search_text(),
        }
        
        # 添加任务场景分析数据
        if self.task_scenario_analysis:
            tsa = self.task_scenario_analysis
            data.update({
                'application_scenario': tsa.application_scenario,
                'scenario_confidence': tsa.scenario_confidence,
                'task_type': tsa.task_type,
                'task_confidence': tsa.task_confidence,
                'task_objectives': '; '.join(tsa.task_objectives),
                'real_world_impact': tsa.real_world_impact,
            })
        
        # 添加会议信息
        if self.conference_info:
            data.update({
                'venue_type': self.conference_info.venue_type,
                'ranking': self.conference_info.ranking,
            })
        
        # 添加向量数据
        if self.text_embedding is not None:
            data['text_vector'] = self.text_embedding.tolist()
        else:
            # 如果没有向量，创建零向量占位
            data['text_vector'] = [0.0] * 768  # 假设使用768维向量
        
        # 注意: 为了兼容Milvus v2.3.3的单向量字段限制，暂时移除semantic_vector
        # 可以在后续版本中通过升级Milvus或使用多集合方案来支持多向量
        
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于JSON序列化等）"""
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'abstract': self.abstract,
            'conference': self.conference,
            'year': self.year,
            'url': self.url,
            'pdf_url': self.pdf_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'task_scenario_analysis': self.task_scenario_analysis.__dict__ if self.task_scenario_analysis else None,
            'conference_info': self.conference_info.__dict__ if self.conference_info else None,
            'author_info': self.author_info.__dict__ if self.author_info else None,
            'metrics': self.metrics.__dict__,
            'keywords': self.keywords,
            'bigrams': self.bigrams,
            'tags': self.tags,
            'categories': self.categories,
            'quality_flags': self.quality_flags,
            'has_text_embedding': self.text_embedding is not None,
            'has_semantic_embedding': self.semantic_embedding is not None,
            'insight_data_keys': list(self.insight_data.keys()) if self.insight_data else []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        """从字典创建Paper对象"""
        paper = cls(
            title=data['title'],
            abstract=data['abstract'],
            conference=data['conference'],
            year=data['year'],
            url=data.get('url'),
            pdf_url=data.get('pdf_url'),
            paper_id=data.get('paper_id')
        )
        
        # 恢复时间戳
        if 'created_at' in data:
            paper.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            paper.updated_at = datetime.fromisoformat(data['updated_at'])
        
        # 恢复分析结果
        if data.get('task_scenario_analysis'):
            tsa_data = data['task_scenario_analysis']
            paper.task_scenario_analysis = TaskScenarioAnalysis(**tsa_data)
        
        # 恢复其他数据
        if 'keywords' in data:
            paper.keywords = data['keywords']
        if 'tags' in data:
            paper.tags = data['tags']
        if 'categories' in data:
            paper.categories = data['categories']
        
        return paper
    
    def __str__(self) -> str:
        return f"Paper(id={self.paper_id}, title='{self.title[:50]}...', conference={self.conference}, year={self.year})"
    
    def __repr__(self) -> str:
        return self.__str__()