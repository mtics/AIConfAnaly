"""
Milvus数据库客户端 - 负责与Milvus数据库的连接和操作
"""

from pymilvus import (
    connections, Collection, CollectionSchema, FieldSchema, DataType,
    utility, Index
)
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
import time
import json
from datetime import datetime
import os

from .milvus_schema import MilvusSchema
from ..models.paper import Paper

logger = logging.getLogger(__name__)


class MilvusClientConfig:
    """Milvus客户端配置"""
    
    def __init__(self,
                 host: str = "localhost",
                 port: str = "19530",
                 user: str = "",
                 password: str = "",
                 db_name: str = "default",
                 alias: str = "default"):
        """
        初始化Milvus连接配置
        
        Args:
            host: Milvus服务器地址
            port: Milvus端口
            user: 用户名
            password: 密码
            db_name: 数据库名称
            alias: 连接别名
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.alias = alias
    
    @classmethod
    def from_env(cls) -> 'MilvusClientConfig':
        """从环境变量创建配置"""
        return cls(
            host=os.getenv('MILVUS_HOST', 'localhost'),
            port=os.getenv('MILVUS_PORT', '19530'),
            user=os.getenv('MILVUS_USER', ''),
            password=os.getenv('MILVUS_PASSWORD', ''),
            db_name=os.getenv('MILVUS_DB', 'default'),
            alias=os.getenv('MILVUS_ALIAS', 'default')
        )


class MilvusClient:
    """
    Milvus数据库客户端
    提供论文数据的存储、检索和管理功能
    """
    
    def __init__(self, config: Optional[MilvusClientConfig] = None, vector_dim: int = 768):
        """
        初始化Milvus客户端
        
        Args:
            config: 连接配置
            vector_dim: 向量维度
        """
        self.config = config or MilvusClientConfig.from_env()
        self.vector_dim = vector_dim
        self.schema_manager = MilvusSchema(vector_dim)
        self.collection: Optional[Collection] = None
        self.connected = False
        
        # 连接到Milvus
        if not self.connect():
            raise Exception(f"Failed to connect to Milvus server at {self.config.host}:{self.config.port}")
        
        # 初始化集合
        if not self.initialize_collection():
            raise Exception("Failed to initialize Milvus collection")
    
    def connect(self) -> bool:
        """
        连接到Milvus服务器
        
        Returns:
            bool: 是否连接成功
        """
        try:
            # 检查是否已连接
            if self.connected:
                return True
            
            # 建立连接
            connections.connect(
                alias=self.config.alias,
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                db_name=self.config.db_name
            )
            
            # 验证连接
            server_version = utility.get_server_version()
            logger.info(f"Connected to Milvus server {self.config.host}:{self.config.port}, version: {server_version}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """断开连接"""
        try:
            if self.connected:
                connections.disconnect(self.config.alias)
                self.connected = False
                logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {e}")
    
    def initialize_collection(self) -> bool:
        """
        初始化集合（如果不存在则创建）
        
        Returns:
            bool: 是否初始化成功
        """
        try:
            collection_name = self.schema_manager.collection_name
            
            # 检查集合是否存在
            if utility.has_collection(collection_name):
                logger.info(f"Collection '{collection_name}' already exists")
                self.collection = Collection(collection_name)
                
                # 检查并加载集合
                if not self.collection.has_index():
                    logger.info("Creating indexes for existing collection...")
                    self._create_indexes()
                
                # 加载集合到内存
                self.collection.load()
                logger.info(f"Collection '{collection_name}' loaded successfully")
                
            else:
                logger.info(f"Creating new collection '{collection_name}'...")
                self._create_collection()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            return False
    
    def _create_collection(self) -> None:
        """创建新集合"""
        # 获取schema
        schema = self.schema_manager.create_schema()
        
        # 创建集合
        self.collection = Collection(
            name=self.schema_manager.collection_name,
            schema=schema,
            using=self.config.alias
        )
        
        logger.info(f"Created collection '{self.schema_manager.collection_name}'")
        
        # 创建索引
        self._create_indexes()
        
        # 加载集合
        self.collection.load()
        logger.info("Collection created and loaded successfully")
    
    def _create_indexes(self) -> None:
        """创建索引"""
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        index_definitions = self.schema_manager.get_index_definitions()
        
        for index_name, index_config in index_definitions.items():
            try:
                # 创建索引
                index_params = {
                    "index_type": index_config["index_type"],
                    "metric_type": index_config.get("metric_type", "COSINE"),
                    "params": index_config.get("params", {})
                }
                
                self.collection.create_index(
                    field_name=index_config["field_name"],
                    index_params=index_params,
                    index_name=index_name
                )
                
                logger.info(f"Created index '{index_name}' on field '{index_config['field_name']}'")
                
            except Exception as e:
                logger.warning(f"Failed to create index '{index_name}': {e}")
    
    def insert_paper(self, paper: Paper) -> bool:
        """
        插入单篇论文
        
        Args:
            paper: Paper对象
            
        Returns:
            bool: 是否插入成功
        """
        try:
            if not self.collection:
                raise ValueError("Collection not initialized")
            
            # 获取Milvus格式的数据
            data = paper.get_milvus_data()
            
            # 转换为列表格式
            insert_data = self._convert_to_insert_format([data])
            
            # 插入数据
            result = self.collection.insert(insert_data)
            
            # 刷新以确保数据持久化
            self.collection.flush()
            
            logger.info(f"Inserted paper '{paper.paper_id}' successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert paper '{paper.paper_id}': {e}")
            return False
    
    def batch_insert_papers(self, papers: List[Paper], batch_size: int = 100) -> Tuple[int, int]:
        """
        批量插入论文
        
        Args:
            papers: Paper对象列表
            batch_size: 批次大小
            
        Returns:
            Tuple[int, int]: (成功数量, 总数量)
        """
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        total_count = len(papers)
        success_count = 0
        
        logger.info(f"Starting batch insert of {total_count} papers...")
        
        # 分批处理
        for i in range(0, total_count, batch_size):
            batch_papers = papers[i:i + batch_size]
            
            try:
                # 准备批次数据
                batch_data = []
                for paper in batch_papers:
                    data = paper.get_milvus_data()
                    batch_data.append(data)
                
                # 转换为插入格式
                insert_data = self._convert_to_insert_format(batch_data)
                
                # 插入批次
                result = self.collection.insert(insert_data)
                success_count += len(batch_papers)
                
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch_papers)} papers")
                
            except Exception as e:
                logger.error(f"Failed to insert batch {i//batch_size + 1}: {e}")
        
        # 刷新数据
        self.collection.flush()
        
        logger.info(f"Batch insert completed: {success_count}/{total_count} papers inserted successfully")
        return success_count, total_count
    
    def _convert_to_insert_format(self, data_list: List[Dict]) -> List[List]:
        """
        转换数据为Milvus插入格式
        
        Args:
            data_list: 数据字典列表
            
        Returns:
            List[List]: 按字段组织的数据列表
        """
        if not data_list:
            return []
        
        # 获取所有字段名
        field_names = list(data_list[0].keys())
        
        # 按字段组织数据
        insert_data = []
        for field_name in field_names:
            field_data = [item.get(field_name) for item in data_list]
            insert_data.append(field_data)
        
        return insert_data
    
    def search_similar_papers(self, 
                            query_vector: np.ndarray,
                            vector_field: str = "text_vector",
                            top_k: int = 10,
                            filters: Optional[str] = None,
                            output_fields: Optional[List[str]] = None) -> List[Dict]:
        """
        搜索相似论文
        
        Args:
            query_vector: 查询向量
            vector_field: 向量字段名
            top_k: 返回结果数量
            filters: 过滤条件
            output_fields: 输出字段
            
        Returns:
            List[Dict]: 搜索结果
        """
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        try:
            # 默认输出字段
            if output_fields is None:
                output_fields = [
                    "paper_id", "title", "abstract", "conference", "year",
                    "application_scenario", "task_type", "practical_value_score"
                ]
            
            # 搜索参数
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 32}
            }
            
            # 执行搜索
            results = self.collection.search(
                data=[query_vector.tolist()],
                anns_field=vector_field,
                param=search_params,
                limit=top_k,
                expr=filters,
                output_fields=output_fields
            )
            
            # 处理结果
            formatted_results = []
            for hits in results:
                for hit in hits:
                    result_data = {
                        "score": hit.score,
                        "distance": hit.distance,
                        **hit.entity.fields
                    }
                    formatted_results.append(result_data)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar papers: {e}")
            return []
    
    def search_by_text(self, 
                      query_text: str,
                      text_encoder,
                      top_k: int = 10,
                      filters: Optional[str] = None) -> List[Dict]:
        """
        基于文本搜索论文
        
        Args:
            query_text: 查询文本
            text_encoder: 文本编码器
            top_k: 返回结果数量
            filters: 过滤条件
            
        Returns:
            List[Dict]: 搜索结果
        """
        try:
            # 编码查询文本
            query_vector = text_encoder.encode(query_text)
            if query_vector.ndim > 1:
                query_vector = query_vector[0]
            
            # 执行向量搜索
            return self.search_similar_papers(
                query_vector=query_vector,
                top_k=top_k,
                filters=filters
            )
            
        except Exception as e:
            logger.error(f"Failed to search by text: {e}")
            return []
    
    def hybrid_search(self,
                     text_query: str,
                     semantic_query: Dict[str, str],
                     text_encoder,
                     top_k: int = 10,
                     text_weight: float = 0.7,
                     semantic_weight: float = 0.3) -> List[Dict]:
        """
        混合搜索（文本 + 语义）
        
        Args:
            text_query: 文本查询
            semantic_query: 语义查询 {"scenario": "Medical Diagnosis", "task": "Classification"}
            text_encoder: 文本编码器
            top_k: 返回结果数量
            text_weight: 文本权重
            semantic_weight: 语义权重
            
        Returns:
            List[Dict]: 混合搜索结果
        """
        try:
            # 文本搜索
            text_results = self.search_by_text(text_query, text_encoder, top_k * 2)
            
            # 语义搜索
            semantic_text = f"Application: {semantic_query.get('scenario', '')} Task: {semantic_query.get('task', '')}"
            semantic_vector = text_encoder.encode(semantic_text)
            if semantic_vector.ndim > 1:
                semantic_vector = semantic_vector[0]
            
            semantic_results = self.search_similar_papers(
                query_vector=semantic_vector,
                vector_field="semantic_vector",
                top_k=top_k * 2
            )
            
            # 合并和重排序结果
            combined_results = self._merge_search_results(
                text_results, semantic_results, text_weight, semantic_weight
            )
            
            return combined_results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to perform hybrid search: {e}")
            return []
    
    def _merge_search_results(self, 
                            text_results: List[Dict],
                            semantic_results: List[Dict],
                            text_weight: float,
                            semantic_weight: float) -> List[Dict]:
        """合并搜索结果"""
        
        # 创建结果字典
        merged_results = {}
        
        # 处理文本搜索结果
        for result in text_results:
            paper_id = result["paper_id"]
            score = result["score"] * text_weight
            merged_results[paper_id] = {
                **result,
                "combined_score": score,
                "text_score": result["score"],
                "semantic_score": 0.0
            }
        
        # 处理语义搜索结果
        for result in semantic_results:
            paper_id = result["paper_id"]
            semantic_score = result["score"] * semantic_weight
            
            if paper_id in merged_results:
                # 更新现有结果
                merged_results[paper_id]["combined_score"] += semantic_score
                merged_results[paper_id]["semantic_score"] = result["score"]
            else:
                # 添加新结果
                merged_results[paper_id] = {
                    **result,
                    "combined_score": semantic_score,
                    "text_score": 0.0,
                    "semantic_score": result["score"]
                }
        
        # 按综合得分排序
        sorted_results = sorted(
            merged_results.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )
        
        return sorted_results
    
    def filter_papers(self, 
                     filters: Dict[str, Any],
                     limit: int = 1000) -> List[Dict]:
        """
        过滤论文
        
        Args:
            filters: 过滤条件字典
            limit: 结果数量限制
            
        Returns:
            List[Dict]: 过滤结果
        """
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        try:
            # 构建过滤表达式
            filter_expr = self._build_filter_expression(filters)
            
            # 输出字段
            output_fields = [
                "paper_id", "title", "abstract", "conference", "year",
                "application_scenario", "task_type", "scenario_confidence",
                "task_confidence", "practical_value_score"
            ]
            
            # 执行查询
            results = self.collection.query(
                expr=filter_expr,
                output_fields=output_fields,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to filter papers: {e}")
            return []
    
    def _build_filter_expression(self, filters: Dict[str, Any]) -> str:
        """构建过滤表达式"""
        conditions = []
        
        # 年份范围
        if "year_range" in filters:
            year_range = filters["year_range"]
            if len(year_range) == 2:
                conditions.append(f"year >= {year_range[0]} and year <= {year_range[1]}")
        
        # 单个年份
        if "year" in filters:
            conditions.append(f"year == {filters['year']}")
        
        # 会议
        if "conference" in filters:
            if isinstance(filters["conference"], list):
                conf_list = "', '".join(filters["conference"])
                conditions.append(f"conference in ['{conf_list}']")
            else:
                conditions.append(f"conference == '{filters['conference']}'")
        
        # 应用场景
        if "application_scenario" in filters:
            conditions.append(f"application_scenario == '{filters['application_scenario']}'")
        
        # 任务类型
        if "task_type" in filters:
            conditions.append(f"task_type == '{filters['task_type']}'")
        
        # 置信度阈值
        if "min_confidence" in filters:
            conditions.append(f"scenario_confidence >= {filters['min_confidence']}")
        
        # 实用价值评分
        if "min_practical_value" in filters:
            conditions.append(f"practical_value_score >= {filters['min_practical_value']}")
        
        # 是否包含完整信息
        if "complete_only" in filters and filters["complete_only"]:
            conditions.append("has_complete_info == true")
        
        # 合并条件
        if conditions:
            return " and ".join(conditions)
        else:
            return ""  # 无过滤条件
    
    def get_existing_paper_ids(self, conferences: List[str] = None, years: List[int] = None) -> set:
        """
        获取数据库中已存在的论文ID集合
        
        Args:
            conferences: 限制的会议列表
            years: 限制的年份列表
            
        Returns:
            set: 已存在的论文ID集合
        """
        if not self.collection:
            return set()
        
        try:
            # 构建查询条件
            filter_conditions = []
            
            if conferences:
                conf_condition = " or ".join([f'conference == "{conf}"' for conf in conferences])
                filter_conditions.append(f"({conf_condition})")
            
            if years:
                year_condition = " or ".join([f'year == {year}' for year in years])
                filter_conditions.append(f"({year_condition})")
            
            # 组合查询条件
            filter_expr = " and ".join(filter_conditions) if filter_conditions else None
            
            # 查询所有论文ID
            results = self.collection.query(
                expr=filter_expr,
                output_fields=["paper_id"],
                limit=16384  # Milvus默认最大限制
            )
            
            # 提取论文ID
            existing_ids = {result["paper_id"] for result in results}
            
            logger.info(f"Found {len(existing_ids)} existing papers in database")
            return existing_ids
            
        except Exception as e:
            logger.error(f"Failed to get existing paper IDs: {e}")
            return set()
    
    def check_papers_exist(self, paper_ids: List[str]) -> Dict[str, bool]:
        """
        检查论文是否已存在于数据库中
        
        Args:
            paper_ids: 要检查的论文ID列表
            
        Returns:
            Dict[str, bool]: 论文ID -> 是否存在的映射
        """
        if not self.collection or not paper_ids:
            return {}
        
        try:
            # 分批查询（避免查询条件过长）
            batch_size = 100
            existence_map = {}
            
            for i in range(0, len(paper_ids), batch_size):
                batch_ids = paper_ids[i:i + batch_size]
                
                # 构建查询条件
                id_conditions = [f'paper_id == "{pid}"' for pid in batch_ids]
                filter_expr = " or ".join(id_conditions)
                
                # 查询存在的论文
                results = self.collection.query(
                    expr=filter_expr,
                    output_fields=["paper_id"],
                    limit=len(batch_ids)
                )
                
                # 构建存在性映射
                existing_ids = {result["paper_id"] for result in results}
                for pid in batch_ids:
                    existence_map[pid] = pid in existing_ids
            
            return existence_map
            
        except Exception as e:
            logger.error(f"Failed to check paper existence: {e}")
            return {pid: False for pid in paper_ids}

    def get_collection_info(self) -> Dict[str, Any]:
        """
        获取集合信息
        
        Returns:
            Dict: 集合统计信息
        """
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            # 基本信息
            info = {
                "collection_name": self.collection.name,
                "description": self.collection.description,
                "schema": {
                    "fields": [
                        {
                            "name": field.name,
                            "type": str(field.dtype),
                            "description": field.description
                        }
                        for field in self.collection.schema.fields
                    ]
                }
            }
            
            # 统计信息 - 使用兼容的方法获取
            try:
                # 尝试获取集合统计信息
                stats = {
                    "row_count": self.collection.num_entities,
                    "collection_name": self.collection.name,
                    "description": self.collection.description
                }
                info["statistics"] = stats
            except Exception as e:
                logger.warning(f"Could not get collection statistics: {e}")
                info["statistics"] = {"row_count": "unknown"}
            
            # 索引信息
            info["indexes"] = []
            for field in self.collection.schema.fields:
                try:
                    index_info = self.collection.index(field.name)
                    if index_info:
                        info["indexes"].append({
                            "field": field.name,
                            "index_type": index_info.index_type,
                            "metric_type": index_info.metric_type
                        })
                except:
                    pass
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
    
    def delete_papers(self, paper_ids: List[str]) -> bool:
        """
        删除论文
        
        Args:
            paper_ids: 论文ID列表
            
        Returns:
            bool: 是否删除成功
        """
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        try:
            # 构建删除表达式
            id_list = "', '".join(paper_ids)
            delete_expr = f"paper_id in ['{id_list}']"
            
            # 执行删除
            result = self.collection.delete(delete_expr)
            
            # 刷新数据
            self.collection.flush()
            
            logger.info(f"Deleted {len(paper_ids)} papers successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete papers: {e}")
            return False
    
    def update_paper(self, paper: Paper) -> bool:
        """
        更新论文（先删除再插入）
        
        Args:
            paper: Paper对象
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 删除现有记录
            self.delete_papers([paper.paper_id])
            
            # 插入新记录
            return self.insert_paper(paper)
            
        except Exception as e:
            logger.error(f"Failed to update paper '{paper.paper_id}': {e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()