from langchain_core.runnables import RunnableConfig
from __004__langgraph_more_nodes.agent_state import AgentState
from common.neo4j_manager import neo4j_client
from __005_fastapi.msg_queue_manager import msg_queue_manager


def check_cypher_node(state: AgentState, config: RunnableConfig = None) -> AgentState:
    """
    检查Cypher语句是否合法
    - 输入：state["cypher_query"]
    - 输出：state["is_all_validate_cypher"]
    - 使用Neo4j的EXPLAIN命令验证语法
    """
    user_id = config.get("configurable", {}).get("thread_id", "default") if config else "default"
    msg_queue_manager.put_msg_content(user_id, "✅ 正在验证 Cypher 语法...")

    print("开始检查Cypher语句")

    cypher_list = state.get("cypher_query", [])

    if not cypher_list:
        print("  无Cypher语句需要检查")
        state["is_all_validate_cypher"] = True
        return state

    print(f"  共有 {len(cypher_list)} 条Cypher语句需要检查")

    all_valid = True
    for i, cypher in enumerate(cypher_list, 1):
        print(f"  检查语句 {i}: {cypher[:60]}...")
        try:
            neo4j_client.run_cypher(f"EXPLAIN {cypher}")
            print(f"    ✅ 合法")
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ 不合法: {error_msg[:80]}")
            all_valid = False

    state["is_all_validate_cypher"] = all_valid

    if all_valid:
        print(f"  ✅ 全部 {len(cypher_list)} 条Cypher语句合法")
        msg_queue_manager.put_msg_content(user_id, f"✅ Cypher 验证通过，共 {len(cypher_list)} 条")
    else:
        print(f"  ❌ 存在不合法的Cypher语句")
        msg_queue_manager.put_msg_content(user_id, "❌ Cypher 验证未通过，重新生成...")

    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 检查Cypher节点测试")
    print("=" * 60)

    test_cases = [
        {
            "cypher_query": [
                "MATCH (d:Disease {name: '感冒'})-[:HAS_SYMPTOM]->(s:Symptom) RETURN d.name AS 疾病, collect(s.name) AS 症状 LIMIT 5",
                "MATCH (h:Herb)-[:HAS_EFFECT]->(e:Effect) RETURN h.name AS 中药, e.name AS 功效 LIMIT 5"
            ]
        },
        {
            "cypher_query": [
                "MATCH (n) RETURN n",
                "INVALID CYPHER SYNTAX"
            ]
        },
        {
            "cypher_query": []
        },
    ]

    for i, test_state in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}")
        print("=" * 60)

        result = check_cypher_node(test_state)

        print(f"\n检查结果: is_all_validate_cypher = {result['is_all_validate_cypher']}")