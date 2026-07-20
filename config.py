import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

# 定义默认的最大token数
DEFAULT_MAX_TOKENS = 8000


print(OPENAI_BASE_URL, OPENAI_API_KEY, MODEL_ID)


class Config:
    def __init__(self):
        self.OPENAI_BASE_URL = OPENAI_BASE_URL
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.MODEL_ID = MODEL_ID
        self.DEFAULT_MAX_TOKENS = DEFAULT_MAX_TOKENS
