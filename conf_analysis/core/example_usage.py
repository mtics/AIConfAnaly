"""
使用示例 - 演示如何使用Paper类和Milvus数据库系统
"""

import sys
from pathlib import Path
import logging

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from models.paper import Paper, TaskScenarioAnalysis, PaperMetrics
from services.paper_service import PaperService
from database.milvus_client import MilvusClientConfig
from batch_processor import BatchProcessor, QueryInterface

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_single_paper():
    """示例1: 处理单篇论文"""
    print("=" * 50)
    print("示例1: 处理单篇论文")
    print("=" * 50)
    
    # 初始化服务
    paper_service = PaperService(
        encoder_type='sentence-transformer',
        enable_cache=True
    )
    
    # 处理论文
    paper = paper_service.process_and_store_paper(
        title="Deep Learning for Automated Skin Cancer Detection in Dermatoscopy Images",
        abstract="This paper presents a novel approach for automated detection of skin cancer using deep convolutional neural networks. We analyze dermatoscopy images to classify skin lesions as benign or malignant, achieving 94% accuracy on a dataset of 10,000 images. Our method could help dermatologists in early cancer detection and improve patient outcomes.",
        conference="MICCAI",
        year=2023,
        url="https://example.com/paper1"
    )
    
    if paper:
        print(f"✓ 论文处理成功: {paper.paper_id}")
        print(f"  标题: {paper.title}")
        print(f"  应用场景: {paper.task_scenario_analysis.application_scenario}")
        print(f"  任务类型: {paper.task_scenario_analysis.task_type}")
        print(f"  置信度: {paper.task_scenario_analysis.scenario_confidence:.3f}")
        print(f"  向量维度: {paper.text_embedding.shape if paper.text_embedding is not None else 'None'}")
    else:
        print("✗ 论文处理失败")


def example_batch_processing():
    """示例2: 批量处理论文"""
    print("\n" + "=" * 50)
    print("示例2: 批量处理论文")
    print("=" * 50)
    
    # 初始化批量处理器
    processor = BatchProcessor(
        milvus_host="localhost",
        milvus_port="19530",
        encoder_type="sentence-transformer"
    )
    
    # 示例论文数据
    sample_papers = [
        {
            'title': 'Reinforcement Learning for Autonomous Vehicle Path Planning in Urban Environments',
            'abstract': 'We propose a reinforcement learning approach for path planning in autonomous vehicles. Our method learns optimal driving policies in complex urban scenarios with dynamic obstacles and traffic rules.',
            'conference': 'ICRA',
            'year': 2023,
            'url': 'https://example.com/paper2'
        },
        {
            'title': 'Machine Learning Analysis of Financial Market Trends for Risk Assessment',
            'abstract': 'This study presents an empirical analysis of machine learning methods for predicting stock market movements. We evaluate various algorithms for financial risk assessment and portfolio optimization.',
            'conference': 'AAAI',
            'year': 2023,
            'url': 'https://example.com/paper3'
        },
        {
            'title': 'Natural Language Processing for Clinical Decision Support Systems',
            'abstract': 'We develop an NLP system to assist healthcare professionals in clinical decision making. Our approach extracts relevant information from electronic health records to support diagnostic processes.',
            'conference': 'ACL',
            'year': 2023,
            'url': 'https://example.com/paper4'
        }
    ]
    
    # 批量处理
    processed_papers, stats = processor.paper_service.batch_process_papers(
        papers_data=sample_papers,
        batch_size=10,
        analyze_all=True,
        store_all=True
    )
    
    print(f"✓ 批量处理完成")
    print(f"  总计: {stats['total_papers']} 篇论文")
    print(f"  成功处理: {stats['processed_papers']} 篇")
    print(f"  成功存储: {stats['inserted_papers']} 篇")
    print(f"  处理时间: {stats['processing_time']:.2f} 秒")
    
    # 显示处理结果
    for paper in processed_papers:
        if paper.task_scenario_analysis:
            print(f"\n  📄 {paper.title[:50]}...")
            print(f"     应用场景: {paper.task_scenario_analysis.application_scenario}")
            print(f"     任务类型: {paper.task_scenario_analysis.task_type}")


