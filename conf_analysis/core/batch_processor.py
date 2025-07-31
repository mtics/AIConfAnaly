"""
批量处理器 - 提供完整的论文数据批量处理和Milvus存储接口
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Tuple, Any
import logging
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import os

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from services.paper_service import PaperService
from database.milvus_client import MilvusClientConfig
from analysis.data_processor import DataProcessor
from models.paper import Paper

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    批量处理器 - 处理会议论文数据并存储到Milvus
    """
    
    def __init__(self, 
                 milvus_host: str = "localhost",
                 milvus_port: str = "19530",
                 encoder_type: str = "sentence-transformer",
                 model_name: Optional[str] = None,
                 enable_cache: bool = True,
                 output_dir: str = "outputs"):
        """
        初始化批量处理器
        
        Args:
            milvus_host: Milvus服务器地址
            milvus_port: Milvus端口
            encoder_type: 编码器类型
            model_name: 模型名称
            enable_cache: 是否启用缓存
            output_dir: 输出目录
        """
        
        # 配置日志
        self._setup_logging()
        
        # 初始化Milvus配置
        self.milvus_config = MilvusClientConfig(
            host=milvus_host,
            port=milvus_port
        )
        
        # 初始化服务
        self.paper_service = PaperService(
            milvus_config=self.milvus_config,
            encoder_type=encoder_type,
            model_name=model_name,
            enable_cache=enable_cache
        )
        
        # 初始化数据处理器
        self.data_processor = DataProcessor()
        
        # 输出目录
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("BatchProcessor initialized successfully")
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('batch_processing.log', encoding='utf-8')
            ]
        )
    
    def process_from_raw_data(self, 
                            data_dir: str = "outputs/data/raw",
                            batch_size: int = 50,
                            conferences: Optional[List[str]] = None,
                            years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        从原始数据目录处理论文
        
        Args:
            data_dir: 原始数据目录
            batch_size: 批处理大小
            conferences: 要处理的会议列表
            years: 要处理的年份列表
            
        Returns:
            Dict: 处理结果统计
        """
        logger.info(f"Starting batch processing from {data_dir}")
        
        try:
            # 1. 加载原始数据
            df = self.data_processor.load_raw_data(data_dir)
            logger.info(f"Loaded {len(df)} papers from raw data")
            
            # 2. 过滤数据
            if conferences:
                df = df[df['conference'].isin(conferences)]
                logger.info(f"Filtered by conferences: {len(df)} papers remaining")
            
            if years:
                df = df[df['year'].isin(years)]
                logger.info(f"Filtered by years: {len(df)} papers remaining")
            
            # 3. 准备数据
            papers_data = self._prepare_papers_data(df)
            
            # 4. 批量处理
            processed_papers, stats = self.paper_service.batch_process_papers(
                papers_data=papers_data,
                batch_size=batch_size,
                analyze_all=True,
                store_all=True
            )
            
            # 5. 保存处理结果
            self._save_processing_results(processed_papers, stats)
            
            logger.info("Batch processing completed successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise
    
    def process_from_csv(self, 
                        csv_path: str,
                        batch_size: int = 50,
                        title_col: str = "title",
                        abstract_col: str = "abstract",
                        conference_col: str = "conference",
                        year_col: str = "year",
                        url_col: Optional[str] = None,
                        pdf_url_col: Optional[str] = None) -> Dict[str, Any]:
        """
        从CSV文件处理论文
        
        Args:
            csv_path: CSV文件路径
            batch_size: 批处理大小
            title_col: 标题列名
            abstract_col: 摘要列名
            conference_col: 会议列名
            year_col: 年份列名
            url_col: URL列名
            pdf_url_col: PDF URL列名
            
        Returns:
            Dict: 处理结果统计
        """
        logger.info(f"Processing papers from CSV: {csv_path}")
        
        try:
            # 读取CSV
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"Loaded {len(df)} papers from CSV")
            
            # 准备数据
            papers_data = []
            for _, row in df.iterrows():
                paper_data = {
                    'title': str(row.get(title_col, '')),
                    'abstract': str(row.get(abstract_col, '')),
                    'conference': str(row.get(conference_col, '')),
                    'year': int(row.get(year_col, 0)),
                    'url': str(row.get(url_col, '')) if url_col else None,
                    'pdf_url': str(row.get(pdf_url_col, '')) if pdf_url_col else None,
                }
                papers_data.append(paper_data)
            
            # 批量处理
            processed_papers, stats = self.paper_service.batch_process_papers(
                papers_data=papers_data,
                batch_size=batch_size,
                analyze_all=True,
                store_all=True
            )
            
            # 保存结果
            self._save_processing_results(processed_papers, stats)
            
            logger.info("CSV processing completed successfully")
            return stats
            
        except Exception as e:
            logger.error(f"CSV processing failed: {e}")
            raise
    
    def process_single_paper(self, 
                           title: str,
                           abstract: str,
                           conference: str,
                           year: int,
                           url: Optional[str] = None,
                           pdf_url: Optional[str] = None) -> Optional[Paper]:
        """
        处理单篇论文
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            conference: 会议名称
            year: 发表年份
            url: 论文链接
            pdf_url: PDF链接
            
        Returns:
            Optional[Paper]: 处理后的Paper对象
        """
        logger.info(f"Processing single paper: {title[:50]}...")
        
        return self.paper_service.process_and_store_paper(
            title=title,
            abstract=abstract,
            conference=conference,
            year=year,
            url=url,
            pdf_url=pdf_url
        )
    
    def _prepare_papers_data(self, df: pd.DataFrame) -> List[Dict]:
        """准备论文数据"""
        papers_data = []
        
        for _, row in df.iterrows():
            paper_data = {
                'title': str(row.get('title', '')),
                'abstract': str(row.get('abstract', '')),
                'conference': str(row.get('conference', '')),
                'year': int(row.get('year', 0)),
                'url': str(row.get('url', '')) if pd.notna(row.get('url')) else None,
                'pdf_url': str(row.get('pdf_url', '')) if pd.notna(row.get('pdf_url')) else None,
            }
            papers_data.append(paper_data)
        
        return papers_data
    
    def _save_processing_results(self, processed_papers: List[Paper], stats: Dict):
        """保存处理结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存统计信息
        stats_file = self.output_dir / f"processing_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存论文摘要信息
        papers_summary = []
        for paper in processed_papers:
            summary = {
                'paper_id': paper.paper_id,
                'title': paper.title,
                'conference': paper.conference,
                'year': paper.year,
                'application_scenario': paper.task_scenario_analysis.application_scenario if paper.task_scenario_analysis else '',
                'task_type': paper.task_scenario_analysis.task_type if paper.task_scenario_analysis else '',
                'has_vectors': paper.text_embedding is not None
            }
            papers_summary.append(summary)
        
        summary_file = self.output_dir / f"papers_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(papers_summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Processing results saved to {self.output_dir}")


