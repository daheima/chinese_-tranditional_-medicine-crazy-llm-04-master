import streamlit as st
import requests
import json
import uuid

st.set_page_config(
    page_title="中医知识图谱问答系统（流式）",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

STREAM_API_URL = "http://localhost:8000/process_stream"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# chat_history 里每条记录：{"role": "user"|"assistant", "content": str, "thinking": list[str]}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.header("⚙️ 设置")
    st.info("API地址: http://localhost:8000")
    st.caption(f"会话ID: {st.session_state.session_id[:8]}...")
    st.markdown("---")
    st.markdown("### 📚 使用示例")
    st.markdown("1. 人参有什么功效？")
    st.markdown("2. 桂枝汤的组成是什么？")
    st.markdown("3. 感冒了吃什么药？")
    st.markdown("---")
    if st.button("🗑️ 新建会话", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

st.title("🏥 中医知识图谱问答系统")
st.caption("流式输出 · 实时推理进度")
st.markdown("---")

# ── 渲染历史对话 ──────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            thinking = msg.get("thinking", [])
            if thinking:
                with st.expander("查看推理过程", expanded=False):
                    for step in thinking:
                        st.caption(step)
            st.markdown(msg["content"])
        else:
            st.markdown(msg["content"])

# ── 输入框 ────────────────────────────────────────────────────
user_input = st.chat_input("请输入您的问题，例如：拉肚子该吃什么中药？")

if user_input:
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input, "thinking": []})

    # 显示助手消息（流式）
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()   # 展示实时推理进度
        answer_placeholder = st.empty()     # 展示最终回答

        thinking_steps = []
        final_answer = ""
        has_error = False

        try:
            with requests.post(
                STREAM_API_URL,
                json={"input": user_input, "session_id": st.session_state.session_id},
                stream=True,
                timeout=180,
            ) as resp:
                if resp.status_code != 200:
                    st.error(f"请求失败，状态码: {resp.status_code}")
                    has_error = True
                else:
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        try:
                            msg = json.loads(line.decode("utf-8"))
                        except json.JSONDecodeError:
                            continue

                        msg_type = msg.get("type")
                        content = msg.get("msg", "")

                        if msg_type == "msg":
                            # 实时追加推理步骤，用 info 框展示
                            thinking_steps.append(content)
                            thinking_placeholder.info("  \n".join(thinking_steps))

                        elif msg_type == "reply":
                            final_answer = content
                            # 先把回答显示出来，推理框还在
                            answer_placeholder.markdown(final_answer)

                        elif msg_type == "error":
                            st.error(content)
                            has_error = True
                            break

                        elif msg_type == "done":
                            # 流结束：把推理过程收进折叠框，回答保持展开
                            thinking_placeholder.empty()
                            answer_placeholder.empty()
                            if thinking_steps:
                                with st.expander("查看推理过程", expanded=False):
                                    for step in thinking_steps:
                                        st.caption(step)
                            st.markdown(final_answer)
                            break

        except requests.exceptions.ConnectionError:
            st.error("无法连接到服务器，请确保 FastAPI 服务已启动！")
            has_error = True
        except requests.exceptions.Timeout:
            st.error("请求超时，请稍后重试")
            has_error = True
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            has_error = True

        # 只有成功拿到回答才写入历史
        if not has_error and final_answer:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": final_answer,
                "thinking": thinking_steps
            })
