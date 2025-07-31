"""
论文服务 - 集成Paper类、任务场景分析、向量编码和数据库存储的完整服务
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Tuple, Any
import logging
from datetime import datetime
import json
from pathlib import Path

from ..models.paper import Paper, TaskScenarioAnalysis, PaperMetrics, ConferenceInfo
from ..analysis.task_scenario_analyzer import TaskScenarioAnalyzer
from ..analysis.deep_insight_generator import DeepInsightGenerator
from ..embeddings.text_encoder import PaperTextEncoder
from ..database.milvus_client import MilvusClient, MilvusClientConfig

logger = logging.getLogger(__name__)


class PaperService:
    """
    论文服务类 - 提供完整的论文数据处理、分析和存储功能
    """
    
    def __init__(self, 
                 milvus_config: Optional[MilvusClientConfig] = None,
                 encoder_type: str = 'sentence-transformer',
                 model_name: Optional[str] = None,
                 vector_dim: int = 768,
                 enable_cache: bool = True):
        """
        初始化论文服务
        
        Args:
            milvus_config: Milvus配置
            encoder_type: 编码器类型
            model_name: 模型名称
            vector_dim: 向量维度
            enable_cache: 是否启用缓存
        """
        self.vector_dim = vector_dim
        
        # 初始化组件
        self.task_analyzer = TaskScenarioAnalyzer()
        self.insight_generator = DeepInsightGenerator()
        self.text_encoder = PaperTextEncoder(
            encoder_type=encoder_type,
            model_name=model_name,
            enable_cache=enable_cache
        )
        
        # 初始化Milvus客户端
        try:
            self.milvus_client = MilvusClient(
                config=milvus_config,
                vector_dim=vector_dim
            )
            logger.info("Milvus client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Milvus client: {e}")
            self.milvus_client = None
        
        # 统计信息
        self.stats = {
            'processed_papers': 0,
            'inserted_papers': 0,
            'failed_papers': 0,
            'last_processing_time': None
        }
    
    def create_paper_from_data(self, 
                              title: str,
                              abstract: str,
                              conference: str,
                              year: int,
                              url: Optional[str] = None,
                              pdf_url: Optional[str] = None,
                              additional_data: Optional[Dict] = None) -> Paper:
        """
        从原始数据创建Paper对象
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            conference: 会议名称
            year: 发表年份
            url: 论文链接
            pdf_url: PDF链接
            additional_data: 额外数据
            
        Returns:
            Paper: 创建的Paper对象
        """
        paper = Paper(
            title=title,
            abstract=abstract,
            conference=conference,
            year=year,
            url=url,
            pdf_url=pdf_url
        )
        
        # 添加额外信息
        if additional_data:
            if 'authors' in additional_data:
                # 处理作者信息
                pass
            
            if 'keywords' in additional_data:
                paper.keywords = additional_data['keywords']
            
            if 'tags' in additional_data:
                paper.add_tags(additional_data['tags'])
        
        return paper
    
    def analyze_paper(self, paper: Paper, 
                     generate_insights: bool = True,
                     encode_vectors: bool = True) -> Paper:
        """
        对论文进行完整分析
        
        Args:
            paper: Paper对象
            generate_insights: 是否生成深层次洞察
            encode_vectors: 是否编码向量
            
        Returns:
            Paper: 分析后的Paper对象
        """
        logger.info(f"Analyzing paper: {paper.paper_id}")
        
        try:
            # 1. 任务场景分析
            df = pd.DataFrame([{
                'title': paper.title,
                'abstract': paper.abstract,
                'conference': paper.conference,
                'year': paper.year
            }])
            
            analyzed_df = self.task_analyzer.analyze_paper_task_scenario(df)
            
            if len(analyzed_df) > 0:
                row = analyzed_df.iloc[0]
                
                # 创建任务场景分析结果
                task_analysis = TaskScenarioAnalysis(
                    application_scenario=row.get('application_scenario', ''),
                    scenario_confidence=float(row.get('scenario_confidence', 0.0)),
                    task_type=row.get('task_type', ''),
                    task_confidence=float(row.get('task_confidence', 0.0)),
                    task_objectives=row.get('task_objectives', '').split(';') if row.get('task_objectives') else [],
                    scenario_keywords=row.get('scenario_keywords', '').split(', ') if row.get('scenario_keywords') else [],
                    task_keywords=row.get('task_keywords', '').split(', ') if row.get('task_keywords') else []
                )
                
                paper.add_task_scenario_analysis(task_analysis)
                logger.info(f"Task scenario analysis completed for {paper.paper_id}")
            
            # 2. 向量编码
            if encode_vectors and self.text_encoder:
                try:
                    # 编码文本向量
                    text_vector = self.text_encoder.encode_paper_text(
                        paper.title, paper.abstract
                    )
                    paper.add_text_embedding(text_vector, 'text')
                    
                    # 编码语义向量
                    if paper.task_scenario_analysis:
                        semantic_vector = self.text_encoder.encode_semantic_content(
                            paper.task_scenario_analysis.application_scenario,
                            paper.task_scenario_analysis.task_type,
                            paper.task_scenario_analysis.task_objectives
                        )
                        paper.add_text_embedding(semantic_vector, 'semantic')
                    
                    logger.info(f"Vector encoding completed for {paper.paper_id}")
                    
                except Exception as e:
                    logger.error(f"Vector encoding failed for {paper.paper_id}: {e}")
            
            # 3. 更新指标
            metrics = PaperMetrics(
                title_length=len(paper.title) if paper.title else 0,
                abstract_length=len(paper.abstract) if paper.abstract else 0,
                abstract_word_count=len(paper.abstract.split()) if paper.abstract else 0,
                keyword_count=len(paper.keywords)
            )
            paper.update_metrics(metrics)
            
            # 4. 生成深层次洞察（可选）
            if generate_insights:
                try:
                    insights = self.insight_generator.generate_comprehensive_research_report(analyzed_df)
                    paper.add_insight_data(insights)
                    logger.info(f"Deep insights generated for {paper.paper_id}")
                except Exception as e:
                    logger.warning(f"Failed to generate insights for {paper.paper_id}: {e}")
            
            self.stats['processed_papers'] += 1
            logger.info(f"Paper analysis completed: {paper.paper_id}")
            
        except Exception as e:
            logger.error(f"Failed to analyze paper {paper.paper_id}: {e}")
            self.stats['failed_papers'] += 1
        
        return paper
    
    def store_paper(self, paper: Paper) -> bool:
        """
        存储论文到数据库
        
        Args:
            paper: Paper对象
            
        Returns:
            bool: 是否存储成功
        """
        if not self.milvus_client:
            logger.error("Milvus client not available")
            return False
        
        try:
            success = self.milvus_client.insert_paper(paper)
            if success:
                self.stats['inserted_papers'] += 1
                logger.info(f"Paper stored successfully: {paper.paper_id}")
            else:
                self.stats['failed_papers'] += 1
                logger.error(f"Failed to store paper: {paper.paper_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing paper {paper.paper_id}: {e}")
            self.stats['failed_papers'] += 1
            return False
    
    def process_and_store_paper(self, 
                               title: str,
                               abstract: str,
                               conference: str,
                               year: int,
                               url: Optional[str] = None,
                               pdf_url: Optional[str] = None,
                               additional_data: Optional[Dict] = None) -> Optional[Paper]:
        """
        处理并存储单篇论文（完整流程）
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            conference: 会议名称
            year: 发表年份
            url: 论文链接
            pdf_url: PDF链接
            additional_data: 额外数据
            
        Returns:
            Optional[Paper]: 处理后的Paper对象，失败时返回None
        """
        try:
            # 1. 创建Paper对象
            paper = self.create_paper_from_data(
                title=title,
                abstract=abstract,
                conference=conference,
                year=year,
                url=url,
                pdf_url=pdf_url,
                additional_data=additional_data
            )
            
            # 2. 分析论文
            paper = self.analyze_paper(paper)
            
            # 3. 存储到数据库
            if self.store_paper(paper):
                return paper
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to process and store paper '{title}': {e}")
            return None
    
    def batch_process_papers(self, 
                           papers_data: List[Dict],
                           batch_size: int = 50,
                           analyze_all: bool = True,
                           store_all: bool = True) -> Tuple[List[Paper], Dict]:
        """
        批量处理论文
        
        Args:
            papers_data: 论文数据列表
            batch_size: 批次大小
            analyze_all: 是否分析所有论文
            store_all: 是否存储所有论文
            
        Returns:
            Tuple[List[Paper], Dict]: (处理后的Paper列表, 统计信息)
        """
        start_time = datetime.now()
        processed_papers = []
        
        logger.info(f"Starting batch processing of {len(papers_data)} papers...")
        
        # 重置统计
        batch_stats = {
            'total_papers': len(papers_data),
            'processed_papers': 0,
            'inserted_papers': 0,
            'failed_papers': 0,
            'processing_time': None
        }
        
        # 分批处理
        for i in range(0, len(papers_data), batch_size):
            batch_data = papers_data[i:i + batch_size]
            batch_papers = []
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(papers_data)-1)//batch_size + 1}...")
            
            # 1. 创建Paper对象
            for paper_data in batch_data:
                try:
                    paper = self.create_paper_from_data(
                        title=paper_data.get('title', ''),
                        abstract=paper_data.get('abstract', ''),
                        conference=paper_data.get('conference', ''),
                        year=paper_data.get('year', 0),
                        url=paper_data.get('url'),
                        pdf_url=paper_data.get('pdf_url'),
                        additional_data=paper_data.get('additional_data')
                    )
                    batch_papers.append(paper)
                    
                except Exception as e:
                    logger.error(f"Failed to create paper from data: {e}")
                    batch_stats['failed_papers'] += 1
            
            # 2. 批量分析
            if analyze_all and batch_papers:
                try:
                    analyzed_papers = self._batch_analyze_papers(batch_papers)
                    batch_papers = analyzed_papers
                    batch_stats['processed_papers'] += len(analyzed_papers)
                    
                except Exception as e:
                    logger.error(f"Batch analysis failed: {e}")
            
            # 3. 批量存储
            if store_all and batch_papers and self.milvus_client:
                try:
                    success_count, total_count = self.milvus_client.batch_insert_papers(batch_papers)
                    batch_stats['inserted_papers'] += success_count
                    batch_stats['failed_papers'] += (total_count - success_count)
                    
                except Exception as e:
                    logger.error(f"Batch storage failed: {e}")
                    batch_stats['failed_papers'] += len(batch_papers)
            
            processed_papers.extend(batch_papers)
        
        # 计算处理时间
        end_time = datetime.now()
        batch_stats['processing_time'] = (end_time - start_time).total_seconds()
        self.stats['last_processing_time'] = end_time
        
        logger.info(f"Batch processing completed in {batch_stats['processing_time']:.2f} seconds")
        logger.info(f"Results: {batch_stats['processed_papers']} processed, {batch_stats['inserted_papers']} stored, {batch_stats['failed_papers']} failed")
        
        return processed_papers, batch_stats
    
    def _batch_analyze_papers(self, papers: List[Paper]) -> List[Paper]:
        """批量分析论文"""
        logger.info(f"Batch analyzing {len(papers)} papers...")
        
        try:
            # 准备数据框
            papers_data = []
            for paper in papers:
                papers_data.append({
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'conference': paper.conference,
                    'year': paper.year
                })
            
            df = pd.DataFrame(papers_data)
            
            # 任务场景分析
            analyzed_df = self.task_analyzer.analyze_paper_task_scenario(df)
            
            # 批量向量编码
            if self.text_encoder:
                text_embeddings, semantic_embeddings = self.text_encoder.batch_encode_papers(papers_data)
            else:
                text_embeddings = None
                semantic_embeddings = None
            
            # 更新Paper对象
            for i, paper in enumerate(papers):
                try:
                    # 添加任务场景分析结果
                    if i < len(analyzed_df):
                        row = analyzed_df.iloc[i]
                        task_analysis = TaskScenarioAnalysis(
                            application_scenario=row.get('application_scenario', ''),
                            scenario_confidence=float(row.get('scenario_confidence', 0.0)),
                            task_type=row.get('task_type', ''),
                            task_confidence=float(row.get('task_confidence', 0.0)),
                            task_objectives=row.get('task_objectives', '').split(';') if row.get('task_objectives') else [],
                            scenario_keywords=row.get('scenario_keywords', '').split(', ') if row.get('scenario_keywords') else [],
                            task_keywords=row.get('task_keywords', '').split(', ') if row.get('task_keywords') else []
                        )
                        paper.add_task_scenario_analysis(task_analysis)
                    
                    # 添加向量表示
                    if text_embeddings is not None and i < len(text_embeddings):
                        paper.add_text_embedding(text_embeddings[i], 'text')
                    
                    if semantic_embeddings is not None and i < len(semantic_embeddings):
                        paper.add_text_embedding(semantic_embeddings[i], 'semantic')
                    
                    # 更新指标
                    metrics = PaperMetrics(
                        title_length=len(paper.title) if paper.title else 0,
                        abstract_length=len(paper.abstract) if paper.abstract else 0,
                        abstract_word_count=len(paper.abstract.split()) if paper.abstract else 0,
                        keyword_count=len(paper.keywords)
                    )
                    paper.update_metrics(metrics)
                    
                except Exception as e:
                    logger.error(f"Failed to update paper {paper.paper_id}: {e}")
            
            return papers
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return papers
    
    def search_papers(self, 
                     query: str,
                     search_type: str = 'hybrid',
                     top_k: int = 10,
                     filters: Optional[Dict] = None) -> List[Dict]:
        """
        搜索论文
        
        Args:
            query: 查询文本
            search_type: 搜索类型 ('text', 'semantic', 'hybrid')
            top_k: 返回结果数量
            filters: 过滤条件
            
        Returns:
            List[Dict]: 搜索结果
        """
        if not self.milvus_client:
            logger.error("Milvus client not available")
            return []
        
        try:
            if search_type == 'text':
                return self.milvus_client.search_by_text(
                    query_text=query,
                    text_encoder=self.text_encoder,
                    top_k=top_k,
                    filters=self._build_filter_string(filters) if filters else None
                )
            
            elif search_type == 'hybrid':
                # 解析查询中的语义信息
                semantic_query = self._extract_semantic_query(query)
                
                return self.milvus_client.hybrid_search(
                    text_query=query,
                    semantic_query=semantic_query,
                    text_encoder=self.text_encoder,
                    top_k=top_k
                )
            
            else:
                logger.error(f"Unknown search type: {search_type}")
                return []
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _extract_semantic_query(self, query: str) -> Dict[str, str]:
        """从查询中提取语义信息"""
        # 简单的语义提取逻辑
        semantic_query = {'scenario': '', 'task': ''}
        
        # 检测应用场景关键词
        scenario_keywords = {
            'medical': 'Medical Diagnosis',
            'healthcare': 'Medical Diagnosis',
            'driving': 'Autonomous Driving',
            'vehicle': 'Autonomous Driving',
            'financial': 'Financial Technology',
            'finance': 'Financial Technology',
            'city': 'Smart City',
            'urban': 'Smart City'
        }
        
        query_lower = query.lower()
        for keyword, scenario in scenario_keywords.items():
            if keyword in query_lower:
                semantic_query['scenario'] = scenario
                break
        
        # 检测任务类型关键词
        task_keywords = {
            'predict': 'Prediction Tasks',
            'classify': 'Classification Tasks',
            'generate': 'Generation Tasks',
            'optimize': 'Optimization Tasks'
        }
        
        for keyword, task in task_keywords.items():
            if keyword in query_lower:
                semantic_query['task'] = task
                break
        
        return semantic_query
    
    def _build_filter_string(self, filters: Dict) -> str:
        """构建过滤字符串"""
        if not self.milvus_client:
            return ""
        
        return self.milvus_client._build_filter_expression(filters)
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        stats = self.stats.copy()
        
        # 添加数据库统计
        if self.milvus_client:
            try:
                db_info = self.milvus_client.get_collection_info()
                stats['database_info'] = db_info
            except Exception as e:
                stats['database_error'] = str(e)
        
        # 添加编码器统计
        if self.text_encoder:
            stats['encoder_info'] = {
                'type': self.text_encoder.encoder_type,
                'dimension': self.text_encoder.get_embedding_dim(),
                'cache_stats': self.text_encoder.get_cache_stats()
            }
        
        return stats
    
    def export_papers(self, 
                     output_path: str,
                     filters: Optional[Dict] = None,
                     format: str = 'json') -> bool:
        """
        导出论文数据
        
        Args:
            output_path: 输出路径
            filters: 过滤条件
            format: 导出格式 ('json', 'csv')
            
        Returns:
            bool: 是否导出成功
        """
        if not self.milvus_client:
            logger.error("Milvus client not available")
            return False
        
        try:
            # 查询数据
            papers_data = self.milvus_client.filter_papers(filters or {})
            
            # 导出数据
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(papers_data, f, ensure_ascii=False, indent=2)
            
            elif format == 'csv':
                df = pd.DataFrame(papers_data)
                df.to_csv(output_path, index=False, encoding='utf-8')
            
            else:
                logger.error(f"Unknown format: {format}")
                return False
            
            logger.info(f"Exported {len(papers_data)} papers to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """清理资源"""
        if self.milvus_client:
            self.milvus_client.disconnect()
        
        if self.text_encoder:
            # 可选：清理缓存
            # self.text_encoder.clear_cache()
            pass
        
        logger.info("PaperService cleanup completed")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()