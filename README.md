# AI Conference Paper Analysis System

## 🚀 项目简介

一个**重新组织优化**的AI会议论文分析系统，提供智能场景识别、技术趋势分析和交互式可视化。

### ✨ 核心特性

- **🎯 智能场景识别**: 40+细分应用领域分类
- **🔬 技术趋势分析**: 15+技术发展方向追踪  
- **⚙️ 任务类型分类**: 18+AI任务类别识别
- **📊 交互式仪表板**: 现代化单页面可视化
- **🏗️ 优化架构**: 清晰的模块化项目结构

## 📁 优化后的项目结构

```
ConfAnalysis/
├── conf_analysis/          # 🏗️ 核心分析系统
│   ├── core/              #   核心组件
│   │   ├── analyzer.py    #   主分析器
│   │   ├── scrapers/      #   数据抓取器
│   │   ├── models/        #   数据模型
│   │   └── utils/         #   工具函数
│   ├── docs/             #   项目文档
│   └── __init__.py       #   包初始化
├── tools/                 # 🔧 精简工具集
│   ├── analyzers/         #   统一分析器
│   ├── generators/        #   统一生成器
│   ├── utilities/         #   助手工具
│   └── data_generators/   #   数据生成器
├── frontend/             # 🎨 前端界面
├── outputs/              # 📊 分析结果
├── tests/               # 🧪 测试文件
├── main.py              # 🚪 统一主入口
└── CLAUDE.md            # 📋 开发指南
```

## 🚀 快速开始

### 安装依赖
```bash
# 使用pip安装
pip install -r requirements.txt

# 或使用conda
conda env create -f environment.yml
conda activate ConfAnalysis
```

### 运行分析
```bash
# 统一主入口（推荐）
python main.py

# 或者使用模块方式
python -m conf_analysis.main
```

### 查看结果
```bash
# 打开生成的统一分析报告
# frontend/unified_dashboard.html
```

## 🎯 主要改进

### ✅ 结构优化
- ✨ **模块化设计**: 清晰的功能分离
- 🗂️ **减少冗余**: 移除重复的代码文件
- 📁 **分类存储**: 工具、文档、核心代码分门别类
- 🧹 **精简前端**: 保留核心界面文件

### ✅ 代码整合
- 🔄 **统一入口**: 新的 `main_new.py` 主入口
- 📦 **包结构**: 标准Python包组织
- 🔗 **导入路径**: 优化的模块导入关系
- 🛠️ **工具集成**: 实用工具统一管理

### ✅ 文档整合  
- 📚 **统一文档**: 合并冗余的分析报告
- 📝 **清晰指南**: 更新的开发和使用说明
- 🏗️ **架构说明**: 详细的项目结构文档

## 📊 分析功能

### 智能分类系统
- **应用场景**: 医疗健康、自动驾驶、金融科技、智慧城市等40+领域
- **技术趋势**: Transformer、图神经网络、大语言模型等15+技术方向
- **任务类型**: 分类识别、生成创造、优化决策等18+任务类别

### 可视化仪表板
- 📈 年度发表趋势分析
- 🏛️ 会议分布统计
- 🎯 应用场景热力图  
- 🔬 技术趋势演进
- 📊 交叉分析图表

## 🧹 项目清理完成

✅ **已清理的冗余文件**:
- ❌ 根目录下的旧Python脚本 (generate_*.py, *_analyzer.py等)
- ❌ 旧的src/和code/目录 
- ❌ 冗余的文档文件 (各种SUMMARY.md)
- ❌ 重复的前端文件 (trend_visualization*.html等)

✅ **已完成精简清理**:
- ❌ 删除了冗余的MCP工具目录 (节省2.6MB空间)
- ❌ 删除了重复的趋势分析器 (合并为统一分析器)
- ❌ 删除了重复的仪表板生成器 (合并为统一生成器)
- ❌ 删除了空目录结构和临时文件

## 🔧 开发指南

详细的开发说明请参考：[CLAUDE.md](CLAUDE.md)

## 📈 使用示例

```python
from conf_analysis import UnifiedAnalyzer

# 创建分析器实例
analyzer = UnifiedAnalyzer()

# 执行综合分析
results = analyzer.perform_comprehensive_analysis()

# 查看结果
print(f"分析了 {results['basic_statistics']['total_papers']} 篇论文")
```

## 🔄 迁移指南

### 从旧版本迁移

旧的使用方式：
```bash
python main.py          # 旧主入口
python src/analyzer.py  # 旧分析器
```

新的使用方式：
```bash
python main.py          # 统一主入口  
python -m conf_analysis.main  # 模块方式
```

### 目录对应关系
```
旧结构 → 新结构
├── main_new.py → main.py (统一入口)
├── 重复分析器 → tools/analyzers/unified_trend_analyzer.py
├── 重复生成器 → tools/generators/unified_dashboard_generator.py
├── mcp_tools/ → 已删除 (节省2.6MB)
├── 空目录 → 已清理
└── frontend/ → frontend/ (保留核心功能)
```

---

**🎉 项目重构完成！现在拥有更清晰、更高效的代码结构！**