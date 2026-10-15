import asyncio
import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from typing import Optional
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __004__langgraph_more_nodes.full_workflow import build_graph
from __005_fastapi.msg_queue_manager import msg_queue_manager

app = FastAPI(title="中医知识图谱问答系统", description="基于FastAPI和LangGraph的中医知识图谱智能问答系统")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局唯一 workflow 实例，InMemorySaver 按 thread_id 隔离每个用户的记忆
_memory = InMemorySaver()
_graph = build_graph().compile(_memory)


class QueryRequest(BaseModel):
    input: str
    session_id: Optional[str] = None  # 客户端传入用于用户隔离，不传则使用 "default"


class QueryResponse(BaseModel):
    input: str
    output: str
    session_id: str


@app.get("/")
async def root():
    return {"status": "ok", "message": "中医知识图谱问答系统服务运行正常"}


@app.post("/process", response_model=QueryResponse)
async def process(request: QueryRequest):
    """
    同步问答接口。每个用户通过 session_id 隔离各自的对话记忆。
    """
    input_text = request.input
    session_id = request.session_id or "default"

    if not input_text:
        return JSONResponse(
            content={"input": "", "output": "请输入问题！", "session_id": session_id},
            status_code=200
        )

    logger.info(f"[session={session_id}] 收到查询: {input_text[:50]}...")

    try:
        config = RunnableConfig(configurable={"thread_id": session_id})
        result = _graph.invoke({"input": input_text}, config)

        output = result.get("output", "") or result.get("direct_out", "系统出错了，请重试！")
        logger.info(f"[session={session_id}] 查询完成，输出长度: {len(output)}")

        return {"input": input_text, "output": output, "session_id": session_id}

    except Exception as e:
        logger.error(f"[session={session_id}] 查询处理失败: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"input": input_text, "output": "系统出错了，请重试！", "session_id": session_id},
            status_code=500
        )


async def generate_data(input_text: str, user_id: str):
    """
    流式输出生成器。
    将 LangGraph workflow 放入线程池运行，各节点通过 msg_queue_manager 往队列里推消息。
    消息格式：
      {"type": "msg",   "msg": "进度文本"}   —— 节点执行进度
      {"type": "reply", "msg": "最终回答"}   —— 最终回答内容
      {"type": "error", "msg": "错误信息"}   —— 执行出错
      {"type": "done",  "msg": ""}           —— 流结束
    """
    # 注入当前事件循环，节点在线程中通过 call_soon_threadsafe 推消息时需要它
    msg_queue_manager.set_loop(asyncio.get_running_loop())
    msg_queue_manager.get_msg_queue(user_id)  # 提前建好队列，避免竞争

    async def run_workflow():
        try:
            config = RunnableConfig(configurable={"thread_id": user_id})
            # _graph.invoke 是同步调用，放线程池里跑，不阻塞事件循环
            #这就是生产者 调用了_graph.invoke ,每个节点都往异步队列中写数据
            await asyncio.to_thread(_graph.invoke, {"input": input_text}, config)
        except Exception as e:
            logger.error(f"[session={user_id}] 流式工作流出错: {str(e)}", exc_info=True)
            msg_queue_manager.put_error_content(user_id, f"系统出错: {str(e)}")
        finally:
            msg_queue_manager.put_done_content(user_id)

    asyncio.create_task(run_workflow())

    #这就是消费者
    while True:
        msg = await msg_queue_manager.get_msg_queue(user_id).get()
        yield json.dumps(msg, ensure_ascii=False) + "\n"
        if msg.get("type") in ("done", "error"):
            msg_queue_manager.del_msg_queue(user_id)
            break


@app.post("/process_stream")
async def process_stream(request: QueryRequest):
    """
    流式问答接口。
    每行返回一个 JSON 对象，type 字段区分消息类型（msg/reply/error/done）。
    """
    input_text = request.input
    user_id = request.session_id or "default"

    if not input_text:
        async def empty():
            yield json.dumps({"type": "error", "msg": "请输入问题！"}, ensure_ascii=False) + "\n"
            yield json.dumps({"type": "done", "msg": ""}, ensure_ascii=False) + "\n"
        return StreamingResponse(empty(), media_type="text/plain")

    logger.info(f"[session={user_id}] 收到流式查询: {input_text[:50]}...")
    return StreamingResponse(generate_data(input_text, user_id), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    logger.info("启动中医知识图谱问答系统服务...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
