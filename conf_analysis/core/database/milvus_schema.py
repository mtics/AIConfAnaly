"""
Milvus数据库schema和索引结构定义
"""

from pymilvus import CollectionSchema, FieldSchema, DataType, Collection
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MilvusSchema:
    """Milvus数据库架构定义"""
    
    def __init__(self, vector_dim: int = 768):
        """
        初始化Milvus架构
        
        Args:
            vector_dim: 向量维度，默认768（BERT/RoBERTa标准维度）
        """
        self.vector_dim = vector_dim
        self.collection_name = "conference_papers"
        self.description = "AI/ML会议论文集合，包含任务场景分析和向量表示"
        
    def create_schema(self) -> CollectionSchema:
        """
        创建Milvus集合的schema定义
        
        Returns:
            CollectionSchema: 定义好的数据库架构
        """
        
        # 定义所有字段
        fields = [
            # ================ 主键和基础信息 ================
            FieldSchema(
                name="paper_id", 
                dtype=DataType.VARCHAR, 
                max_length=64,
                is_primary=True,
                description="论文唯一标识符"
            ),
            
            FieldSchema(
                name="title", 
                dtype=DataType.VARCHAR, 
                max_length=512,
                description="论文标题"
            ),
            
            FieldSchema(
                name="abstract", 
                dtype=DataType.VARCHAR, 
                max_length=8192,
                description="论文摘要"
            ),
            
            FieldSchema(
                name="conference", 
                dtype=DataType.VARCHAR, 
                max_length=64,
                description="会议名称"
            ),
            
            FieldSchema(
                name="year", 
                dtype=DataType.INT32,
                description="发表年份"
            ),
            
            FieldSchema(
                name="url", 
                dtype=DataType.VARCHAR, 
                max_length=512,
                description="论文链接"
            ),
            
            FieldSchema(
                name="pdf_url", 
                dtype=DataType.VARCHAR, 
                max_length=512,
                description="PDF下载链接"
            ),
            
            # ================ 时间戳 ================
            FieldSchema(
                name="created_at", 
                dtype=DataType.INT64,
                description="创建时间戳"
            ),
            
            FieldSchema(
                name="updated_at", 
                dtype=DataType.INT64,
                description="更新时间戳"
            ),
            
            # ================ 任务场景分析结果 ================
            FieldSchema(
                name="application_scenario", 
                dtype=DataType.VARCHAR, 
                max_length=128,
                description="应用场景分类"
            ),
            
            FieldSchema(
                name="scenario_confidence", 
                dtype=DataType.FLOAT,
                description="应用场景分类置信度"
            ),
            
            FieldSchema(
                name="task_type", 
                dtype=DataType.VARCHAR, 
                max_length=128,
                description="任务类型分类"
            ),
            
            FieldSchema(
                name="task_confidence", 
                dtype=DataType.FLOAT,
                description="任务类型分类置信度"
            ),
            
            FieldSchema(
                name="task_objectives", 
                dtype=DataType.VARCHAR, 
                max_length=1024,
                description="任务目标描述"
            ),
            
            FieldSchema(
                name="real_world_impact", 
                dtype=DataType.VARCHAR, 
                max_length=512,
                description="现实世界影响描述"
            ),
            
            # ================ 会议和作者信息 ================
            FieldSchema(
                name="venue_type", 
                dtype=DataType.VARCHAR, 
                max_length=32,
                description="发表场所类型：conference/journal/workshop"
            ),
            
            FieldSchema(
                name="ranking", 
                dtype=DataType.VARCHAR, 
                max_length=16,
                description="会议排名：A*/A/B/C"
            ),
            
            # ================ 论文指标 ================
            FieldSchema(
                name="citation_count", 
                dtype=DataType.INT32,
                description="引用次数"
            ),
            
            FieldSchema(
                name="influence_score", 
                dtype=DataType.FLOAT,
                description="影响力评分"
            ),
            
            FieldSchema(
                name="practical_value_score", 
                dtype=DataType.FLOAT,
                description="实用价值评分"
            ),
            
            FieldSchema(
                name="title_length", 
                dtype=DataType.INT32,
                description="标题长度"
            ),
            
            FieldSchema(
                name="abstract_length", 
                dtype=DataType.INT32,
                description="摘要长度"
            ),
            
            FieldSchema(
                name="keyword_count", 
                dtype=DataType.INT32,
                description="关键词数量"
            ),
            
            # ================ 文本和标签数据 ================
            FieldSchema(
                name="keywords", 
                dtype=DataType.VARCHAR, 
                max_length=2048,
                description="关键词列表（JSON格式）"
            ),
            
            FieldSchema(
                name="tags", 
                dtype=DataType.VARCHAR, 
                max_length=1024,
                description="标签列表（JSON格式）"
            ),
            
            FieldSchema(
                name="categories", 
                dtype=DataType.VARCHAR, 
                max_length=512,
                description="分类列表（JSON格式）"
            ),
            
            # ================ 质量标识 ================
            FieldSchema(
                name="has_complete_info", 
                dtype=DataType.BOOL,
                description="是否有完整信息"
            ),
            
            FieldSchema(
                name="analysis_complete", 
                dtype=DataType.BOOL,
                description="是否完成分析"
            ),
            
            # ================ 搜索字段 ================
            FieldSchema(
                name="search_text", 
                dtype=DataType.VARCHAR, 
                max_length=16384,
                description="组合搜索文本"
            ),
            
            # ================ 向量字段 ================
            FieldSchema(
                name="text_vector", 
                dtype=DataType.FLOAT_VECTOR, 
                dim=self.vector_dim,
                description="文本向量表示（标题+摘要）"
            ),
            
            FieldSchema(
                name="semantic_vector", 
                dtype=DataType.FLOAT_VECTOR, 
                dim=self.vector_dim,
                description="语义向量表示（任务+场景）"
            ),
        ]
        
        # 创建schema
        schema = CollectionSchema(
            fields=fields,
            description=self.description,
            enable_dynamic_field=True  # 允许动态字段
        )
        
        return schema
    
    def get_index_definitions(self) -> Dict[str, Dict]:
        """
        获取索引定义
        
        Returns:
            Dict: 包含所有需要创建的索引定义
        """
        
        indexes = {
            # 向量索引 - 用于相似性搜索
            "text_vector_index": {
                "field_name": "text_vector",
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",  # 余弦相似度
                "params": {"nlist": 1024},
                "description": "文本向量索引，用于语义相似性搜索"
            },
            
            "semantic_vector_index": {
                "field_name": "semantic_vector", 
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 1024},
                "description": "语义向量索引，用于任务场景相似性搜索"
            },
            
            # 标量索引 - 用于过滤和排序
            "conference_index": {
                "field_name": "conference",
                "index_type": "INVERTED",
                "description": "会议名称索引，用于按会议过滤"
            },
            
            "year_index": {
                "field_name": "year",
                "index_type": "INVERTED", 
                "description": "年份索引，用于时间范围查询"
            },
            
            "application_scenario_index": {
                "field_name": "application_scenario",
                "index_type": "INVERTED",
                "description": "应用场景索引，用于按场景分类"
            },
            
            "task_type_index": {
                "field_name": "task_type",
                "index_type": "INVERTED",
                "description": "任务类型索引，用于按任务分类"
            },
            
            "venue_type_index": {
                "field_name": "venue_type",
                "index_type": "INVERTED",
                "description": "场所类型索引"
            },
            
            "ranking_index": {
                "field_name": "ranking",
                "index_type": "INVERTED",
                "description": "会议排名索引"
            },
        }
        
        return indexes
    
    def get_search_params(self) -> Dict[str, Dict]:
        """
        获取搜索参数配置
        
        Returns:
            Dict: 包含不同类型搜索的参数配置
        """
        
        search_params = {
            # 向量搜索参数
            "vector_search": {
                "text_vector": {
                    "metric_type": "COSINE",
                    "params": {"nprobe": 32},
                    "description": "文本语义搜索参数"
                },
                
                "semantic_vector": {
                    "metric_type": "COSINE", 
                    "params": {"nprobe": 32},
                    "description": "任务场景搜索参数"
                }
            },
            
            # 混合搜索参数
            "hybrid_search": {
                "text_weight": 0.7,      # 文本相似性权重
                "semantic_weight": 0.3,  # 语义相似性权重
                "filter_threshold": 0.5, # 过滤阈值
                "rerank_size": 100,      # 重排序候选数量
                "description": "混合搜索权重配置"
            },
            
            # 过滤搜索参数
            "filter_search": {
                "year_range": [2018, 2024],           # 默认年份范围
                "min_confidence": 0.6,               # 最小分类置信度
                "include_incomplete": False,          # 是否包含不完整数据
                "min_practical_value": 0.0,         # 最小实用价值评分
                "description": "过滤条件配置"
            }
        }
        
        return search_params
    
    def get_collection_config(self) -> Dict:
        """
        获取集合配置参数
        
        Returns:
            Dict: 集合配置信息
        """
        
        config = {
            "collection_name": self.collection_name,
            "description": self.description,
            "shard_num": 2,                    # 分片数量
            "consistency_level": "Strong",     # 一致性级别
            
            # 性能配置
            "performance": {
                "max_insert_batch_size": 1000,   # 最大批量插入大小
                "index_building_threshold": 1024, # 索引构建阈值
                "search_timeout": 30,            # 搜索超时时间（秒）
                "max_result_window": 10000,      # 最大结果窗口
            },
            
            # 内存配置
            "memory": {
                "loading_replica_number": 1,     # 加载副本数
                "resource_groups": ["default"],  # 资源组
            },
            
            # 备份配置
            "backup": {
                "auto_backup": True,              # 自动备份
                "backup_interval_hours": 24,     # 备份间隔（小时）
                "retention_days": 30,            # 保留天数
            }
        }
        
        return config
    
    def validate_schema(self) -> bool:
        """
        验证schema定义的有效性
        
        Returns:
            bool: 是否有效
        """
        try:
            schema = self.create_schema()
            
            # 验证必要字段
            required_fields = ['paper_id', 'title', 'text_vector']
            schema_fields = [field.name for field in schema.fields]
            
            for field in required_fields:
                if field not in schema_fields:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # 验证向量维度
            for field in schema.fields:
                if field.dtype == DataType.FLOAT_VECTOR:
                    if field.dim != self.vector_dim:
                        logger.error(f"Vector dimension mismatch for {field.name}: {field.dim} != {self.vector_dim}")
                        return False
            
            logger.info("Schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def get_field_mapping(self) -> Dict[str, str]:
        """
        获取字段映射关系（用于数据转换）
        
        Returns:
            Dict: Paper对象属性到Milvus字段的映射
        """
        
        mapping = {
            # 基础字段映射
            'paper_id': 'paper_id',
            'title': 'title', 
            'abstract': 'abstract',
            'conference': 'conference',
            'year': 'year',
            'url': 'url',
            'pdf_url': 'pdf_url',
            
            # 时间戳映射
            'created_at': 'created_at',
            'updated_at': 'updated_at',
            
            # 分析结果映射
            'task_scenario_analysis.application_scenario': 'application_scenario',
            'task_scenario_analysis.scenario_confidence': 'scenario_confidence',
            'task_scenario_analysis.task_type': 'task_type',
            'task_scenario_analysis.task_confidence': 'task_confidence',
            'task_scenario_analysis.task_objectives': 'task_objectives',
            'task_scenario_analysis.real_world_impact': 'real_world_impact',
            
            # 指标映射
            'metrics.citation_count': 'citation_count',
            'metrics.influence_score': 'influence_score',
            'metrics.practical_value_score': 'practical_value_score',
            'metrics.title_length': 'title_length',
            'metrics.abstract_length': 'abstract_length',
            'metrics.keyword_count': 'keyword_count',
            
            # 向量映射
            'text_embedding': 'text_vector',
            'semantic_embedding': 'semantic_vector',
        }
        
        return mapping