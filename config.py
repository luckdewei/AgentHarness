import os
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

# 定义默认的最大token数
DEFAULT_MAX_TOKENS = 8000

# 定义工作目录为当前目录
WORKDIR = Path.cwd()

# 设置默认编码为utf-8
if os.name == "nt":
    os.system("chcp 65001 >nul")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TEXT_ENCODING = "utf-8"

print(OPENAI_BASE_URL, OPENAI_API_KEY, MODEL_ID)


class Config:
    def __init__(self):
        self.WORKDIR = WORKDIR
        self.TEXT_ENCODING = TEXT_ENCODING
        self.OPENAI_BASE_URL = OPENAI_BASE_URL
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.MODEL_ID = MODEL_ID
        self.DEFAULT_MAX_TOKENS = DEFAULT_MAX_TOKENS
