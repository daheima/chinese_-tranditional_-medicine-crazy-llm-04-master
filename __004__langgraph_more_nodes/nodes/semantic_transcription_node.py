from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from __004__langgraph_more_nodes.agent_state import AgentState
from common.llm import my_llm
from common.config import Config
from __005_fastapi.msg_queue_manager import msg_queue_manager

conf = Config()


def semantic_transcription_node(state: AgentState, config: RunnableConfig = None) -> dict:
    """
    语义转写节点：结合历史对话，将当前用户输入转写为语义明确的问题。
    """
    user_id = config.get("configurable", {}).get("thread_id", "default") if config else "default"
    msg_queue_manager.put_msg_content(user_id, "🔄 正在理解对话上下文，转写语义...")

    print("开始生成语义转写...")
    user_input = state["input"]
    history_messages = state.get("history_messages", [])
    print(f"历史消息：{history_messages}")

    recent_history = history_messages[-(conf.history_num):]

    prompt = f"""
你是一名语言理解专家，负责将用户输入转写为清晰、简洁、语义明确的问题或意图表达。
你需要基于以下上下文（最近6轮对话），分析用户真正想表达的意思。
请不要编造不存在的信息，也不要直接回答问题，只需输出语义转写后的句子。

【历史对话】
{recent_history}

【当前用户输入】
{user_input}

请输出：
1. 一句自然语言，清楚表达用户当前真正的问题或意图；
2. 不要包含解释性文字；
3. 如果用户输入含糊不清，请基于上下文合理补全语义；
4. 输出格式：直接输出转写结果，无需加前缀。
"""

    response = my_llm.invoke([HumanMessage(content=prompt)])
    result = response.content.strip()

    print(f"完成生成语义转写：{result}")
    msg_queue_manager.put_msg_content(user_id, f"🔄 语义转写完成：{result}")

    return {
        "input_semantic_trans": result,
        "history_messages": [{"role": "user", "content": user_input}]
    }
