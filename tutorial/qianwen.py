# 启动命令：
# cd D:\PycharmProjects\PythonProject\fastapi-tutorial\tutorial
# & "D:\PycharmProjects\PythonProject\fastapi-tutorial\.venv\Scripts\python.exe" "qianwen.py"

#
import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi

# override=True 确保当前文件所在目录的 .env 优先
load_dotenv(override=True)

# 兼容 .env 中旧命名和新命名
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY") or os.getenv("qianwen_key")

if not DASHSCOPE_API_KEY:
    raise ValueError("未找到 DASHSCOPE_API_KEY，请在 tutorial/.env 中配置有效的 Qwen API Key")

tongyi_llm = ChatTongyi(
    api_key=DASHSCOPE_API_KEY,
    model="qwen-plus",
)

print(tongyi_llm.invoke("请介绍一下你自己,并讲解一下agent"))