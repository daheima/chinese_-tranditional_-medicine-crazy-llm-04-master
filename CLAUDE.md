# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Traditional Chinese Medicine (TCM) intelligent Q&A system combining a Neo4j knowledge graph with LangGraph AI workflows. Users ask TCM questions; the system either queries the knowledge graph or falls back to direct LLM responses.

## Environment Setup

All secrets and service credentials are in `common/.env`. Key variables:

- `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` — LLM API (OpenAI-compatible)
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — graph database
- `EMBEDDING_MODEL_PATH` — local path to BGE-large-zh SentenceTransformer model
- `LANGSMITH_API_KEY` — optional tracing

## Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend API (port 8000)
cd __005_fastapi && python main.py

# Start web UI (port 8501)
cd __006_streamlit && streamlit run app.py
```

The Streamlit UI calls the FastAPI `/process` endpoint (`POST {"input": "..."}`).

## Running Individual Modules

Every major Python file has an `if __name__ == '__main__':` block for standalone testing:

```bash
# Test the full LangGraph workflow directly
python __004__langgraph_more_nodes/full_workflow.py

# Test the FastAPI endpoints
python __005_fastapi/test_api.py

# Rebuild FAISS embeddings from Neo4j
python __003__create__information/__003__faiss_embedding.py

# Re-import extracted data into Neo4j
python __003__create__information/import_tcm_data.py
```

## Architecture

### Data Pipeline (one-time setup)

```
Raw web data (crawled CSVs)
  → __002__extract_information/   LLM-based entity/relation extraction → JSON
  → __003__create__information/   Neo4j import + FAISS vector index creation
```

The FAISS index (`nero4j_embedding_faiss.index`) and its ID-to-text pickle map are pre-built and committed.

### Query-Time Workflow (`__004__langgraph_more_nodes/`)

```
User Query
  → zhongyi_intent_node      (TCM or non-TCM?)
  ├─ Non-TCM → llm_direct_out_node
  └─ TCM →
       extract_entity_node   (extract entity names from query)
     → match_entity_node     (FAISS similarity → Neo4j catalog)
     → generate_cypher_node  (LLM generates Cypher)
     → check_cypher_node     (validate; up to 3 retries)
     → run_cypher_node       (execute on Neo4j)
     → generate_answer_node  (LLM formats final answer)
```

State flows through `AgentState` (TypedDict in `agent_state.py`). Each node is a standalone function in `nodes/`. The graph is assembled and compiled in `full_workflow.py`.

### Shared Utilities (`common/`)

| File | Purpose |
|---|---|
| `config.py` | `Config` class — loads `.env`, exposes all settings |
| `llm.py` | `get_llm()` — returns `ChatOpenAI` pointed at DeepSeek |
| `neo4j_manager.py` | `Neo4jClient` — wraps Cypher execution |
| `embedding_model.py` | Singleton `SentenceTransformer` loader |
| `path_utils.py` | Cross-platform path resolution for the FAISS index |

### Neo4j Schema

Defined in `__003__create__information/neo4j_metadata.json`. Node types: Disease, Symptom, Formula (方剂), Herb (中药), Effect, Source. The Cypher generator receives this schema as context.

## Key Design Decisions

- **LLM provider:** DeepSeek via OpenAI-compatible API — `langchain_openai.ChatOpenAI` with a custom `base_url`.
- **Cypher validation loop:** `check_cypher_node` retries generation up to 3 times; on persistent failure the workflow falls back to a direct LLM answer.
- **FAISS entity matching:** Before generating Cypher, entities are matched against the Neo4j catalog using dense retrieval to avoid hallucinated node names in queries.
- **Semantic transcription node** (`nodes/semantic_transcription_node.py`) — newly added, handles query rewriting/semantic normalization before entity extraction.
