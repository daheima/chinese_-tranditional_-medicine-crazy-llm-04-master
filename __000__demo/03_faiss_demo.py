# encoding: utf-8
import sys

import faiss
import numpy as np

# 1. 构造样本文本（假设是中医症状）
texts = [
    "腹泻",
    "夜间盗汗",
    "手足心热",
    "腰膝酸软",
    "头晕耳鸣",
    "胃脘不适",
    "咳嗽有痰",
    "气短乏力",
    "心烦易怒",
    "失眠多梦"
]

# 2. 加载一个中文向量模型（可换为 bge 或其他模型）
model = SentenceTransformer(r'E:\BaiduNetdiskDownload\阶段13 知识图谱项目\5月24日-知识图谱项目\05_扩展\模型权重\bge-large-zh-v1.5')

# 3. 向量化处理 FAISS 只认 numpy 数组 所以要 convert_to_numpy=True
embeddings = model.encode(texts, convert_to_numpy=True)

# 4. 构建 Faiss 索引（L2 距离）
# print(f"embeddings.shape:{embeddings.shape}")
# sys.exit(-1)
dimension = embeddings.shape[1] #生成的向量的维度
index = faiss.IndexFlatL2(dimension)   # 也可以用 IndexFlatIP 做余弦相似度
index.add(embeddings)                  # 添加向量到索引中

# 5. 输入查询语句
query = "肚子疼"

# 6. 向量化查询文本
query_vec = model.encode([query], convert_to_numpy=True)
print(f"query_vec.shape:{query_vec.shape}")
# # 7. Faiss 查询最相近的5条
top_k = 5
distances, indices = index.search(query_vec, top_k)

# 8. 打印结果
print("🔍 查询文本：", query)
print("\n📋 最相似的结果：")
for i, idx in enumerate(indices[0]):
    print(f"{i+1}. {texts[idx]} (欧式距离: {distances[0][i]:.4f})")