def example_search_and_query():
    """示例3: 搜索和查询论文"""
    print("\n" + "=" * 50)
    print("示例3: 搜索和查询论文")
    print("=" * 50)
    
    # 初始化查询接口
    query_interface = QueryInterface(
        milvus_host="localhost",
        milvus_port="19530"
    )
    
    # 1. 文本搜索
    print("\n1. 文本搜索 - '医疗诊断':")
    results = query_interface.search_papers(
        query="医疗诊断 皮肤癌检测",
        search_type="text",
        top_k=3
    )
    
    for i, paper in enumerate(results, 1):
        print(f"   {i}. {paper.get('title', 'No title')[:60]}...")
        print(f"      相似度: {paper.get('score', 0):.3f}")
        print(f"      会议: {paper.get('conference', 'Unknown')} ({paper.get('year', 'Unknown')})")
    
    # 2. 混合搜索
    print("\n2. 混合搜索 - '自动驾驶路径规划':")
    results = query_interface.search_papers(
        query="自动驾驶 路径规划 强化学习",
        search_type="hybrid",
        top_k=3
    )
    
    for i, paper in enumerate(results, 1):
        print(f"   {i}. {paper.get('title', 'No title')[:60]}...")
        print(f"      综合得分: {paper.get('combined_score', paper.get('score', 0)):.3f}")
        print(f"      应用场景: {paper.get('application_scenario', 'Unknown')}")
    
    # 3. 过滤查询
    print("\n3. 过滤查询 - 2023年AAAI会议:")
    results = query_interface.get_papers_by_filters(
        filters={
            'conference': 'AAAI',
            'year': 2023
        },
        limit=5
    )
    
    for i, paper in enumerate(results, 1):
        print(f"   {i}. {paper.get('title', 'No title')[:60]}...")
        print(f"      任务类型: {paper.get('task_type', 'Unknown')}")


def example_database_statistics():
    """示例4: 数据库统计信息"""
    print("\n" + "=" * 50)
    print("示例4: 数据库统计信息")
    print("=" * 50)
    
    # 初始化查询接口
    query_interface = QueryInterface()
    
    # 获取统计信息
    stats = query_interface.get_statistics()
    
    print("📊 数据库统计:")
    print(f"  已处理论文: {stats.get('processed_papers', 0)}")
    print(f"  已存储论文: {stats.get('inserted_papers', 0)}")
    print(f"  失败论文: {stats.get('failed_papers', 0)}")
    
    if 'encoder_info' in stats:
        encoder_info = stats['encoder_info']
        print(f"\n🔧 编码器信息:")
        print(f"  类型: {encoder_info.get('type', 'Unknown')}")
        print(f"  向量维度: {encoder_info.get('dimension', 'Unknown')}")
        
        if 'cache_stats' in encoder_info:
            cache_stats = encoder_info['cache_stats']
            print(f"  缓存文件: {cache_stats.get('total_files', 0)}")
            print(f"  缓存大小: {cache_stats.get('total_size_mb', 0):.2f} MB")


def example_export_data():
    """示例5: 导出数据"""
    print("\n" + "=" * 50)
    print("示例5: 导出数据")
    print("=" * 50)
    
    # 初始化查询接口
    query_interface = QueryInterface()
    
    # 导出搜索结果
    success = query_interface.export_search_results(
        query="机器学习 深度学习",
        output_path="outputs/search_results.json",
        search_type="hybrid",
        top_k=20,
        format="json"
    )
    
    if success:
        print("✓ 搜索结果已导出到 outputs/search_results.json")
    else:
        print("✗ 导出失败")
    
    # 使用PaperService导出过滤数据
    paper_service = PaperService()
    success = paper_service.export_papers(
        output_path="outputs/all_papers.csv",
        filters={'year_range': [2020, 2023]},
        format="csv"
    )
    
    if success:
        print("✓ 论文数据已导出到 outputs/all_papers.csv")
    else:
        print("✗ 导出失败")


def example_paper_similarity():
    """示例6: 论文相似性分析"""
    print("\n" + "=" * 50)
    print("示例6: 论文相似性分析")
    print("=" * 50)
    
    # 初始化查询接口
    query_interface = QueryInterface()
    
    # 首先搜索一篇论文
    search_results = query_interface.search_papers(
        query="深度学习",
        top_k=1
    )
    
    if search_results:
        target_paper = search_results[0]
        paper_id = target_paper.get('paper_id')
        
        print(f"目标论文: {target_paper.get('title', 'No title')[:60]}...")
        
        # 查找相似论文
        similar_papers = query_interface.get_similar_papers(
            paper_id=paper_id,
            top_k=5
        )
        
        print(f"\n找到 {len(similar_papers)} 篇相似论文:")
        for i, paper in enumerate(similar_papers, 1):
            print(f"  {i}. {paper.get('title', 'No title')[:60]}...")
            print(f"     相似度: {paper.get('score', 0):.3f}")
            print(f"     应用场景: {paper.get('application_scenario', 'Unknown')}")
    else:
        print("未找到论文进行相似性分析")


def main():
    """运行所有示例"""
    print("🚀 Paper类和Milvus数据库系统使用示例")
    print("注意: 确保Milvus服务器在localhost:19530运行")
    
    try:
        # 运行示例
        example_single_paper()
        example_batch_processing()
        example_search_and_query()
        example_database_statistics()
        example_export_data()
        example_paper_similarity()
        
        print("\n" + "=" * 50)
        print("✅ 所有示例运行完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        print("请检查:")
        print("1. Milvus服务器是否正在运行")
        print("2. 网络连接是否正常")
        print("3. 依赖包是否已安装")


if __name__ == "__main__":
    main()