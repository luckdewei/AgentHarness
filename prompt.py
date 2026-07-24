# 定义一个包含提示语片段的字典，键为'identity'
from config import WORKDIR
from skills import SKILL_REGISTRY

PROMPT_SECTIONS = {
    # 'identity'键对应一个多行字符串，作为智能体的系统身份提示
    "identity": (
        f"你是一个编程 Agent。直接行动，不要解释"
        f"如果在 Windows cmd 环境下执行任务，请使用 cmd 命令完成任务"
        f"直接调用工具完成任务。危险操作的权限确认由系统自动处理，你无需在对话中重复询问用户"
        f"开始多步骤任务前，先用todo_write规划步骤;执行过程中及时更新状态"
        f"遇到复杂子问题时，使用 spawn_subagent 工具派生子Agent"
    ),
    "workspace": f"工作目录：{WORKDIR}",
    "skill": "需要完整技术说明时，使用 load_skill 加载相关文档",
}


# 定义函数，将各段拼接成完整的系统提示，skills 为技能描述字符串
def _assemble_system_prompt(skills: str) -> str:
    # 初始化包含基本身份与工作目录的列表 sections
    sections = [PROMPT_SECTIONS["identity"], PROMPT_SECTIONS["workspace"]]
    # 若传入的技能描述非空，则将其与技能说明段落加入 sections
    if skills:
        sections.append(f"可用技能:\n{skills}")
        sections.append(PROMPT_SECTIONS["skill"])
    # 用两个换行符拼接所有片段并返回完整的系统提示
    return "\n\n".join(sections)


# 定义一个私有函数，生成所有注册技能的简介文本
def _skills_text() -> str:
    # 若技能注册表为空则返回空字符串
    if not SKILL_REGISTRY:
        return ""
    # 遍历技能注册表，为每项技能生成 markdown 列表条目并拼接返回
    return "\n".join(
        f"- **{s['name']}**: {s['description']}" for s in SKILL_REGISTRY.values()
    )


# 定义一个函数，返回系统提示语
def get_system_prompt() -> str:
    # 内部调用技能文本拼接及总装配函数
    return _assemble_system_prompt(_skills_text())


# 定义子Agent的系统提示语
SUB_SYSTEM = (
    f"你是一个位于工作目录 {WORKDIR} 的编程 Agent，直接行动，不要解释"
    "如果在 Windows cmd 环境下执行任务。使用 cmd 命令完成任务"
    "完成分配给你的任务，然后返回简洁摘要。不要继续委派"
)
