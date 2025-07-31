# AI Conference Paper Analysis System

## 项目简介

这是一个综合性的AI会议论文分析系统，能够自动抓取和分析来自主要AI/ML会议的研究论文，提供深度的NLP分析、研究领域分类和交互式可视化。

## 核心特性

### 🎯 **智能场景识别 (40+类别)**
- **医疗健康**: 医疗诊断成像、药物发现、个性化医疗、心理健康分析
- **自动驾驶**: 自动驾驶、交通管理、车辆安全监控  
- **金融科技**: 算法交易、欺诈检测、信贷评分、数字银行
- **智慧城市**: 基础设施、能源管理、环境监测
- **更多领域**: 内容创作、工业制造、网络安全、科学研究等

### 🚀 **技术趋势分析 (15+类别)**
- **深度学习架构**: Transformer、CNN、图神经网络、扩散模型
- **学习范式**: 自监督学习、元学习、联邦学习、持续学习
- **新兴技术**: 大语言模型、多模态AI、检索增强、提示工程

### ⚙️ **任务分类系统 (18+类别)**
- **基础AI任务**: 分类识别、回归预测、聚类分割
- **生成创造**: 内容生成、数据增强、风格迁移
- **优化决策**: 优化搜索、决策制定、资源分配

## 项目结构

```
ConfAnalysis/
├── conf_analysis/          # 核心分析系统
│   ├── core/              # 核心分析组件
│   │   ├── analyzer.py    # 主分析器
│   │   ├── scrapers/      # 数据抓取器
│   │   ├── models/        # 数据模型
│   │   └── utils/         # 工具函数
│   ├── analysis/          # 高级分析工具
│   ├── visualization/     # 可视化组件
│   └── docs/             # 项目文档
├── tools/                 # 辅助工具
│   ├── data_generators/   # 数据生成工具
│   ├── visualization_generators/  # 可视化生成器
│   └── utilities/         # 实用工具
├── frontend/             # 前端界面
├── outputs/              # 分析结果
└── tests/               # 测试文件
```

## 快速开始

### 安装依赖

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 conda
conda env create -f environment.yml
conda activate ConfAnalysis
```

### 运行分析

```bash
# 完整分析流程
python main_new.py

# 或者使用模块方式
python -m conf_analysis.main
```

### 查看结果

分析完成后，可以通过以下方式查看结果：

- **综合报告**: 打开 `frontend/comprehensive_report.html`
- **分析数据**: 查看 `outputs/analysis/comprehensive_analysis.json`
- **摘要报告**: 阅读 `outputs/analysis/summary_report.md`

## 主要功能

### 数据抓取
- 支持主要AI会议：ICML、NeuRIPS、ICLR、AAAI、IJCAI
- 自动化论文元数据提取
- 内置速率限制和错误处理

### 智能分析
- **应用场景识别**: 40+细分应用领域
- **技术趋势分析**: 15+技术发展方向  
- **任务类型分类**: 18+AI任务类别
- **新兴趋势识别**: 自动发现快速增长的研究方向

### 可视化仪表板
- 现代化单页面设计
- 交互式图表和热力图
- 实时数据过滤和排序
- 响应式移动端支持

## 分析维度

### 时间维度
- 年度发展趋势
- 增长率计算
- 峰值年份识别

### 会议维度  
- 会议影响力评分
- 专业化方向分析
- 交叉领域研究

### 技术维度
- 技术成熟度评估
- 新兴技术识别
- 技术演进路径

### 应用维度
- 实际应用场景分类
- 商业化潜力评估
- 跨领域应用分析

## 输出说明

### 分析报告
- `comprehensive_analysis.json`: 完整分析数据
- `summary_report.md`: 可读性摘要
- `processed_papers.csv`: 处理后的论文数据

### 可视化界面
- `comprehensive_report.html`: 自包含的完整报告
- 支持离线浏览，无需服务器

## 技术架构

### 核心组件
- **UnifiedAnalyzer**: 主分析引擎
- **TaskScenarioAnalyzer**: 场景识别器
- **BaseScraper**: 抓取器基类

### 设计模式
- **策略模式**: 不同会议的抓取策略
- **模板方法**: 统一的分析流程
- **管道架构**: 顺序数据处理

## 扩展指南

### 添加新会议
1. 继承 `BaseScraper` 创建新抓取器
2. 实现 `get_papers_for_year()` 方法
3. 在配置中注册新会议

### 添加新分析维度
1. 扩展 `TaskScenarioAnalyzer` 类
2. 定义新的关键词分类
3. 更新可视化模板

## 开发团队

Conference Analysis Team

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。