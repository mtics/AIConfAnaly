#!/usr/bin/env python3
"""
AI会议论文分析系统 - 统一主入口
基于任务场景识别的智能分析系统
"""

import sys
import os
from pathlib import Path

# 确保正确的导入路径
sys.path.insert(0, str(Path(__file__).parent))

from conf_analysis.core.analyzer import UnifiedAnalyzer


def main():
    """主函数"""
    print("🚀 AI会议论文深度分析系统")
    print("=" * 50)
    print("基于任务场景识别的智能分析系统")
    print("区分真实应用场景与论文章节")
    print("=" * 50)
    
    try:
        # 初始化分析器
        analyzer = UnifiedAnalyzer()
        
        # 执行综合分析
        results = analyzer.perform_comprehensive_analysis()
        
        print("\n✅ 分析完成！")
        print(f"📊 总论文数: {results['basic_statistics']['total_papers']:,}")
        print(f"📅 时间跨度: {results['basic_statistics']['year_range']}")
        print(f"🏛️ 覆盖会议: {len(results['basic_statistics']['conferences'])}个")
        print(f"📈 整体增长率: {results['temporal_analysis']['total_growth_rate']:.1f}%")
        
        print("\n📂 分析结果已保存到: outputs/analysis/")
        
        # 生成自包含的HTML报告
        try:
            import json
            from pathlib import Path
            
            # 读取分析数据
            analysis_file = Path("outputs/analysis/comprehensive_analysis.json")
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # 读取统一分析仪表板模板
            template_file = Path("frontend/unified_analysis_dashboard.html")
            with open(template_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 将数据嵌入HTML
            data_script = f'''<script>
                window.embeddedAnalysisData = {json.dumps(analysis_data, ensure_ascii=False, indent=4)};
            </script>'''
            
            # 在</head>之前插入数据脚本
            html_content = html_content.replace('</head>', f'{data_script}\n</head>')
            
            # 保存自包含的统一分析报告
            output_file = Path("frontend/unified_analysis_report.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("📊 统一分析报告已生成: frontend/unified_analysis_report.html")
            print("🌐 查看细化分析: 用浏览器打开 frontend/unified_analysis_report.html")
        except Exception as e:
            print(f"⚠️  HTML报告生成失败: {e}")
            print("🌐 查看前端仪表板: frontend/index.html")
        
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
        
        return results
        
    except Exception as e:
        print(f"\n❌ 分析过程中出错: {e}")
        print("请检查数据文件是否存在于 outputs/data/raw/ 目录")
        return None


if __name__ == "__main__":
    main()