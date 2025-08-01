"""
简单本地向量存储 - 不依赖FAISS的轻量级替代方案
使用cosine相似度进行向量搜索，本地JSON文件存储
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

from ..models.paper import Paper

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """简单本地向量存储系统"""
    
    def __init__(self, storage_dir: str = "outputs/vector_store", vector_dim: int = 384):
        """
        初始化简单向量存储
        
        Args:
            storage_dir: 存储目录
            vector_dim: 向量维度
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.vector_dim = vector_dim
        self.metadata_file = self.storage_dir / "papers_metadata.json"
        self.vectors_file = self.storage_dir / "vectors.npy"
        self.id_mapping_file = self.storage_dir / "id_mapping.json"
        
        # 存储结构
        self.papers_metadata = {}  # paper_id -> metadata
        self.paper_vectors = None  # numpy array of vectors
        self.paper_ids = []  # list of paper_ids corresponding to vectors
        
        self.connected = False
        self._load_existing_data()
    
    def connect(self) -> bool:
        """连接到本地存储"""
        try:
            self.connected = True
            logger.info(f"Connected to simple vector store at {self.storage_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to simple vector store: {e}")
            return False
    
    def _load_existing_data(self):
        """加载已存在的数据"""
        try:
            # 加载元数据
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.papers_metadata = json.load(f)
                logger.info(f"Loaded {len(self.papers_metadata)} papers metadata")
            
            # 加载向量和ID映射
            if self.vectors_file.exists() and self.id_mapping_file.exists():
                self.paper_vectors = np.load(self.vectors_file)
                with open(self.id_mapping_file, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                    self.paper_ids = mapping_data.get('paper_ids', [])
                
                logger.info(f"Loaded {len(self.paper_ids)} paper vectors")
            
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
    
    def _save_data(self):
        """保存数据到磁盘"""
        try:
            # 保存元数据
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.papers_metadata, f, ensure_ascii=False, indent=2)
            
            # 保存向量
            if self.paper_vectors is not None:
                np.save(self.vectors_file, self.paper_vectors)
            
            # 保存ID映射
            mapping_data = {
                'paper_ids': self.paper_ids,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.id_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, ensure_ascii=False, indent=2)
            
            logger.info("Data saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def insert_paper(self, paper: Paper) -> bool:
        """插入单篇论文"""
        if not self.connected:
            return False
        
        try:
            paper_data = paper.get_milvus_data()
            paper_id = paper_data['paper_id']
            
            # 检查是否已存在
            if paper_id in self.papers_metadata:
                logger.warning(f"Paper {paper_id} already exists, skipping")
                return True
            
            # 获取向量
            text_vector = paper_data.get('text_vector')
            if text_vector is None:
                logger.warning(f"No text vector for paper {paper_id}")
                return False
            
            # 添加向量
            vector = np.array(text_vector, dtype=np.float32)
            if self.paper_vectors is None:
                self.paper_vectors = vector.reshape(1, -1)
            else:
                self.paper_vectors = np.vstack([self.paper_vectors, vector.reshape(1, -1)])
            
            # 添加ID
            self.paper_ids.append(paper_id)
            
            # 保存元数据
            metadata = {
                'paper_id': paper_id,
                'title': paper_data.get('title', ''),
                'abstract': paper_data.get('abstract', ''),
                'authors': paper_data.get('authors', ''),
                'conference': paper_data.get('conference', ''),
                'year': paper_data.get('year', 0),
                'application_scenario': paper_data.get('application_scenario', ''),
                'task_type': paper_data.get('task_type', ''),
                'practical_value_score': paper_data.get('practical_value_score', 0.0),
                'has_complete_info': paper_data.get('has_complete_info', False),
                'created_at': datetime.now().isoformat()
            }
            
            self.papers_metadata[paper_id] = metadata
            
            logger.debug(f"Inserted paper: {paper_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert paper {paper.paper_id}: {e}")
            return False
    
    def batch_insert_papers(self, papers: List[Paper], batch_size: int = 100) -> Tuple[int, int]:
        """批量插入论文"""
        if not self.connected:
            return 0, len(papers)
        
        success_count = 0
        total_count = len(papers)
        
        logger.info(f"Starting batch insert of {total_count} papers...")
        
        for i, paper in enumerate(papers):
            if self.insert_paper(paper):
                success_count += 1
            
            # 定期保存
            if (i + 1) % batch_size == 0:
                self._save_data()
                logger.info(f"Batch insert progress: {i + 1}/{total_count}")
        
        # 最终保存
        self._save_data()
        
        logger.info(f"Batch insert completed: {success_count}/{total_count} papers inserted")
        return success_count, total_count
    
    def search_similar_papers(self, 
                            query_vector: np.ndarray,
                            top_k: int = 10,
                            filters: Optional[Dict] = None) -> List[Dict]:
        """搜索相似论文"""
        if not self.connected or self.paper_vectors is None or len(self.paper_ids) == 0:
            return []
        
        try:
            # 计算余弦相似度
            query_vector = query_vector.reshape(1, -1)
            similarities = cosine_similarity(query_vector, self.paper_vectors)[0]
            
            # 获取top_k索引
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                paper_id = self.paper_ids[idx]
                if paper_id in self.papers_metadata:
                    metadata = self.papers_metadata[paper_id]
                    
                    # 应用过滤器
                    if filters and not self._apply_filters(metadata, filters):
                        continue
                    
                    result = {
                        'score': float(similarities[idx]),
                        'paper_id': paper_id,
                        **metadata
                    }
                    results.append(result)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to search similar papers: {e}")
            return []
    
    def _apply_filters(self, metadata: Dict, filters: Dict) -> bool:
        """应用过滤条件"""
        try:
            # 年份过滤
            if 'year' in filters:
                if metadata.get('year') != filters['year']:
                    return False
            
            if 'year_range' in filters:
                year_range = filters['year_range']
                paper_year = metadata.get('year', 0)
                if len(year_range) == 2 and not (year_range[0] <= paper_year <= year_range[1]):
                    return False
            
            # 会议过滤
            if 'conference' in filters:
                if isinstance(filters['conference'], list):
                    if metadata.get('conference') not in filters['conference']:
                        return False
                else:
                    if metadata.get('conference') != filters['conference']:
                        return False
            
            # 应用场景过滤
            if 'application_scenario' in filters:
                if metadata.get('application_scenario') != filters['application_scenario']:
                    return False
            
            # 任务类型过滤
            if 'task_type' in filters:
                if metadata.get('task_type') != filters['task_type']:
                    return False
            
            # 实用价值评分过滤
            if 'min_practical_value' in filters:
                if metadata.get('practical_value_score', 0) < filters['min_practical_value']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            return True
    
    def get_existing_paper_ids(self, conferences: List[str] = None, years: List[int] = None) -> set:
        """获取已存在的论文ID"""
        existing_ids = set()
        
        for paper_id, metadata in self.papers_metadata.items():
            # 应用会议过滤
            if conferences and metadata.get('conference') not in conferences:
                continue
            
            # 应用年份过滤
            if years and metadata.get('year') not in years:
                continue
            
            existing_ids.add(paper_id)
        
        logger.info(f"Found {len(existing_ids)} existing papers matching criteria")
        return existing_ids
    
    def check_papers_exist(self, paper_ids: List[str]) -> Dict[str, bool]:
        """检查论文是否存在"""
        return {pid: pid in self.papers_metadata for pid in paper_ids}
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        return {
            'storage_type': 'SimpleVectorStore',
            'storage_dir': str(self.storage_dir),
            'total_papers': len(self.papers_metadata),
            'vector_dimension': self.vector_dim,
            'vectors_loaded': self.paper_vectors is not None,
            'vector_count': len(self.paper_ids) if self.paper_ids else 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def disconnect(self):
        """断开连接并保存数据"""
        if self.connected:
            self._save_data()
            self.connected = False
            logger.info("Disconnected from simple vector store")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()