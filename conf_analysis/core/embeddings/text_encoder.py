"""
文本编码器 - 将论文文本转换为向量表示
支持多种预训练模型和编码策略
"""

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Union, Tuple
import logging
import os
from abc import ABC, abstractmethod
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseTextEncoder(ABC):
    """文本编码器基类"""
    
    @abstractmethod
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """编码文本为向量"""
        pass
    
    @abstractmethod
    def get_embedding_dim(self) -> int:
        """获取向量维度"""
        pass


class SentenceTransformerEncoder(BaseTextEncoder):
    """基于SentenceTransformers的编码器"""
    
    def __init__(self, 
                 model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2',
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        初始化SentenceTransformer编码器
        
        Args:
            model_name: 模型名称
            device: 设备（cuda/cpu）
            cache_dir: 缓存目录
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.cache_dir = cache_dir
        
        try:
            self.model = SentenceTransformer(
                model_name, 
                device=self.device,
                cache_folder=cache_dir
            )
            logger.info(f"Loaded SentenceTransformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            # 回退到更小的模型
            self.model_name = 'paraphrase-MiniLM-L6-v2'
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Fallback to model: {self.model_name}")
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        编码文本为向量
        
        Args:
            texts: 单个文本或文本列表
            
        Returns:
            np.ndarray: 向量表示
        """
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            # 清理和预处理文本
            cleaned_texts = [self._clean_text(text) for text in texts]
            
            # 编码
            embeddings = self.model.encode(
                cleaned_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,  # L2归一化
                show_progress_bar=len(cleaned_texts) > 100
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            # 返回零向量
            dim = self.get_embedding_dim()
            return np.zeros((len(texts), dim), dtype=np.float32)
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除过长的文本（超过512 tokens）
        if len(text.split()) > 400:
            text = ' '.join(text.split()[:400])
        
        # 基本清理
        text = text.strip()
        text = ' '.join(text.split())  # 规范化空白字符
        
        return text
    
    def get_embedding_dim(self) -> int:
        """获取向量维度"""
        return self.model.get_sentence_embedding_dimension()


class HuggingFaceEncoder(BaseTextEncoder):
    """基于HuggingFace Transformers的编码器"""
    
    def __init__(self, 
                 model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
                 device: Optional[str] = None,
                 max_length: int = 512):
        """
        初始化HuggingFace编码器
        
        Args:
            model_name: 模型名称
            device: 设备
            max_length: 最大序列长度
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.max_length = max_length
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Loaded HuggingFace model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """编码文本为向量"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        
        with torch.no_grad():
            for text in texts:
                try:
                    # 分词
                    inputs = self.tokenizer(
                        text,
                        padding=True,
                        truncation=True,
                        max_length=self.max_length,
                        return_tensors="pt"
                    )
                    
                    # 移动到设备
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    # 获取模型输出
                    outputs = self.model(**inputs)
                    
                    # 池化策略（平均池化）
                    embedding = self._mean_pooling(outputs, inputs['attention_mask'])
                    
                    # L2归一化
                    embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
                    
                    embeddings.append(embedding.cpu().numpy())
                    
                except Exception as e:
                    logger.error(f"Failed to encode text: {e}")
                    # 添加零向量
                    dim = self.model.config.hidden_size
                    embeddings.append(np.zeros((1, dim), dtype=np.float32))
        
        return np.vstack(embeddings)
    
    def _mean_pooling(self, model_output, attention_mask):
        """平均池化"""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def get_embedding_dim(self) -> int:
        """获取向量维度"""
        return self.model.config.hidden_size


class PaperTextEncoder:
    """
    论文文本编码器 - 专门为论文数据设计的编码系统
    支持多种编码策略和缓存机制
    """
    
    def __init__(self, 
                 encoder_type: str = 'sentence-transformer',
                 model_name: Optional[str] = None,
                 cache_dir: Optional[str] = None,
                 enable_cache: bool = True):
        """
        初始化论文文本编码器
        
        Args:
            encoder_type: 编码器类型 ('sentence-transformer' 或 'huggingface')
            model_name: 模型名称
            cache_dir: 缓存目录
            enable_cache: 是否启用缓存
        """
        self.encoder_type = encoder_type
        self.cache_dir = cache_dir or "outputs/cache/embeddings"
        self.enable_cache = enable_cache
        
        # 创建缓存目录
        if self.enable_cache:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化编码器
        if encoder_type == 'sentence-transformer':
            model_name = model_name or 'paraphrase-multilingual-MiniLM-L12-v2'
            self.encoder = SentenceTransformerEncoder(model_name, cache_dir=cache_dir)
        elif encoder_type == 'huggingface':
            model_name = model_name or 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
            self.encoder = HuggingFaceEncoder(model_name)
        else:
            raise ValueError(f"Unknown encoder type: {encoder_type}")
        
        logger.info(f"Initialized PaperTextEncoder with {encoder_type} encoder")
    
    def encode_paper_text(self, title: str, abstract: str) -> np.ndarray:
        """
        编码论文文本（标题+摘要）
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            
        Returns:
            np.ndarray: 文本向量表示
        """
        # 组合文本
        combined_text = self._combine_title_abstract(title, abstract)
        
        # 检查缓存
        if self.enable_cache:
            cache_key = self._get_cache_key(combined_text)
            cached_embedding = self._load_from_cache(cache_key)
            if cached_embedding is not None:
                return cached_embedding
        
        # 编码
        embedding = self.encoder.encode(combined_text)
        
        # 确保是二维数组
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # 保存到缓存
        if self.enable_cache:
            self._save_to_cache(cache_key, embedding[0])
        
        return embedding[0]  # 返回一维向量
    
    def encode_semantic_content(self, 
                               application_scenario: str,
                               task_type: str,
                               task_objectives: List[str]) -> np.ndarray:
        """
        编码语义内容（任务场景信息）
        
        Args:
            application_scenario: 应用场景
            task_type: 任务类型  
            task_objectives: 任务目标列表
            
        Returns:
            np.ndarray: 语义向量表示
        """
        # 组合语义信息
        semantic_text = self._combine_semantic_info(
            application_scenario, task_type, task_objectives
        )
        
        # 检查缓存
        if self.enable_cache:
            cache_key = self._get_cache_key(semantic_text, prefix="semantic")
            cached_embedding = self._load_from_cache(cache_key)
            if cached_embedding is not None:
                return cached_embedding
        
        # 编码
        embedding = self.encoder.encode(semantic_text)
        
        # 确保是二维数组
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # 保存到缓存
        if self.enable_cache:
            self._save_to_cache(cache_key, embedding[0])
        
        return embedding[0]  # 返回一维向量
    
    def encode_keywords(self, keywords: List[str]) -> np.ndarray:
        """
        编码关键词列表
        
        Args:
            keywords: 关键词列表
            
        Returns:
            np.ndarray: 关键词向量表示
        """
        if not keywords:
            # 返回零向量
            dim = self.encoder.get_embedding_dim()
            return np.zeros(dim, dtype=np.float32)
        
        # 组合关键词
        keywords_text = ' '.join(keywords[:20])  # 限制关键词数量
        
        # 编码
        embedding = self.encoder.encode(keywords_text)
        
        if embedding.ndim == 1:
            return embedding
        else:
            return embedding[0]
    
    def batch_encode_papers(self, papers_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        批量编码论文
        
        Args:
            papers_data: 论文数据列表，每个包含title, abstract等字段
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (文本向量矩阵, 语义向量矩阵)
        """
        logger.info(f"Batch encoding {len(papers_data)} papers...")
        
        text_embeddings = []
        semantic_embeddings = []
        
        # 准备文本数据
        text_list = []
        semantic_list = []
        
        for paper in papers_data:
            # 文本数据
            combined_text = self._combine_title_abstract(
                paper.get('title', ''), 
                paper.get('abstract', '')
            )
            text_list.append(combined_text)
            
            # 语义数据
            semantic_text = self._combine_semantic_info(
                paper.get('application_scenario', ''),
                paper.get('task_type', ''),
                paper.get('task_objectives', [])
            )
            semantic_list.append(semantic_text)
        
        # 批量编码文本
        try:
            text_embeddings = self.encoder.encode(text_list)
            if text_embeddings.ndim == 1:
                text_embeddings = text_embeddings.reshape(1, -1)
        except Exception as e:
            logger.error(f"Batch text encoding failed: {e}")
            dim = self.encoder.get_embedding_dim()
            text_embeddings = np.zeros((len(papers_data), dim), dtype=np.float32)
        
        # 批量编码语义
        try:
            semantic_embeddings = self.encoder.encode(semantic_list)
            if semantic_embeddings.ndim == 1:
                semantic_embeddings = semantic_embeddings.reshape(1, -1)
        except Exception as e:
            logger.error(f"Batch semantic encoding failed: {e}")
            dim = self.encoder.get_embedding_dim()
            semantic_embeddings = np.zeros((len(papers_data), dim), dtype=np.float32)
        
        logger.info(f"Batch encoding completed. Text shape: {text_embeddings.shape}, Semantic shape: {semantic_embeddings.shape}")
        
        return text_embeddings, semantic_embeddings
    
    def _combine_title_abstract(self, title: str, abstract: str) -> str:
        """组合标题和摘要"""
        components = []
        
        if title and title.strip():
            components.append(title.strip())
        
        if abstract and abstract.strip():
            components.append(abstract.strip())
        
        return ' '.join(components) if components else "empty paper"
    
    def _combine_semantic_info(self, 
                              application_scenario: str,
                              task_type: str, 
                              task_objectives: List[str]) -> str:
        """组合语义信息"""
        components = []
        
        if application_scenario and application_scenario.strip():
            components.append(f"Application: {application_scenario}")
        
        if task_type and task_type.strip():
            components.append(f"Task: {task_type}")
        
        if task_objectives:
            objectives_text = '; '.join(task_objectives[:3])  # 限制目标数量
            components.append(f"Objectives: {objectives_text}")
        
        return ' '.join(components) if components else "general research"
    
    def _get_cache_key(self, text: str, prefix: str = "text") -> str:
        """生成缓存键"""
        content = f"{prefix}_{text}".encode('utf-8')
        return f"{prefix}_{hashlib.md5(content).hexdigest()}"
    
    def _load_from_cache(self, cache_key: str) -> Optional[np.ndarray]:
        """从缓存加载向量"""
        cache_file = Path(self.cache_dir) / f"{cache_key}.npy"
        
        try:
            if cache_file.exists():
                return np.load(cache_file)
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, embedding: np.ndarray) -> None:
        """保存向量到缓存"""
        cache_file = Path(self.cache_dir) / f"{cache_key}.npy"
        
        try:
            np.save(cache_file, embedding)
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_key}: {e}")
    
    def get_embedding_dim(self) -> int:
        """获取向量维度"""
        return self.encoder.get_embedding_dim()
    
    def clear_cache(self) -> None:
        """清除缓存"""
        if self.enable_cache and Path(self.cache_dir).exists():
            for cache_file in Path(self.cache_dir).glob("*.npy"):
                cache_file.unlink()
            logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        if not self.enable_cache or not Path(self.cache_dir).exists():
            return {"total_files": 0, "total_size_mb": 0}
        
        cache_files = list(Path(self.cache_dir).glob("*.npy"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "total_files": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
        }