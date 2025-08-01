# CLAUDE.md

这是为Claude Code（claude.ai/code）提供的项目开发指南。

## 🎯 项目概述

**AI会议论文分析系统** 是一个端到端的智能论文分析平台，专门针对顶级AI/ML会议进行数据采集、分析和可视化。

### 核心功能
- **多会议论文爬取**: 支持AAAI、ICLR、ICML、IJCAI、NeuRIPS五大顶级会议
- **智能分析引擎**: 基于70+应用场景、25+技术趋势、18+任务类型的多维度分析
- **向量存储系统**: 双模式存储（Milvus分布式 + 本地SimpleVectorStore）
- **PDF管理系统**: 智能下载与反爬虫机制
- **可视化仪表板**: 交互式HTML报告和趋势分析

### 技术栈
- **后端**: Python 3.8+, AsyncIO, BeautifulSoup, Pandas
- **机器学习**: SentenceTransformers, Transformers, Scikit-learn
- **数据库**: Milvus向量数据库, JSON本地存储
- **前端**: HTML5, JavaScript, Chart.js, ECharts
- **部署**: Docker Compose, 支持本地和云端部署

## 🚀 开发命令

### 环境设置
```bash
# 安装依赖
pip install -r requirements.txt

# 或使用Conda
conda env create -f environment.yml
conda activate ConfAnalysis

# 启动Milvus向量数据库（可选）
docker-compose up -d
```

### 主要命令
```bash
# 🎯 完整分析流水线（推荐）
python main.py

# 🔧 模块化调用
python -m conf_analysis.main

# 📊 生成综合仪表板
python -c "from tools.generators.unified_dashboard_generator import UnifiedDashboardGenerator; UnifiedDashboardGenerator().generate_all_dashboards()"

# 📈 趋势分析
python -c "from tools.analyzers.unified_trend_analyzer import UnifiedTrendAnalyzer; UnifiedTrendAnalyzer().run_comprehensive_analysis()"

# 🔍 完整数据集分析
python tools/generators/full_dataset_analyzer.py

# 📄 PDF下载管理
python -c "from conf_analysis.core.utils.pdf_manager import PDFManager; PDFManager().download_all_missing_pdfs()"
```

### 测试与调试
```bash
# 运行测试
python tests/quick_test_2025.py
python tests/test_2025_scrapers.py

# 调试特定组件
python tests/debug/test_integrated_system.py
```

## 🏗️ 系统架构

### 端到端数据流
```
1. 数据采集层 → 2. 处理分析层 → 3. 存储层 → 4. 可视化层
     ↓              ↓              ↓           ↓
🕷️ 爬虫系统    ⚙️ 分析引擎     💾 向量存储   📊 仪表板
```

### 核心组件架构

#### 1. 数据采集系统 (`conf_analysis/core/scrapers/`)
- **BaseScraper**: 通用爬虫基类，实现重试机制和错误处理
- **会议专用爬虫**: 针对每个会议的专用实现
  - `AAAIScraper`: AAAI会议爬虫，支持Cloudflare反爬
  - `ICLRScraper`: ICLR/OpenReview平台爬虫
  - `ICMLScraper`: ICML/MLR Press爬虫
  - `IJCAIScraper`: IJCAI会议爬虫
  - `NeuRIPSScraper`: NeurIPS论文爬虫

#### 2. 智能分析引擎 (`conf_analysis/core/analyzer.py`)
**UnifiedAnalyzer** 是系统的分析核心，具备：

##### 🎯 应用场景识别 (70+子领域)
- **医疗健康** (8个子领域): 医学影像、临床诊断、药物发现、基因组学、心理健康、流行病学、医疗机器人、远程医疗
- **金融科技** (7个子领域): 算法交易、风险管理、反欺诈、信贷评分、智能投顾、数字支付、保险科技
- **交通出行** (6个子领域): 自动驾驶、驾驶辅助、交通优化、智能基础设施、安全监控、物流配送
- **智慧城市** (6个子领域): 城市基础设施、智能电网、环境监测、智能建筑、城市出行、废物管理
- **教育科技** (6个子领域): 自适应学习、教育评估、课程内容、语言学习、STEM教育、特殊教育
- **其他领域**: 内容创作、工业制造、网络安全、社交媒体、科学研究、农业科技、零售电商、人机交互、游戏娱乐

