#!/usr/bin/env python3
"""
生成自包含的分析报告HTML文件
将JSON数据嵌入HTML中，避免CORS问题
"""

import json
from pathlib import Path

def generate_standalone_report():
    """生成自包含的HTML报告"""
    
    # 读取分析数据
    analysis_file = Path("outputs/analysis/comprehensive_analysis.json")
    if not analysis_file.exists():
        print("❌ 分析数据文件不存在，请先运行分析")
        return False
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 读取HTML模板
    template_file = Path("frontend/dashboard.html")
    with open(template_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 将数据嵌入HTML
    # 找到fetch部分并替换
    old_fetch = '''                // 加载分析数据
                const response = await fetch('../outputs/analysis/comprehensive_analysis.json');
                analysisData = await response.json();'''
    
    new_data = f'''                // 嵌入的分析数据
                analysisData = {json.dumps(analysis_data, ensure_ascii=False, indent=8)};'''
    
    # 替换数据加载部分
    html_content = html_content.replace(old_fetch, new_data)
    
    # 保存自包含的HTML文件
    output_file = Path("frontend/report.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 自包含报告已生成: {output_file}")
    print(f"📊 直接用浏览器打开文件即可查看: {output_file.absolute()}")
    
    return True

if __name__ == "__main__":
    generate_standalone_report()