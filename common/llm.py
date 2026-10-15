from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from config import Config
import os
#加载配置
conf = Config()


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"]
# LangSmith 项目名称，默认 default
os.environ["LANGCHAIN_PROJECT"] = "default"
#利用ChatOpenAI 创建大模型对象
# ============ 配置llm区域 ============
my_llm = ChatOpenAI(
    api_key=conf.MODEL_API_KEY,
    base_url=conf.MODEL_BASE_URL,
    model=conf.MODEL_NAME
)

if __name__ == '__main__':
    # 构造对话消
    stard_name = "腹泻"
    #有元数据
    messages = [
        HumanMessage(content=f"你是一个cypher语句生成专家，用户提问是'我拉肚子了要吃什么药？'，neo4j的元数据是{conf.TCM_METADATA}, 抽取出来的标准实体是{stard_name},请帮我生成cpyher语句,不要包含换行符什么的东西，就直接给我一条直接可用的cypher语句，请勿返回其他内容")
    ]
    # #没有 元数据
    # #MATCH (d:Disease {name:'腹泻'})<-[:TREATS]-(m:Medicine) RETURN m.name
    # messages = [
    #     HumanMessage(
    #         content=f"你是一个cypher语句生成专家，用户提问是'我拉肚子了要吃什么药？'，, 抽取出来的标准实体是{stard_name},请帮我生成cpyher语句,不要包含换行符什么的东西，就直接给我一条直接可用的cypher语句，请勿返回其他内容")
    # ]
    # messages = [
    #     HumanMessage(
    #         content=f"你好")
    # ]
    # 调用模型
    response = my_llm.invoke(messages)
    print(response)