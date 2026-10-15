import os
from typing import List

import torch

from config import Config

# 尝试导入sentence-transformers库
# 如果没有安装，可以使用pip install sentence-transformers
from sentence_transformers import SentenceTransformer
# 如果你们的torch 装的是cpu版本的，就没法使用gpu
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
class EmbeddingModel:
    """嵌入模型类，用于将文本转换为向量表示"""

    def __init__(self):
        """初始化嵌入模型"""
        config = Config()

        # 如果配置了模型路径，使用配置的路径，否则使用默认模型
        if config.EMBEDDING_MODEL_PATH and os.path.exists(config.EMBEDDING_MODEL_PATH):
            self.model = SentenceTransformer(config.EMBEDDING_MODEL_PATH,device=device)
        else:
            # 使用默认的中文预训练模型
            self.model = SentenceTransformer(
                r'E:\中医知识图谱备课02\05_扩展\模型权重\bge-large-zh-v1.5',device=device)

    def encode(self, texts: List[str], convert_to_numpy=False, normalize_embeddings=False) -> List[List[float]]:
        """
        将文本列表转换为向量表示

        Args:
            texts: 文本列表
            convert_to_numpy: 是否将结果转换为numpy数组
            normalize_embeddings: 是否对向量进行归一化

        Returns:
            向量列表或numpy数组，每个向量对应一个文本
        """
        return self.model.encode(texts, convert_to_numpy=convert_to_numpy, normalize_embeddings=normalize_embeddings)


# 创建全局的嵌入模型对象
embedding_model = EmbeddingModel()
print(embedding_model)
print(embedding_model.encode(["你好"]))
# 打印模型维度
print(embedding_model.model.get_embedding_dimension())
# print(embedding_model.encode(["你好", "世界"]))
