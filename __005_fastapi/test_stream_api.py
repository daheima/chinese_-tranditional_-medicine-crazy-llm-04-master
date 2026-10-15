import requests
import json
import uuid
import time

BASE_URL = "http://localhost:8000"


def test_health():
    print("=" * 60)
    print("测试健康检查 GET /")
    print("=" * 60)
    resp = requests.get(f"{BASE_URL}/")
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.json()}")
    return resp.status_code == 200


def test_process(question: str, session_id: str = None):
    """测试同步接口 POST /process"""
    sid = session_id or str(uuid.uuid4())
    print(f"\n[同步接口] 问题: {question}")
    print(f"           session_id: {sid[:8]}...")
    resp = requests.post(
        f"{BASE_URL}/process",
        json={"input": question, "session_id": sid},
        timeout=120
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"回答: {result.get('output', '')[:200]}")
    else:
        print(f"❌ 失败: {resp.status_code} {resp.text}")
    return sid


def test_stream(question: str, session_id: str = None):
    """
    测试流式接口 POST /process_stream
    每行输出一个 JSON，type 字段：
      msg   —— 节点进度
      reply —— 最终回答
      error —— 出错
      done  —— 结束
    """
    sid = session_id or str(uuid.uuid4())
    print(f"\n{'='*60}")
    print(f"[流式接口] 问题: {question}")
    print(f"           session_id: {sid[:8]}...")
    print("=" * 60)

    try:
        with requests.post(
            f"{BASE_URL}/process_stream",
            json={"input": question, "session_id": sid},
            stream=True,
            timeout=180
        ) as resp:
            if resp.status_code != 200:
                print(f"❌ 请求失败: {resp.status_code} {resp.text}")
                return sid

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
                    print(f"  [进度] {content}")
                elif msg_type == "reply":
                    print(f"\n  [回答]\n{content}")
                elif msg_type == "error":
                    print(f"\n  [错误] {content}")
                elif msg_type == "done":
                    print("\n  [完成]")
                    break

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接服务器，请先启动 FastAPI 服务")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 异常: {e}")

    return sid


def test_multi_turn_memory():
    """测试多轮对话记忆：同一 session_id 连续提问，第二问依赖上文"""
    print("\n" + "=" * 60)
    print("多轮对话记忆测试（流式）")
    print("=" * 60)
    sid = str(uuid.uuid4())

    questions = [
        "桂枝汤的组成是什么？",
        "它的功效是什么？",   # "它" 指代桂枝汤，依赖上下文
    ]
    for q in questions:
        test_stream(q, session_id=sid)
        time.sleep(1)


def test_user_isolation():
    """测试用户隔离：两个不同 session_id 的对话互不干扰"""
    print("\n" + "=" * 60)
    print("用户隔离测试（流式）")
    print("=" * 60)
    sid_a = str(uuid.uuid4())
    sid_b = str(uuid.uuid4())

    print("\n--- 用户 A ---")
    test_stream("人参有什么功效？", session_id=sid_a)

    print("\n--- 用户 B（独立会话，不知道用户A问了什么）---")
    test_stream("今天天气怎么样？", session_id=sid_b)


if __name__ == "__main__":
    print("=" * 80)
    print("中医知识图谱问答系统 — 流式接口测试")
    print("=" * 80)
    print(f"服务地址: {BASE_URL}")

    print("\n等待服务就绪...")
    time.sleep(2)

    if not test_health():
        print("❌ 服务未启动，请先运行: cd __005_fastapi && python main.py")
        exit(1)

    # # 1. 单次中医问题（流式）
    # test_stream("拉肚子了该吃什么中药？")
    #
    # # 2. 单次非中医问题（流式，走 llm_direct_out 路径）
    # test_stream("今天天气怎么样？")

    # 3. 多轮记忆测试
    test_multi_turn_memory()

    # 4. 用户隔离测试
    test_user_isolation()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
