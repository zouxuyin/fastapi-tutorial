#####运行程序
# cd D:\PycharmProjects\PythonProject\fastapi-tutorial\tutorial> 
# & "D:\PycharmProjects\PythonProject\fastapi-tutorial\.venv\Scripts\python.exe" "deepseek.py"

###---------------------------------案例1-----------------------------------------------


import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
# 将env文件中的变量加载为环境变量
#override=True：表示.env优先
load_dotenv(override=True)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("deepseek_key")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
model = ChatDeepSeek(
    api_key=DEEPSEEK_API_KEY,
    api_base=DEEPSEEK_BASE_URL,
    model_name="deepseek-v4-flash"
)
print(model.invoke("你好"))


###---------------------------------案例2-----------------------------------------------
# import os
# from dotenv import load_dotenv
# from langchain_deepseek import ChatDeepSeek
# from openai import APIStatusError

# # override=True 确保当前文件所在目录的 .env 优先
# load_dotenv(override=True)

# # 兼容 .env 中旧命名和新命名
# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("deepseek_key")
# DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"

# if not DEEPSEEK_API_KEY:
#     raise ValueError("未找到 DEEPSEEK_API_KEY，请在 tutorial/.env 中配置有效的 DeepSeek API Key")

# model = ChatDeepSeek(
#     model="deepseek-chat",
#     api_key=DEEPSEEK_API_KEY,
#     base_url=DEEPSEEK_BASE_URL,
# )

# try:
#     print(model.invoke("你好，用一句话回答"))
# except APIStatusError as error:
#     if error.status_code == 402 or "Insufficient Balance" in str(error):
#         print("DeepSeek API 调用失败：账号余额不足，请充值或更换有效的 API Key。")
#         raise SystemExit(1) from error
#     raise   

###---------------------------------案例3-----------------------------------------------



# from langchain.chat_models import init_chat_model
# from dotenv import load_dotenv
# import os
# from openai import APIStatusError
# from rich import print as rprint
# # 从.env文件中加载环境变量
# load_dotenv(override=True)
# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("deepseek_key")
# DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
# # 1. 初始化模型
# model = init_chat_model(
#     model="deepseek-v4-flash",
#     model_provider="deepseek",
#     api_key=DEEPSEEK_API_KEY,
#     base_url=DEEPSEEK_BASE_URL,
#     temperature=0.2,
#     max_tokens=500,
#     # 指定可调整参数
#     configurable_fields=("model", "model_provider", "temperature",
# "max_tokens"),
# )
# # 2. 准备 config 字典
# config = {
#     "run_name": "joke_generation",  # 在LangSmith中这次运行会显示为
# "joke_generation"
#     "tags": ["my_tag1", "my_tag2"],  # 打上标签便于分类查找
#     "metadata": {
#         "user_id": "shkstart",     # 记录用户ID
#         "session_id": "sess_123"   # 记录会话ID
#     },
#     "configurable": {
#         "model": "deepseek-v4-pro",  # 配置模型参数
#         "model_provider": "openai",  # 配置模型提供商参数
#         "temperature": 0.7,  # 配置温度参数
#         "max_tokens": 1000  # 配置最大令牌数
#     }
# }
# # 3. 调用模型并传入config
# try:
#     response = model.invoke(
#         "1 + 2 = ？",
#         config=config
#     )
#     rprint(response)
# except APIStatusError as error:
#     if error.status_code == 402 or "Insufficient Balance" in str(error):
#         print("DeepSeek API 调用失败：账号余额不足，请充值或更换有效的 API Key。")
#         raise SystemExit(1) from error
#     raise   