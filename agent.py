import json

from langsmith import traceable
from config import Config
from llm import LLM
from hooks import trigger_hooks
from prompt import get_system_prompt
from tools.executor import execute_tool
from utils import assistant_message_dict


@traceable(name="agent_loop")
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
            # 调用trigger_hooks函数，触发名为Stop的钩子，传入当前的消息列表
            force = trigger_hooks("Stop", messages)
            # 如果force有值说明活没干完，也就是hook返回了需要进一步处理的信息
            if force:
                # 如果有值，则将其作为用户角色的消息添加到消息列表中
                messages.append({"role": "user", "content": force})
                # 继续while循环，重新进入 agent loop的流程
                continue
            return
        # 如果助手有工具调用，则调用工具
        for tool_call in assistant.tool_calls:
            # 获取工具名称
            tool_name = tool_call.function.name
            # 获取工具参数
            # 获取解析工具参数
            args = json.loads(tool_call.function.arguments or "{}")
            # 打印工具名称（蓝色高亮）
            print(
                f"\x1b[36m> {tool_name} {json.dumps(args, ensure_ascii=False)}\x1b[0m"
            )

            # 检查工具执行权限
            # 触发PreToolUse这个钩子，判断是否允许工具执行
            blocked = trigger_hooks("PreToolUse", tool_name, args)
            # 只要有一个钩子函数返回一个非None的值，后面的钩子就不走了，
            if blocked:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": blocked + ".",
                    }
                )
                # 跳过本次工具调用，继续下一个
                continue
            # 执行工具，获取输出结果
            output = execute_tool(tool_name, args)
            # 把工具执行结果以特定格式加入消息列表
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": output}
            )
