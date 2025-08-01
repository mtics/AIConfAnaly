# 🎯 AI会议论文分析系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](docker-compose.yml)

> **智能化的学术论文分析平台** - 专门针对顶级AI/ML会议的端到端数据采集、分析和可视化系统

## ✨ 核心特性

### 🚀 一键启动，端到端流水线
```bash
python main.py  # 完整分析流水线，从爬取到报告生成
```

### 🏆 顶级会议全覆盖
- **AAAI** - 人工智能协会会议
- **ICLR** - 国际学习表征会议  
- **ICML** - 国际机器学习会议
- **IJCAI** - 国际人工智能联合会议
- **NeurIPS** - 神经信息处理系统会议

### 🧠 智能多维分析引擎
- **70+应用场景识别** - 从医疗健康到金融科技，全面覆盖AI应用领域
- **25+技术趋势追踪** - 实时追踪从Transformer到多模态AI的技术演进
- **18+任务场景分类** - 精准识别论文的核心AI任务类型

### 💾 双模式向量存储
- **Milvus分布式存储** - 高性能生产级向量数据库
- **SimpleVectorStore** - 轻量级本地存储，零依赖部署

### 📊 交互式可视化仪表板
- 实时趋势分析
- 跨会议对比
- 技术发展脉络
- 研究热点识别

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
