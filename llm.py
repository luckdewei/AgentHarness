from config import Config
from openai import OpenAI


class LLM:
    def __init__(self):
        self.client = OpenAI(
            base_url=Config.OPENAI_BASE_URL,
            api_key=Config.OPENAI_API_KEY,
        )

    def call_llm(self, system: str, messages: list, max_tokens: int, model: str):
        return self.client.chat.completions.create(
            model=model,
            # 将系统提示和传入的消息列表组合成messages参数
            messages=[{"role": "system", "content": system}, *messages],
            # 传入工具集合
            tools=[],
            # 传入最大允许的token数
            max_tokens=max_tokens,
        )
