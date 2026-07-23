# 定义一个函数_fn_tool，接收名称、描述、属性和必需字段列表，返回一个字典
def _fn_tool(
    name: str, description: str, properties: dict, required: list[str]
) -> dict:
    # 返回一个包含类型和函数信息的字典
    return {
        # 设定类型为'function'
        "type": "function",
        # 定义函数的具体内容
        "function": {
            # 函数名称
            "name": name,
            # 函数描述
            "description": description,
            # 参数设置，定义为一个对象，包含属性和必需字段
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


# 定义一个工具列表，包含一个通过_fn_tool函数生成的工具：bash命令执行
tools = [
    _fn_tool(
        "bash",
        "执行一条 shell 命令。",
        {"command": {"type": "string"}},
        ["command"],
    ),
    _fn_tool(
        "read_file",
        "读取文件内容。",
        {"path": {"type": "string"}, "limit": {"type": "integer"}},
        ["path", "limit"],
    ),
    _fn_tool(
        "write_file",
        "写入文件内容。",
        {
            "path": {"type": "string"},
            "old_content": {"type": "string"},
            "new_content": {"type": "string"},
        },
        ["path", "old_content", "new_content"],
    ),
    # 定义使用 glob 模式查找文件的工具，参数为 pattern（字符串类型）
    _fn_tool(
        "glob",
        "按 glob 模式查找文件",
        {"pattern": {"type": "string"}},
        ["pattern"],
    ),
    _fn_tool(
        "todo_write",  # 名称
        "创建并管理当前编码会话的任务列表。",  # 描述
        {
            "todos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},  # 子任务的内容
                        "status": {  # 子任务的状态
                            "type": "string",
                            "enum": [
                                "pending",  # 待执行
                                "in_progress",  # 进行中
                                "completed",  # 已完成
                            ],
                        },
                    },
                    "required": ["content", "status"],
                },
            }
        },
        ["todos"],
    ),
]
