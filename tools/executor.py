import inspect
import json
from config import Config
from hooks import trigger_hooks
from prompt import SUB_SYSTEM
from tools.handlers import tool_handlers
from tools.schema import base_tools, tools
from llm import LLM
from utils import assistant_message_dict, extract_text

llm = LLM()
config = Config()


def execute_tool(tool_name, tool_args) -> str:
    """
    执行工具
    """
    # 根据工具名称执行工具
    handler = tool_handlers.get(tool_name)

    if not handler:
        return f"工具不存在: {tool_name}"

    # 获取处理函数的参数签名
    sig = inspect.signature(handler)
    # 从输入参数中筛选出处理函数所需的有效参数
    valid = {k: v for k, v in tool_args.items() if k in sig.parameters}
    # 调用处理函数并返回结果
    return handler(**valid)


# 定义运行子 Agent 的函数，参数为描述字符串，返回字符串类型
def run_spawn_subagent(description: str) -> str:
    """
    运行子 Agent
    """
    # 打印子 Agent 已启动的信息
    print(f"\n\x1b[35m[子 Agent 已启动]\x1b[0m")
    # 初始化消息列表，用户以描述作为第一条消息
    messages = [{"role": "user", "content": description}]
    # 最多进行30轮消息交互
    for _ in range(30):
        response = llm.client.chat.completions.create(
            model=config.MODEL_ID,
            messages=[{"role": "system", "content": SUB_SYSTEM}, *messages],
            tools=base_tools,
            max_tokens=config.DEFAULT_MAX_TOKENS,
        )
        # 取出assistant回复内容
        assistant = response.choices[0].message
        # 将assistant回复格式化为dict并加入消息历史
        messages.append(assistant_message_dict(assistant))
        # 如果assistant没有工具调用，跳出循环
        if not assistant.tool_calls:
            break
        # 遍历assistant需要调用的所有工具
        for tool_call in assistant.tool_calls:
            # 获取工具名称
            name = tool_call.function.name
            # 获取调用的参数，JSON格式
            args = json.loads(tool_call.function.arguments or "{}")
            # 调用PreToolUse钩子判断是否被阻止
            blocked = trigger_hooks("PreToolUse", name, args)
            # 如果被拒绝了，则加入一个tool的回复，内容为阻止的理由
            if blocked:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(blocked),
                    }
                )
                continue
            # 执行工具，如果此工具未注册，则提示未知工具
            output = (
                execute_tool(name, args)
                if name in tool_handlers
                else f"未知工具:{name}"
            )
            trigger_hooks("PostToolUse", name, output)
            print(f"\x1b[90m [SubAgent] {name}: {str(output)[:100]}  \x1b[0m")
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": output}
            )
    # 从所有的消息中最后一条内容中提取文本为最终的结果
    result = extract_text(messages[-1].get("content"))
    # 如果没有提取到，反向查找assistant角色消息并提取结果
    if not result:
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                result = extract_text(msg.get("content"))
                if result:
                    break
    print(f"\x1b[35m [SubAgent]完成任务  \x1b[0m")
    return result


tool_handlers["spawn_subagent"] = run_spawn_subagent
