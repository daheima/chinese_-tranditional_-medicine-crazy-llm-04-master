import streamlit as st
import requests
import uuid

st.set_page_config(
    page_title="中医知识图谱问答系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = "http://localhost:8000/process"

# 每个浏览器 Tab 启动时生成一次 session_id，存在 session_state 里
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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
        # 重置 session_id，LangGraph 会为新 thread_id 创建独立记忆
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

st.title("🏥 中医知识图谱问答系统")
st.markdown("---")

# 渲染历史对话
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
user_input = st.chat_input("请输入您的问题，例如：拉肚子该吃什么中药？")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("正在思考中..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"input": user_input, "session_id": st.session_state.session_id},
                    timeout=120
                )
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("output", "")
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"请求失败，状态码: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("无法连接到服务器，请确保FastAPI服务已启动！")
            except requests.exceptions.Timeout:
                st.error("请求超时，请稍后重试")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
