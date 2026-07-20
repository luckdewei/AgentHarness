from config import Config
import openai
from langsmith.wrappers import wrap_openai

from tools.schema import tools

client = wrap_openai(openai.Client())


class LLM:
    def __init__(self):
        config = Config()
        self.client = wrap_openai(
            openai.Client(
                base_url=config.OPENAI_BASE_URL,
                api_key=config.OPENAI_API_KEY,
            )
        )

    def call_llm(self, system: str, messages: list, max_tokens: int, model: str):
        """
        调用大模型获取回复
        :param system: 系统提示词
        :param messages: 消息列表
        :param max_tokens: 最大允许的token数
        :param model: 模型ID
        :return: 大模型回复
        """
        return self.client.chat.completions.create(
            model=model,
            # 将系统提示和传入的消息列表组合成messages参数
            messages=[{"role": "system", "content": system}, *messages],
            # 传入工具集合
            tools=tools,
            # 传入最大允许的token数
            max_tokens=max_tokens,
        )
