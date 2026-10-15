import os
from dotenv import load_dotenv

from path_utils import get_file_path

# load_dotenv()
#把环境变量加载起来
load_dotenv(get_file_path("common/.env"))

#Config是用来读取.env中的配置的.
#创建了一个config类
class Config:
    #init 方法是模型实例化时候执行的
    def __init__(self):
        # 大模型相关
        #self: 表示的是对象本身
        self.MODEL_API_KEY = os.getenv("MODEL_API_KEY")
        self.MODEL_BASE_URL = os.getenv("MODEL_BASE_URL")
        self.MODEL_NAME = os.getenv("MODEL_NAME")

        # neo4j相关
        self.NEO4J_URI = os.getenv("NEO4J_URI")
        self.NEO4J_USER = os.getenv("NEO4J_USER")
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
        self.TCM_METADATA = open(get_file_path(r"__003__create__information\neo4j_metadata.json"), "r",encoding="utf-8").read()
        self.EMBEDDING_MODEL_PATH=os.getenv("EMBEDDING_MODEL_PATH")
        self.JIMENG_AK = os.getenv("JIMENG_AK")
        self.JIMENG_SK = os.getenv("JIMENG_SK")
        self.DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
        # 添加历史数据获取的轮数
        self.history_num = 5




if __name__ == "__main__":
    # 类实例化 ,创建对象
    conf = Config()
    # print(conf.MODEL_API_KEY)
    # print(conf.MODEL_BASE_URL)
    # print(conf.MODEL_NAME)
    print(conf.TCM_METADATA)
    # print(conf.EMBEDDING_MODEL_PATH)