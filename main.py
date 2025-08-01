#!/usr/bin/env python3
"""
AI会议论文分析系统 - 完整集成主入口
端到端工作流：论文爬取 → PDF下载 → 向量编码 → Milvus存储 → 分析报告
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json
from datetime import datetime

# 确保正确的导入路径
sys.path.insert(0, str(Path(__file__).parent))

# 核心组件导入
from conf_analysis.core.analyzer import UnifiedAnalyzer
from conf_analysis.core.scrapers.base_scraper import BaseScraper
from conf_analysis.core.scrapers.aaai_scraper import AAAIScraper
from conf_analysis.core.scrapers.iclr_scraper import ICLRScraper
from conf_analysis.core.scrapers.icml_scraper import ICMLScraper
from conf_analysis.core.scrapers.ijcai_scraper import IJCAIScraper
from conf_analysis.core.scrapers.neurips_scraper import NeuRIPSScraper
from conf_analysis.core.utils.pdf_manager import PDFDownloader, PDFManager
from conf_analysis.core.embeddings.text_encoder import PaperTextEncoder
from conf_analysis.core.database.milvus_client import MilvusClient, MilvusClientConfig
from conf_analysis.core.database.simple_vector_store import SimpleVectorStore
from conf_analysis.core.models.paper import Paper
from conf_analysis.core.utils.config import CONFERENCES

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedPaperAnalysisSystem:
    """集成论文分析系统 - 完整的端到端工作流"""
    
    def __init__(self, 
                 conferences: Optional[List[str]] = None,
                 years: Optional[List[int]] = None,
                 enable_milvus: bool = True,
                 enable_pdf_download: bool = True):
        """
        初始化集成分析系统
        
        Args:
            conferences: 要处理的会议列表 ['AAAI', 'ICLR', 'ICML', 'IJCAI', 'NeuRIPS']
            years: 要处理的年份列表 [2018, 2019, ..., 2024]
            enable_milvus: 是否启用Milvus向量数据库
            enable_pdf_download: 是否启用PDF下载
        """
        # 使用config.py中的会议和年份配置
        if conferences is None:
            self.conferences = list(CONFERENCES.keys())
        else:
            self.conferences = conferences
        
        if years is None:
            # 从所有会议中获取年份范围的并集
            all_years = set()
            for conf_config in CONFERENCES.values():
                all_years.update(conf_config.get('years', []))
            self.years = sorted(list(all_years))
        else:
            self.years = years
        self.enable_milvus = enable_milvus
        self.enable_pdf_download = enable_pdf_download
        
        # 初始化组件
        self.scrapers = self._initialize_scrapers()
        self.analyzer = UnifiedAnalyzer()
        self.pdf_manager = PDFManager() if enable_pdf_download else None
        self.text_encoder = PaperTextEncoder() if enable_milvus else None
        self.milvus_client = None
        self.simple_vector_store = None
        
        # 状态跟踪
        self.progress = {
            'scraping': {'completed': 0, 'total': 0, 'status': 'pending'},
            'pdf_download': {'completed': 0, 'total': 0, 'status': 'pending'},
            'vector_encoding': {'completed': 0, 'total': 0, 'status': 'pending'},
            'milvus_storage': {'completed': 0, 'total': 0, 'status': 'pending'},
            'analysis': {'status': 'pending'}
        }
        
        logger.info(f"Initialized system for conferences: {self.conferences}, years: {self.years}")
    
    def _initialize_scrapers(self) -> Dict[str, BaseScraper]:
        """初始化爬虫"""
        scrapers = {}
        
        scraper_classes = {
            'AAAI': AAAIScraper,
            'ICLR': ICLRScraper,
            'ICML': ICMLScraper,
            'IJCAI': IJCAIScraper,
            'NeuRIPS': NeuRIPSScraper
        }
        
        for conf in self.conferences:
            if conf in scraper_classes:
                try:
                    scrapers[conf] = scraper_classes[conf]()
                    logger.info(f"Initialized {conf} scraper")
                except Exception as e:
                    logger.error(f"Failed to initialize {conf} scraper: {e}")
            else:
                logger.warning(f"Unknown conference: {conf}")
        
        return scrapers
    
    def _initialize_milvus(self) -> bool:
        """初始化Milvus客户端，失败时回退到本地向量存储"""
        if not self.enable_milvus:
            return False
        
        # 获取向量维度
        vector_dim = self.text_encoder.get_embedding_dim() if self.text_encoder else 768
        
        # 首先尝试Milvus
        try:
            config = MilvusClientConfig.from_env()
            self.milvus_client = MilvusClient(config, vector_dim)
            logger.info(f"✅ Initialized Milvus client with vector dimension: {vector_dim}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Milvus client: {e}")
            logger.info("🔄 Falling back to local vector store...")
            
            # 回退到简单向量存储
            try:
                self.simple_vector_store = SimpleVectorStore(vector_dim=vector_dim)
                if self.simple_vector_store.connect():
                    logger.info(f"✅ Initialized simple vector store with vector dimension: {vector_dim}")
                    return True
                else:
                    logger.error("❌ Failed to initialize simple vector store")
                    self.enable_milvus = False
                    return False
                    
            except Exception as e2:
                logger.error(f"❌ Failed to initialize simple vector store: {e2}")
                logger.warning("⚠️ Continuing without vector storage...")
                self.enable_milvus = False
                return False
    
    async def scrape_papers(self) -> Dict[str, int]:
        """爬取论文元数据"""
        print("\n🕷️ 开始爬取论文元数据...")
        self.progress['scraping']['status'] = 'running'
        
        total_papers = 0
        results = {}
        
        # 计算总任务数
        self.progress['scraping']['total'] = len(self.conferences) * len(self.years)
        
        for conf in self.conferences:
            if conf not in self.scrapers:
                logger.warning(f"Scraper for {conf} not available")
                continue
            
            scraper = self.scrapers[conf]
            conf_results = {}
            
            for year in self.years:
                try:
                    print(f"  📋 爬取 {conf} {year}...")
                    
                    # 检查是否已存在数据文件
                    json_file = Path(f"outputs/data/raw/{conf}_{year}.json")
                    if json_file.exists():
                        with open(json_file, 'r', encoding='utf-8') as f:
                            papers = json.load(f)
                        print(f"    ✅ 使用已存在数据: {len(papers)} 篇论文")
                    else:
                        # 爬取新数据
                        papers = scraper.get_papers_for_year(year)
                        
                        # 保存数据
                        json_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(papers, f, ensure_ascii=False, indent=2)
                        
                        print(f"    ✅ 爬取完成: {len(papers)} 篇论文")
                    
                    conf_results[year] = len(papers)
                    total_papers += len(papers)
                    
                    # 更新进度
                    self.progress['scraping']['completed'] += 1
                    self._print_progress('scraping')
                    
                except Exception as e:
                    logger.error(f"Failed to scrape {conf} {year}: {e}")
                    conf_results[year] = 0
                    self.progress['scraping']['completed'] += 1
            
            results[conf] = conf_results
        
        self.progress['scraping']['status'] = 'completed'
        print(f"\n✅ 论文爬取完成！总计: {total_papers:,} 篇论文")
        
        return results
    
    async def download_pdfs(self) -> Dict[str, int]:
        """下载PDF文件"""
        if not self.enable_pdf_download:
            print("\n⏭️ 跳过PDF下载")
            return {'downloaded': 0, 'failed': 0, 'skipped': 0}
        
        print("\n📥 开始下载PDF文件...")
        self.progress['pdf_download']['status'] = 'running'
        
        try:
            # 检查现有PDF状态
            status = self.pdf_manager.get_download_status()
            print(f"📊 当前PDF状态: {status['total_pdfs']:,}/{status['total_papers']:,} ({status['download_rate']:.1%})")
            
            # 执行增量下载
            async with PDFDownloader() as downloader:
                stats = await downloader.download_all_papers(
                    conferences=self.conferences,
                    years=self.years
                )
            
            self.progress['pdf_download']['status'] = 'completed'
            print(f"\n✅ PDF下载完成！")
            print(f"   📥 新下载: {stats['downloaded']}")
            print(f"   ❌ 失败: {stats['failed']}")
            print(f"   ⏭️ 跳过: {stats['skipped']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"PDF download failed: {e}")
            self.progress['pdf_download']['status'] = 'failed'
            return {'downloaded': 0, 'failed': 1, 'skipped': 0}
    
    def check_pdf_duplicates(self, papers_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """检查PDF重复和缺失情况"""
        print("\n🔍 检查PDF文件状态...")
        
        existing_pdfs = []
        missing_pdfs = []
        
        pdf_base_dir = Path("outputs/data/pdfs")
        
        for paper in papers_data:
            title = paper.get('title', 'Unknown')
            conference = paper.get('conference', 'Unknown')
            year = paper.get('year', 2024)
            
            # 生成可能的文件名
            if hasattr(self.pdf_manager, 'generate_filename'):
                filename = self.pdf_manager.generate_filename(title, conference, year)
            else:
                # 简单的文件名生成
                safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')[:100]
                filename = f"{safe_title}_{year}.pdf"
            
            pdf_path = pdf_base_dir / conference / filename
            
            if pdf_path.exists() and pdf_path.stat().st_size > 1000:  # 至少1KB
                existing_pdfs.append(paper)
            else:
                missing_pdfs.append(paper)
        
        print(f"   ✅ 已存在PDF: {len(existing_pdfs)}")
        print(f"   ❌ 缺失PDF: {len(missing_pdfs)}")
        
        return existing_pdfs, missing_pdfs
    
    def filter_unencoded_papers(self, papers_data: List[Dict]) -> Tuple[List[Dict], int, int]:
        """过滤出未编码的论文"""
        if not self.enable_milvus:
            return papers_data, len(papers_data), 0
        
        print(f"\n🔍 检查已编码论文状态...")
        
        # 生成论文ID
        paper_ids = []
        for i, paper_data in enumerate(papers_data):
            paper_id = paper_data.get('id') or f"{paper_data.get('conference', 'UNK')}_{paper_data.get('year', 2024)}_{i}"
            paper_ids.append(paper_id)
            paper_data['generated_id'] = paper_id  # 保存生成的ID
        
        # 检查已存在的论文
        if not self.milvus_client and not self.simple_vector_store and self.enable_milvus:
            # 延迟初始化向量存储
            self._initialize_milvus()
        
        storage_client = self.milvus_client or self.simple_vector_store
        if storage_client:
            try:
                existing_ids = storage_client.get_existing_paper_ids(
                    conferences=self.conferences,
                    years=self.years
                )
            except Exception as e:
                logger.warning(f"Failed to check existing papers: {e}")
                existing_ids = set()
        else:
            existing_ids = set()
        
        # 过滤未编码的论文
        unencoded_papers = []
        for paper_data in papers_data:
            paper_id = paper_data['generated_id']
            if paper_id not in existing_ids:
                unencoded_papers.append(paper_data)
        
        existing_count = len(papers_data) - len(unencoded_papers)
        print(f"   📊 总论文: {len(papers_data)}")
        print(f"   ✅ 已编码: {existing_count}")
        print(f"   🆕 待编码: {len(unencoded_papers)}")
        
        return unencoded_papers, len(unencoded_papers), existing_count

    def encode_papers_to_vectors(self, papers_data: List[Dict]) -> Tuple[List[Paper], int]:
        """将论文编码为向量（只处理未编码的论文）"""
        if not self.enable_milvus or not self.text_encoder:
            print("\n⏭️ 跳过向量编码")
            return [], 0
        
        # 过滤未编码的论文
        unencoded_papers, unencoded_count, existing_count = self.filter_unencoded_papers(papers_data)
        
        if unencoded_count == 0:
            print("\n✅ 所有论文已编码，跳过向量编码步骤")
            return [], 0
        
        print(f"\n🧮 开始向量编码 {unencoded_count} 篇新论文...")
        self.progress['vector_encoding']['status'] = 'running'
        self.progress['vector_encoding']['total'] = unencoded_count
        
        paper_objects = []
        success_count = 0
        
        # 批量编码文本
        try:
            print("   📝 批量编码文本内容...")
            text_embeddings, semantic_embeddings = self.text_encoder.batch_encode_papers(unencoded_papers)
            
            print(f"   ✅ 编码完成: {text_embeddings.shape[0]} 篇论文")
            
            # 创建Paper对象
            for i, paper_data in enumerate(unencoded_papers):
                try:
                    # 创建Paper对象（根据Paper类的构造函数签名）
                    paper = Paper(
                        title=paper_data.get('title', ''),
                        abstract=paper_data.get('abstract', ''),
                        conference=paper_data.get('conference', ''),
                        year=int(paper_data.get('year', 2024)),
                        url=paper_data.get('url', ''),
                        pdf_url=paper_data.get('pdf_url', ''),
                        paper_id=paper_data.get('generated_id', f"{paper_data.get('conference', 'UNK')}_{paper_data.get('year', 2024)}_{i}")
                    )
                    
                    # 添加其他信息
                    if paper_data.get('keywords'):
                        paper.keywords = paper_data['keywords']
                    if paper_data.get('authors'):
                        from conf_analysis.core.models.paper import AuthorInfo
                        author_info = AuthorInfo(names=paper_data['authors'])
                        paper.add_author_info(author_info)
                    
                    # 设置向量
                    if i < len(text_embeddings):
                        paper.set_text_vector(text_embeddings[i])
                    if i < len(semantic_embeddings):
                        paper.set_semantic_vector(semantic_embeddings[i])
                    
                    # 分析任务场景
                    paper.analyze_task_scenario()
                    
                    paper_objects.append(paper)
                    success_count += 1
                    
                    self.progress['vector_encoding']['completed'] += 1
                    
                    if success_count % 100 == 0:
                        self._print_progress('vector_encoding')
                        
                except Exception as e:
                    logger.error(f"Failed to process paper {i}: {e}")
            
            self.progress['vector_encoding']['status'] = 'completed'
            print(f"\n✅ 向量编码完成！新编码: {success_count}/{unencoded_count}, 总计跳过: {existing_count}")
            
        except Exception as e:
            logger.error(f"Batch encoding failed: {e}")
            self.progress['vector_encoding']['status'] = 'failed'
        
        return paper_objects, success_count
    
    def store_to_milvus(self, paper_objects: List[Paper]) -> int:
        """存储到Milvus数据库"""
        if not self.enable_milvus or not paper_objects:
            print("\n⏭️ 跳过Milvus存储")
            return 0
        
        # 初始化向量存储连接
        if not self.milvus_client and not self.simple_vector_store:
            if not self._initialize_milvus():
                return 0
        
        # 确定使用哪种存储
        storage_type = "Milvus" if self.milvus_client else "Simple Vector Store"
        storage_client = self.milvus_client or self.simple_vector_store
        
        print(f"\n🗄️ 开始存储到{storage_type}: {len(paper_objects)} 篇论文...")
        self.progress['milvus_storage']['status'] = 'running'
        self.progress['milvus_storage']['total'] = len(paper_objects)
        
        try:
            # 批量插入
            success_count, total_count = storage_client.batch_insert_papers(
                paper_objects, batch_size=100
            )
            
            self.progress['milvus_storage']['completed'] = success_count
            self.progress['milvus_storage']['status'] = 'completed'
            
            print(f"\n✅ {storage_type}存储完成！成功存储: {success_count}/{total_count}")
            
            # 显示集合信息
            collection_info = storage_client.get_collection_info()
            if 'statistics' in collection_info:
                print(f"📊 数据库统计: {collection_info['statistics']}")
            elif 'total_papers' in collection_info:
                print(f"📊 存储统计: 总论文数 {collection_info['total_papers']}")
            
            return success_count
            
        except Exception as e:
            logger.error(f"{storage_type} storage failed: {e}")
            self.progress['milvus_storage']['status'] = 'failed'
            return 0
    
    def perform_analysis(self) -> Optional[Dict]:
        """执行论文分析"""
        print("\n📊 开始分析论文数据...")
        self.progress['analysis']['status'] = 'running'
        
        try:
            # 执行综合分析
            results = self.analyzer.perform_comprehensive_analysis()
            
            self.progress['analysis']['status'] = 'completed'
            print("\n✅ 分析完成！")
            print(f"📊 总论文数: {results['basic_statistics']['total_papers']:,}")
            print(f"📅 时间跨度: {results['basic_statistics']['year_range']}")
            print(f"🏛️ 覆盖会议: {len(results['basic_statistics']['conferences'])}个")
            print(f"📈 整体增长率: {results['temporal_analysis']['total_growth_rate']:.1f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.progress['analysis']['status'] = 'failed'
            return None
    
    def generate_reports(self, analysis_results: Dict) -> bool:
        """生成分析报告"""
        print("\n📋 生成分析报告...")
        
        try:
            # 读取模板
            template_file = Path("frontend/unified_analysis_dashboard.html")
            if not template_file.exists():
                logger.error(f"Dashboard template not found at {template_file}")
                print(f"❌ 模板文件不存在: {template_file}")
                # 创建简单的HTML报告
                self._create_simple_report(analysis_results)
                return True
            
            with open(template_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 嵌入数据
            data_script = f'''<script>
                window.embeddedAnalysisData = {json.dumps(analysis_results, ensure_ascii=False, indent=4)};
            </script>'''
            
            html_content = html_content.replace('</head>', f'{data_script}\n</head>')
            
            # 保存报告
            output_file = Path("outputs/unified_analysis_report.html")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📊 统一分析报告已生成: {output_file}")
            print(f"🌐 使用浏览器打开查看: {output_file.absolute()}")
            
            # 显示关键结果
            self._display_key_results(analysis_results)
            
            return True
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return False
    
    def _create_simple_report(self, analysis_results: Dict) -> None:
        """创建简单的HTML报告"""
        try:
            # 创建JSON安全的数据副本
            def make_json_safe(obj):
                if isinstance(obj, dict):
                    return {str(k): make_json_safe(v) for k, v in obj.items() if not isinstance(k, tuple)}
                elif isinstance(obj, list):
                    return [make_json_safe(item) for item in obj]
                elif isinstance(obj, tuple):
                    return list(obj)
                elif hasattr(obj, '__dict__'):
                    return str(obj)
                else:
                    return obj
            
            safe_results = make_json_safe(analysis_results)
            
            html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI会议论文分析报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .section {{ margin: 30px 0; }}
        .list-item {{ margin: 10px 0; padding: 10px; background: #fff; border-left: 4px solid #007bff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI会议论文分析报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stat-card">
        <h2>📊 基础统计</h2>
        <p><strong>总论文数:</strong> {analysis_results.get('basic_statistics', {}).get('total_papers', 0):,}</p>
        <p><strong>时间跨度:</strong> {analysis_results.get('basic_statistics', {}).get('year_range', 'N/A')}</p>
        <p><strong>会议数量:</strong> {len(analysis_results.get('basic_statistics', {}).get('conferences', []))}</p>
        <p><strong>增长率:</strong> {analysis_results.get('temporal_analysis', {}).get('total_growth_rate', 0):.1f}%</p>
    </div>
    
    <div class="section">
        <h2>🎯 热门应用场景</h2>"""
            
            # 添加应用场景数据
            if 'task_scenario_analysis' in analysis_results:
                scenarios = analysis_results['task_scenario_analysis'].get('top_scenarios', [])
                for i, scenario in enumerate(scenarios[:10], 1):
                    count = analysis_results['task_scenario_analysis']['scenario_distribution'].get(scenario, 0)
                    html_content += f"""
        <div class="list-item">
            <strong>{i}. {scenario}</strong> - {count} 篇论文
        </div>"""
            
            html_content += """
    </div>
    
    <div class="section">
        <h2>🔥 新兴技术趋势</h2>"""
            
            # 添加新兴趋势数据
            if 'emerging_trends' in analysis_results:
                emerging = analysis_results['emerging_trends'].get('emerging_application_scenarios', {})
                for scenario, data in list(emerging.items())[:5]:
                    html_content += f"""
        <div class="list-item">
            <strong>{scenario}</strong> - 增长率: +{data.get('growth_rate', 0)}%
        </div>"""
            
            html_content += """
    </div>
    
    <div class="section">
        <h2>📈 数据可视化</h2>
        <p>完整的交互式数据可视化需要运行完整版本的仪表板。</p>
        <p>详细数据请查看: <code>outputs/analysis/comprehensive_analysis.json</code></p>
    </div>
    
    <script>
        // 数据摘要信息
        window.analysisSummary = {
            total_papers: """ + str(analysis_results.get('basic_statistics', {}).get('total_papers', 0)) + """,
            conferences: """ + str(len(analysis_results.get('basic_statistics', {}).get('conferences', []))) + """,
            year_range: '""" + str(analysis_results.get('basic_statistics', {}).get('year_range', 'N/A')) + """',
            growth_rate: """ + str(analysis_results.get('temporal_analysis', {}).get('total_growth_rate', 0)) + """
        };
    </script>
</body>
</html>"""
            
            # 保存简单报告
            output_file = Path("outputs/unified_analysis_report.html")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📊 简化分析报告已生成: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to create simple report: {e}")
            import traceback
            traceback.print_exc()
    
    def _display_key_results(self, results: Dict) -> None:
        """显示关键分析结果"""
        # 显示热门应用场景
        if 'task_scenario_analysis' in results and results['task_scenario_analysis']:
            scenarios = results['task_scenario_analysis'].get('top_scenarios', [])
            if scenarios:
                print(f"\n🎯 热门应用场景:")
                for i, scenario in enumerate(scenarios[:5], 1):
                    count = results['task_scenario_analysis']['scenario_distribution'].get(scenario, 0)
                    print(f"   {i}. {scenario} ({count} 篇)")
        
        # 显示新兴趋势
        if 'emerging_trends' in results:
            emerging = results['emerging_trends'].get('emerging_application_scenarios', {})
            if emerging:
                print(f"\n🔥 新兴技术趋势:")
                for scenario, data in list(emerging.items())[:3]:
                    print(f"   📈 {scenario}: +{data['growth_rate']}% 增长")
    
    def _print_progress(self, task: str) -> None:
        """打印进度信息"""
        progress = self.progress[task]
        if progress['total'] > 0:
            percentage = (progress['completed'] / progress['total']) * 100
            print(f"    进度: {progress['completed']}/{progress['total']} ({percentage:.1f}%)")
    
    def print_final_summary(self) -> None:
        """打印最终摘要"""
        print("\n" + "=" * 80)
        print("🎉 AI会议论文分析系统 - 执行完成")
        print("=" * 80)
        
        for task, progress in self.progress.items():
            status_emoji = {
                'completed': '✅',
                'running': '🔄',
                'failed': '❌',
                'pending': '⏸️'
            }.get(progress['status'], '❓')
            
            task_names = {
                'scraping': '论文爬取',
                'pdf_download': 'PDF下载',
                'vector_encoding': '向量编码',
                'milvus_storage': 'Milvus存储',
                'analysis': '数据分析'
            }
            
            task_name = task_names.get(task, task)
            print(f"{status_emoji} {task_name}: {progress['status']}")
            
            if 'total' in progress and progress['total'] > 0:
                print(f"   完成: {progress['completed']}/{progress['total']}")
        
        print("\n📂 输出目录结构:")
        print("   outputs/")
        print("   ├── data/raw/              # 论文元数据JSON")
        print("   ├── data/pdfs/             # PDF文件")
        print("   ├── analysis/              # 分析结果数据")
        print("   └── unified_analysis_report.html # 分析报告")
        
        if self.enable_milvus:
            print("\n🗄️ Milvus数据库已就绪，支持以下功能:")
            print("   • 语义相似论文搜索")
            print("   • 任务场景分类检索")
            print("   • 混合查询 (文本+语义)")
            print("   • 智能增量编码 (只处理新论文)")
        
        print("\n" + "=" * 80)
    
    async def run_complete_pipeline(self) -> Dict:
        """运行完整的端到端流水线"""
        print("🚀 启动 AI会议论文分析系统 - 完整流水线")
        print("=" * 60)
        print(f"📋 会议: {', '.join(self.conferences)}")
        print(f"📅 年份: {self.years[0]}-{self.years[-1]}")
        print(f"🗄️ Milvus存储: {'启用' if self.enable_milvus else '禁用'}")
        print(f"📥 PDF下载: {'启用' if self.enable_pdf_download else '禁用'}")
        print("=" * 60)
        
        pipeline_results = {}
        
        try:
            # 1. 爬取论文元数据
            scraping_results = await self.scrape_papers()
            pipeline_results['scraping'] = scraping_results
            
            # 2. 加载所有论文数据
            print("\n📚 加载论文数据...")
            all_papers_data = []
            
            for conf in self.conferences:
                for year in self.years:
                    json_file = Path(f"outputs/data/raw/{conf}_{year}.json")
                    if json_file.exists():
                        with open(json_file, 'r', encoding='utf-8') as f:
                            papers = json.load(f)
                            # 添加conference和year信息
                            for paper in papers:
                                paper['conference'] = conf
                                paper['year'] = year
                            all_papers_data.extend(papers)
            
            print(f"   📊 总计加载: {len(all_papers_data)} 篇论文")
            
            # 3. 检查PDF状态
            if self.enable_pdf_download:
                existing_pdfs, missing_pdfs = self.check_pdf_duplicates(all_papers_data)
                pipeline_results['pdf_status'] = {
                    'existing': len(existing_pdfs),
                    'missing': len(missing_pdfs)
                }
            
            # 4. 下载缺失的PDF
            pdf_results = await self.download_pdfs()
            pipeline_results['pdf_download'] = pdf_results
            
            # 5. 向量编码（智能跳过已编码论文）
            paper_objects, encoding_count = self.encode_papers_to_vectors(all_papers_data)
            pipeline_results['vector_encoding'] = encoding_count
            
            # 6. 存储到Milvus
            milvus_count = self.store_to_milvus(paper_objects)
            pipeline_results['milvus_storage'] = milvus_count
            
            # 7. 执行分析
            analysis_results = self.perform_analysis()
            if analysis_results:
                pipeline_results['analysis'] = 'success'
                
                # 8. 生成报告
                report_success = self.generate_reports(analysis_results)
                pipeline_results['reports'] = 'success' if report_success else 'failed'
            else:
                pipeline_results['analysis'] = 'failed'
                pipeline_results['reports'] = 'skipped'
            
            return pipeline_results
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            pipeline_results['error'] = str(e)
            return pipeline_results
        
        finally:
            # 清理资源
            if self.milvus_client:
                self.milvus_client.disconnect()
            
            # 打印最终摘要
            self.print_final_summary()


def main(conferences: Optional[List[str]] = None, 
         years: Optional[List[int]] = None,
         enable_milvus: bool = True,
         enable_pdf_download: bool = True):
    """主函数 - 启动完整的论文分析流水线"""
    
    # 创建集成系统
    system = IntegratedPaperAnalysisSystem(
        conferences=conferences,
        years=years,
        enable_milvus=enable_milvus,
        enable_pdf_download=enable_pdf_download
    )
    
    # 运行完整流水线
    try:
        results = asyncio.run(system.run_complete_pipeline())
        return results
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断执行")
        return None
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        return None


if __name__ == "__main__":
    main()