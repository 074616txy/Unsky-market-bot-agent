import os
from dotenv import load_dotenv

# 完成配置读取，这里现以运行一个最小agent为目的
# 加载env的全局文件，有这个可以在全局调用LLM
load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL_ID")