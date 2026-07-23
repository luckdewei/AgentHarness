# 定义一个包含提示语片段的字典，键为'identity'
PROMPT_SECTIONS = {
    # 'identity'键对应一个多行字符串，作为智能体的系统身份提示
    "identity": (
        f"你是一个编程 Agent。直接行动，不要解释"
        f"直接调用工具完成任务。危险操作的权限确认由系统自动处理，你无需在对话中重复询问用户"
        f"开始多步骤任务前，先用todo_write规划步骤;执行过程中及时更新状态"
    )
}


# 定义一个函数，返回系统提示语
def get_system_prompt() -> str:
    # 返回字典中'identity'键对应的提示语
    return PROMPT_SECTIONS["identity"]
