<!-- 顶部横幅 -->
<div align="center">
</div>

<!-- 标题与徽章 -->
<h1 align="center">
  ✨ Spark AI RAG Task Ordering ✨
</h1>
<p align="center">
  <em>智能 · 健康 · 高效 · 基于讯飞星火大模型的 RAG 日程优化引擎</em><br/>
  <em>Intelligent · Healthy · Efficient · RAG-based Daily Planner Powered by iFLYTEK Spark</em>
</p>

<p align="center">
  <a href="#"><img alt="Python" src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python"/></a>
  <a href="#"><img alt="Chroma" src="https://img.shields.io/badge/Chroma-VectorDB-00a4e4?style=flat"/></a>
  <a href="#"><img alt="iFLYTEK" src="https://img.shields.io/badge/Powered%20by-iFLYTEK%20Spark-ff5252?style=flat"/></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg?style=flat"/></a>
</p>

---

<!-- 中英文导航 -->
<div align="center">
  <strong>
    <a href="#📖-中文版">📖 中文版</a> 
  </strong>
</div>

---

<!-- 中文版 -->
## 📖 中文版

### 🚀 项目简介
“Spark AI RAG Task Ordering” 利用 **科大讯飞星火大模型** 与 **检索增强生成（RAG）** 技术，将用户输入的一整天任务 JSON 自动重排，为每个任务分配 **所需休息间隔** 与 **完成优先级**，并给出可解释的排序理由。  
从此告别“计划列出来，却不知道先做哪个”的烦恼！

### ✨ 核心特性
- 🧠 **大模型 + RAG** 双重决策，科学又人性化  
- 🕒 自动插入 休息时间  
- 🔍 实时从知识库检索“任务拆分”与“时长估算”最佳实践  
- 📊 输出结构化 JSON，方便二次开发或同步到日历  
- 🌐 支持 **中文/英文** 双语交互

### 🛠 技术栈
| 模块        | 技术选型                     |
|-------------|------------------------------|
| 大模型      | 科大讯飞 Spark API           |
| 向量数据库  | ChromaDB                     |
| 框架        | Python 3.9+ /         |
| 依赖管理    | Pip                 |

### 📦 安装 & 运行
```bash
# 1. 克隆仓库
git clone https://github.com/hacker-anglr/spark-ai-rag-task-ordering.git
cd spark-ai-rag-task-ordering

# 2. 安装依赖
pip install -r requirements.txt

# 3.参考对接文档食用
cat 对接文档.txt

###声明
此项目遵守MIT协议!请自觉遵守，谢谢!