class QueryInterface:
    """
    查询接口 - 提供论文搜索和查询功能
    """
    
    def __init__(self, 
                 milvus_host: str = "localhost",
                 milvus_port: str = "19530",
                 encoder_type: str = "sentence-transformer"):
        """
        初始化查询接口
        
        Args:
            milvus_host: Milvus服务器地址
            milvus_port: Milvus端口
            encoder_type: 编码器类型
        """
        
        # 配置Milvus
        self.milvus_config = MilvusClientConfig(
            host=milvus_host,
            port=milvus_port
        )
        
        # 初始化服务
        self.paper_service = PaperService(
            milvus_config=self.milvus_config,
            encoder_type=encoder_type
        )
        
        logger.info("QueryInterface initialized successfully")
    
    def search_papers(self, 
                     query: str,
                     search_type: str = "hybrid",
                     top_k: int = 10,
                     conferences: Optional[List[str]] = None,
                     years: Optional[List[int]] = None,
                     scenarios: Optional[List[str]] = None,
                     min_confidence: Optional[float] = None) -> List[Dict]:
        """
        搜索论文
        
        Args:
            query: 搜索查询
            search_type: 搜索类型 ('text', 'semantic', 'hybrid')
            top_k: 返回结果数量
            conferences: 会议过滤
            years: 年份过滤
            scenarios: 应用场景过滤
            min_confidence: 最小置信度
            
        Returns:
            List[Dict]: 搜索结果
        """
        
        # 构建过滤条件
        filters = {}
        
        if conferences:
            filters['conference'] = conferences
        
        if years:
            if len(years) == 1:
                filters['year'] = years[0]
            else:
                filters['year_range'] = [min(years), max(years)]
        
        if scenarios:
            # 如果只有一个场景，使用精确匹配
            if len(scenarios) == 1:
                filters['application_scenario'] = scenarios[0]
        
        if min_confidence:
            filters['min_confidence'] = min_confidence
        
        # 执行搜索
        results = self.paper_service.search_papers(
            query=query,
            search_type=search_type,
            top_k=top_k,
            filters=filters
        )
        
        return results
    
    def get_similar_papers(self, 
                          paper_id: str,
                          top_k: int = 10,
                          vector_field: str = "text_vector") -> List[Dict]:
        """
        获取相似论文
        
        Args:
            paper_id: 论文ID
            top_k: 返回结果数量
            vector_field: 向量字段
            
        Returns:
            List[Dict]: 相似论文列表
        """
        
        if not self.paper_service.milvus_client:
            logger.error("Milvus client not available")
            return []
        
        try:
            # 首先获取目标论文的向量
            target_paper = self.paper_service.milvus_client.filter_papers(
                filters={'paper_id': paper_id},
                limit=1
            )
            
            if not target_paper:
                logger.error(f"Paper {paper_id} not found")
                return []
            
            # 获取向量（这里需要实现向量提取逻辑）
            # 简化实现：使用文本重新编码
            paper_data = target_paper[0]
            query_text = f"{paper_data.get('title', '')} {paper_data.get('abstract', '')}"
            
            # 搜索相似论文
            results = self.paper_service.search_papers(
                query=query_text,
                search_type='text',
                top_k=top_k + 1  # +1 因为会包含自己
            )
            
            # 过滤掉自己
            filtered_results = [r for r in results if r.get('paper_id') != paper_id]
            
            return filtered_results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to get similar papers: {e}")
            return []
    
    def get_papers_by_filters(self, 
                            filters: Dict[str, Any],
                            limit: int = 100,
                            sort_by: str = "year",
                            ascending: bool = False) -> List[Dict]:
        """
        根据过滤条件获取论文
        
        Args:
            filters: 过滤条件
            limit: 结果限制
            sort_by: 排序字段
            ascending: 是否升序
            
        Returns:
            List[Dict]: 论文列表
        """
        
        if not self.paper_service.milvus_client:
            logger.error("Milvus client not available")
            return []
        
        try:
            results = self.paper_service.milvus_client.filter_papers(
                filters=filters,
                limit=limit
            )
            
            # 排序
            if sort_by in ['year', 'practical_value_score', 'scenario_confidence']:
                results.sort(
                    key=lambda x: x.get(sort_by, 0),
                    reverse=not ascending
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get papers by filters: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        return self.paper_service.get_service_stats()
    
    def export_search_results(self, 
                            query: str,
                            output_path: str,
                            search_type: str = "hybrid",
                            top_k: int = 100,
                            format: str = "json") -> bool:
        """
        导出搜索结果
        
        Args:
            query: 搜索查询
            output_path: 输出路径
            search_type: 搜索类型
            top_k: 结果数量
            format: 导出格式
            
        Returns:
            bool: 是否成功
        """
        
        try:
            # 执行搜索
            results = self.search_papers(
                query=query,
                search_type=search_type,
                top_k=top_k
            )
            
            # 导出结果
            if format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            elif format == "csv":
                df = pd.DataFrame(results)
                df.to_csv(output_path, index=False, encoding='utf-8')
            
            else:
                logger.error(f"Unknown format: {format}")
                return False
            
            logger.info(f"Exported {len(results)} search results to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(description="批量处理和查询会议论文")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 批量处理命令
    process_parser = subparsers.add_parser('process', help='批量处理论文')
    process_parser.add_argument('--data-dir', default='outputs/data/raw', help='原始数据目录')
    process_parser.add_argument('--csv-path', help='CSV文件路径')
    process_parser.add_argument('--batch-size', type=int, default=50, help='批处理大小')
    process_parser.add_argument('--conferences', nargs='+', help='要处理的会议')
    process_parser.add_argument('--years', type=int, nargs='+', help='要处理的年份')
    process_parser.add_argument('--milvus-host', default='localhost', help='Milvus服务器地址')
    process_parser.add_argument('--milvus-port', default='19530', help='Milvus端口')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索论文')
    search_parser.add_argument('query', help='搜索查询')
    search_parser.add_argument('--type', choices=['text', 'semantic', 'hybrid'], default='hybrid', help='搜索类型')
    search_parser.add_argument('--top-k', type=int, default=10, help='返回结果数量')
    search_parser.add_argument('--conferences', nargs='+', help='会议过滤')
    search_parser.add_argument('--years', type=int, nargs='+', help='年份过滤')
    search_parser.add_argument('--output', help='输出文件路径')
    search_parser.add_argument('--milvus-host', default='localhost', help='Milvus服务器地址')
    search_parser.add_argument('--milvus-port', default='19530', help='Milvus端口')
    
    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='获取统计信息')
    stats_parser.add_argument('--milvus-host', default='localhost', help='Milvus服务器地址')
    stats_parser.add_argument('--milvus-port', default='19530', help='Milvus端口')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        # 批量处理
        processor = BatchProcessor(
            milvus_host=args.milvus_host,
            milvus_port=args.milvus_port
        )
        
        if args.csv_path:
            # 从CSV处理
            stats = processor.process_from_csv(
                csv_path=args.csv_path,
                batch_size=args.batch_size
            )
        else:
            # 从原始数据处理
            stats = processor.process_from_raw_data(
                data_dir=args.data_dir,
                batch_size=args.batch_size,
                conferences=args.conferences,
                years=args.years
            )
        
        print("处理完成！")
        print(f"总计: {stats['total_papers']} 篇论文")
        print(f"成功处理: {stats['processed_papers']} 篇")
        print(f"成功存储: {stats['inserted_papers']} 篇")
        print(f"失败: {stats['failed_papers']} 篇")
        print(f"处理时间: {stats['processing_time']:.2f} 秒")
    
    elif args.command == 'search':
        # 搜索论文
        query_interface = QueryInterface(
            milvus_host=args.milvus_host,
            milvus_port=args.milvus_port
        )
        
        results = query_interface.search_papers(
            query=args.query,
            search_type=args.type,
            top_k=args.top_k,
            conferences=args.conferences,
            years=args.years
        )
        
        print(f"找到 {len(results)} 篇相关论文：")
        for i, paper in enumerate(results, 1):
            print(f"\n{i}. {paper.get('title', 'No title')}")
            print(f"   会议: {paper.get('conference', 'Unknown')} ({paper.get('year', 'Unknown')})")
            print(f"   应用场景: {paper.get('application_scenario', 'Unknown')}")
            print(f"   任务类型: {paper.get('task_type', 'Unknown')}")
            print(f"   相似度: {paper.get('score', 0):.3f}")
        
        # 导出结果
        if args.output:
            query_interface.export_search_results(
                query=args.query,
                output_path=args.output,
                search_type=args.type,
                top_k=args.top_k
            )
            print(f"\n结果已导出到: {args.output}")
    
    elif args.command == 'stats':
        # 获取统计信息
        query_interface = QueryInterface(
            milvus_host=args.milvus_host,
            milvus_port=args.milvus_port
        )
        
        stats = query_interface.get_statistics()
        
        print("数据库统计信息：")
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()