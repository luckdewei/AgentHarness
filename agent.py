import json
from config import Config
from llm import LLM
from prompt import get_system_prompt
from utils import assistant_message_dict


def agent_loop(messages: list):
    config = Config()
    llm_client = LLM()
    max_tokens = config.DEFAULT_MAX_TOKENS
    model = config.MODEL_ID
    while True:
        # 获取系统提示词
        system = get_system_prompt()
        # 调用大模型获取回复
        response = llm_client.call_llm(system, messages, max_tokens, model)
        # 获取助手返回的消息
        choice = response.choices[0]
        assistant = choice.message
        # 消耗的token在choice.usage
        # 将助手的回复以字典的形式添加到消息列表
        messages.append(assistant_message_dict(assistant))
        # 如果助手没有工具调用，则终止循环
        if not assistant.tool_calls:
            return
        # 如果助手有工具调用，则调用工具
        for tool_call in assistant.tool_calls:
            # 获取工具名称
            tool_name = tool_call.function.name
            # 获取工具参数
            # 获取解析工具参数
            args = json.loads(tool_call.function.arguments or "{}")
            # 调用工具