##### 🔬 技术趋势分析 (25+前沿技术)
- **基础架构演进**: Transformer演进、CNN架构、图神经网络、生成模型、记忆网络
- **学习范式创新**: 基础模型、自监督学习、小样本学习、联邦学习、持续学习、迁移学习
- **优化效率技术**: 神经架构搜索、模型压缩、训练优化、软硬件协同设计
- **新兴技术前沿**: 大语言模型、多模态智能、检索增强生成、高级提示技术、AI智能体

##### 📋 任务场景分类 (18+核心任务)
- **基础AI任务**: 分类识别、回归预测、聚类分割
- **生成创造任务**: 内容生成、数据增强、风格迁移
- **优化决策任务**: 优化搜索、决策制定、资源配置
- **理解分析任务**: 理解解释、知识提取、异常检测
- **交互对话任务**: 对话AI、推荐系统
- **多模态任务**: 多模态学习、迁移学习
- **安全隐私任务**: 隐私保护、鲁棒性安全

#### 3. 向量存储系统
**双模式存储架构**:

##### Milvus分布式存储 (`conf_analysis/core/database/milvus_client.py`)
- 高性能向量相似度搜索
- 支持大规模数据集
- 分布式架构，可水平扩展
- 适合生产环境部署

##### SimpleVectorStore本地存储 (`conf_analysis/core/database/simple_vector_store.py`)
- 轻量级本地实现
- 无外部依赖
- JSON + NumPy存储
- 适合开发和小规模应用

#### 4. PDF管理系统 (`conf_analysis/core/utils/pdf_manager.py`)
**智能PDF下载器**具备：
- **反爬虫机制**: 现代浏览器头、Cookie支持、域名特定延迟
- **下载优化**: 并发下载、断点续传、自动重试
- **URL转换**: 支持直接PDF链接提取
- **Cloudflare绕过**: 检测和处理挑战页面

#### 5. 文本编码系统 (`conf_analysis/core/embeddings/text_encoder.py`)
**多模型支持**:
- **SentenceTransformers**: 多语言支持、预训练优化
- **Transformers**: 灵活的模型选择
- **缓存机制**: 本地模型缓存和向量缓存

### 数据处理流水线

#### 阶段1: 数据采集 🕷️
```python
# 爬虫并行采集
scrapers = [AAAIScraper(), ICLRScraper(), ICMLScraper(), IJCAIScraper(), NeuRIPSScraper()]
papers_data = await scrape_all_conferences(scrapers, years=[2020-2025])
# → 输出: outputs/data/raw/{CONFERENCE}_{YEAR}.json
```

#### 阶段2: PDF下载 📥
```python
# 智能PDF下载
pdf_manager = PDFManager()
download_stats = await pdf_manager.download_all_missing_pdfs()
# → 输出: outputs/data/pdfs/{CONFERENCE}/{YEAR}/
```

#### 阶段3: 文本编码 🔤
```python
# 向量编码
encoder = PaperTextEncoder(model='paraphrase-multilingual-MiniLM-L12-v2') 
vectors = encoder.encode_papers(papers)
# → 384维向量表示
```

#### 阶段4: 向量存储 💾
```python
# 存储到向量数据库
vector_store = SimpleVectorStore()  # 或 MilvusClient()
vector_store.store_papers(papers, vectors)
# → 向量搜索就绪
```

#### 阶段5: 智能分析 🧠
```python
# 多维度分析
analyzer = UnifiedAnalyzer()
results = analyzer.perform_comprehensive_analysis()
# → 70+场景 + 25+技术趋势 + 18+任务分类
```

#### 阶段6: 可视化生成 📊
```python
# 交互式仪表板
dashboard_gen = UnifiedDashboardGenerator()
dashboard_gen.generate_all_dashboards()
# → HTML交互式报告
```

## 📊 输出文件说明

### 主要输出
- **`outputs/reports/unified_analysis_report.html`**: 📈 综合分析报告
- **`outputs/reports/unified_dashboard.html`**: 🎛️ 交互式仪表板
- **`outputs/analysis/comprehensive_analysis.json`**: 📋 完整分析数据

