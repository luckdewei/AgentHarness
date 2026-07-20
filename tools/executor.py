import inspect
from tools.handlers import tool_handlers


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
