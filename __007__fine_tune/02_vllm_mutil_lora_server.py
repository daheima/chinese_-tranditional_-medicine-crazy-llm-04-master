import subprocess
import sys
import os

def main():
    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",

        # base model
        "--model", "Qwen/Qwen2.5-1.5B-Instruct/", #从modelscope上下载下来的模型路径

        # server
        "--host", "0.0.0.0",
        "--port", "8000",

        # precision & memory
        "--dtype", "float16",
        "--gpu-memory-utilization", "0.8",
        "--max-model-len", "8192",

        # ===== LoRA 关键参数 =====
        "--enable-lora",
        "--lora-modules",
        "tcm=/workspace/LLaMA-Factory/saves/Qwen2.5-1.5B-Instruct/lora/train_2025-12-25-04-59-03",   # 中医
        "law=/workspace/LLaMA-Factory/saves/Qwen2.5-1.5B-Instruct/lora/train_2026-06-07-07-26-29",   # 法律
        "cs=/workspace/LLaMA-Factory/saves/Qwen2.5-1.5B-Instruct/lora/train_2026-06-07-07-26-29",     # 客服
        "--max-loras", "3",
        "--max-lora-rank", "8",
    ]

    print("Starting vLLM server with multiple LoRA adapters...")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