### 数据结构
```
outputs/
├── data/                    # 📁 数据文件
│   ├── raw/                # 原始JSON数据 (按会议年份)
│   ├── pdfs/               # PDF文件 (按会议分类)
│   └── backup/             # 数据备份
├── analysis/               # 📊 分析结果
│   ├── comprehensive_analysis.json
│   ├── complete_dataset_analysis.json
│   └── processed_papers.csv
├── reports/                # 📈 HTML报告
├── cache/                  # 🔄 缓存文件
└── vector_store/           # 🗄️ 向量存储
```

## 🔧 扩展开发

### 添加新会议
1. 继承`BaseScraper`创建新爬虫
2. 实现`get_papers_for_year(year)`方法
3. 在`config.py`中添加会议配置
4. 更新`main.py`中的爬虫映射

### 添加新分析维度
1. 编辑`TaskScenarioAnalyzer`
2. 扩展场景/任务/趋势分类字典
3. 更新分析方法
4. 扩展可视化模板

### 自定义PDF下载策略
1. 扩展`PDFDownloader.get_direct_pdf_url()`
2. 添加新的URL转换规则
3. 配置域名特定延迟
4. 更新反爬虫头信息

## 🏷️ 核心开发原则

### 1. KISS原则 - Keep It Simple Stupid
**保持代码简单有效**
- ✅ 最小化修改范围 - 只修改必要文件
- ✅ 避免过度工程 - 优先使用简单方案
- ✅ 拒绝不必要依赖 - 除非绝对必要
- ❌ 禁止炫技实现 - 简单解决方案优先
- ❌ 禁止过早优化 - 无性能问题时不优化

### 2. YAGNI原则 - You Aren't Gonna Need It  
**只实现当前需要的功能**
- ✅ 专注当前需求 - 只解决明确提出的问题
- ✅ 避免预测性编程 - 不为"可能的未来需求"编码
- ✅ 最小化修改范围 - 只修改必须修改的代码
- ❌ 禁止"以防万一"功能 - 用户未要求不实现
- ❌ 禁止过度设计扩展性 - 当前不需要不添加

### 3. DRY原则 - Don't Repeat Yourself
**避免代码重复，但不过度抽象**
- ✅ 合理复用 - 相同逻辑出现3次以上才考虑抽象
- ✅ 保持一致性 - 使用项目现有模式和组件
- ✅ 渐进式重构 - 基于现有代码改进，不重写
- ❌ 禁止过度抽象 - 不为消除轻微重复创建复杂抽象
- ❌ 禁止重写运行良好的代码

### 开发决策清单
修改代码前，请确认：
- [ ] 这个修改是用户明确要求的吗？(YAGNI)
- [ ] 有更简单的实现方式吗？(KISS)
- [ ] 我在复用现有代码还是重新发明轮子？(DRY)
- [ ] 这个修改会增加不必要的复杂性吗？
- [ ] 我在解决真实问题还是想象的问题？

### 禁止行为
- 🚫 重写运行良好的现有代码
- 🚫 添加用户未要求的功能
- 🚫 引入新技术栈或框架（除非绝对必要）
- 🚫 为"最佳实践"进行大规模重构
- 🚫 在无性能问题时过度优化性能

## 🎯 核心理念

**简单有效的解决方案 > 复杂完美的架构**

当你想进行大量修改时，停下来想想：用户真的需要这些改变吗？有更简单的方法吗？

记住：**做用户要求的，仅此而已。**

## 📝 维护和支持

### 常见问题排查
1. **爬虫失败**: 检查网站结构变化，更新CSS选择器
2. **PDF下载403**: 更新反爬虫头信息，调整请求频率
3. **Milvus连接失败**: 确认Docker服务运行，检查端口配置
4. **分析结果异常**: 验证输入数据格式，检查分类字典

### 性能优化建议
- 使用缓存减少重复计算
- 批量处理向量编码
- 并行化数据采集
- 定期清理临时文件

---

**🎉 系统已完全优化，遵循KISS、YAGNI、DRY原则！**