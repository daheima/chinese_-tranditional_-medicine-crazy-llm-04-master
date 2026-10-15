# 个人简历

## 基本信息

**求职意向：** AI 工程师 / 大模型应用开发工程师  
**方向：** 中医知识图谱 · 智能问答系统

---

## 项目经历

### 中医知识图谱智能问答系统

**项目描述**

基于 Neo4j 知识图谱与 LangGraph 多节点 AI 工作流，构建面向中医领域的智能问答系统。系统支持多轮对话记忆、用户会话隔离、流式实时输出，能够理解中医语义并自动生成知识图谱查询语句，返回准确的中医知识。

**核心职责**

- 设计并实现 LangGraph 有状态工作流，包含语义转写、意图识别、实体抽取、向量匹配、Cypher 生成与校验、知识图谱查询、答案生成共 9 个节点，节点间通过 `AgentState`（TypedDict）传递状态
- 使用 FAISS + BGE-large-zh Sentence Transformer 构建中医实体向量索引，实现用户输入实体到 Neo4j 标准节点名的语义相似度匹配（阈值 0.65），解决用户表述与图谱节点名不一致的问题
- 设计 Cypher 自动生成与自愈机制：LLM 生成 Cypher → Neo4j EXPLAIN 校验 → 失败自动重试（最多 3 次）→ 超限降级为直接 LLM 回答，保障系统鲁棒性
- 基于 `InMemorySaver` 实现多用户会话隔离，每个用户通过 `session_id` 映射到独立 `thread_id`，历史消息使用 `Annotated[List[dict], operator.add]` reducer 自动追加，支持多轮上下文理解
- 设计基于 `asyncio.Queue` 的流式推送架构：LangGraph 工作流在线程池（`asyncio.to_thread`）中运行，各节点通过 `call_soon_threadsafe` 向主事件循环推送进度消息，FastAPI 以 `StreamingResponse` 实时返回给前端
- 使用 FastAPI 构建 RESTful 后端（`/process` 同步接口、`/process_stream` 流式接口），Streamlit 构建前端，实现推理过程实时展示与折叠
- 爬取中医药网站数据（BeautifulSoup + Playwright），通过 LLM 批量抽取疾病、症状、方剂、中药、功效、典籍六类实体及关系，导入 Neo4j 图数据库

**技术成果**

- 系统支持对"桂枝汤有什么功效"、"拉肚子吃什么药"等自然语言问题的端到端回答，准确率显著高于纯 LLM 直接回答
- 流式接口首包延迟 < 500ms，用户可实时看到每个推理步骤
- 多用户并发场景下会话记忆完全隔离，无串号现象

---

## 技术栈

| 方向 | 技术 |
|---|---|
| AI 工作流 | LangGraph、LangChain、LangSmith |
| 大语言模型 | DeepSeek（OpenAI 兼容接口）、vLLM（本地部署）、LoRA 微调 |
| 向量检索 | FAISS、BGE-large-zh（Sentence Transformers） |
| 图数据库 | Neo4j 5.x、Cypher |
| 后端框架 | FastAPI、Uvicorn、asyncio |
| 前端框架 | Streamlit |
| 数据处理 | Pandas、BeautifulSoup、Playwright |
| 工程化 | Python-dotenv、Pydantic v2、typing-extensions |

---

## 核心能力

- 熟悉 LLM 应用落地全链路：数据爬取 → 实体抽取 → 知识图谱构建 → RAG 检索 → 多节点 Agent 编排 → 流式 API 服务
- 深入理解 LangGraph 状态图设计：节点拆分、条件边、循环重试、InMemorySaver 持久化、Reducer 机制
- 熟悉 RAG 与 Graph RAG 结合实践：向量检索 + 图数据库查询的混合增强生成
- 具备大模型微调经验：vLLM 部署、多 LoRA 头并行加载推理
