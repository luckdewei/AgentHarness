# 从config模块导入工作目录变量
import json
from config import WORKDIR

# 定义一个钩子字典，每个事件对应一个回调函数列表
HOOKS = {"UserPromptSubmit": [], "PreToolUse": [], "PostToolUse": [], "Stop": []}

# 定义禁止执行的命令列表
# rm -rf / 强制递归删除根目录 删除系统
# sudo 以root权限执行
# shutdown/reboot 关机/重启
# mkfs 格式化磁盘
# dd if= 用零覆盖磁盘 销毁所有的数据 不可恢复
# > /dev/sda 重定向到块设备，会破坏分区表 会导致磁盘损坏
DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if=", "> /dev/sda"]

# 定义需要用户确认的危险命令关键字列表（增加cmd的删除命令）
DESTRUCTIVE = ["rm ", "> /etc/", "chmod 777", "del ", "erase "]


# 注册钩子函数，将回调添加到对应事件的钩子列表
def register_hook(event: str, callback):
    HOOKS[event].append(callback)


# 注入当前工作目录信息到用户查询
def workspace_inject_hook(query: str) -> str | None:
    # 打印注入工作目录的钩子信息
    print(f"\x1b[90m[HOOK] UserPromptSubmit：注入工作目录 {WORKDIR}\x1b[0m")
    # 返回带有工作目录信息的查询字符串
    return f"<workspace>\n当前工作目录：{WORKDIR}\n</workspace>\n\n{query}"


# 权限控制钩子函数，对命令执行进行校验
def permission_hook(tool_name: str, tool_args: dict):
    """
    检查工具执行权限
    """
    print(
        f"\x1b[36m [HOOK] PreToolUse {tool_name} {json.dumps(tool_args,ensure_ascii=False)} \x1b[0m"
    )
    if tool_name == "bash":
        # 遍历每一条禁止执行的命令
        for pattern in DENY_LIST:
            # 如果命令包含禁止执行的命令
            if pattern in tool_args.get("command", ""):
                # 打印红色警告信息，显示被拦截内容
                print(f"\n\x1b[31m⛔ 已拦截：'{pattern}'\x1b[0m")
                # 返回禁止权限的原因（被禁止列表拦截）
                return "禁止列表拒绝权限"
        # 遍历每一条危险关键字
        for kw in DESTRUCTIVE:
            # 如果命令参数中包含危险关键字
            if kw in tool_args.get("command", ""):
                # 打印黄色警告，告知是可能破坏性的命令
                print(f"\n\x1b[33m⚠  可能破坏性的命令\x1b[0m")
                # 显示实际调用的工具和参数
                print(f"   工具: {tool_name}({tool_args})")
                # 提示用户是否允许执行，输入'y'或'yes'才继续
                choice = input("   允许？[y/N] ").strip().lower()
                # 如果用户不是输入“y”或"yes"
                if choice not in ("y", "yes"):
                    # 返回用户拒绝权限
                    return "用户拒绝权限"
    # 如果工具名称为write_file或edit_file，说明要操作文件
    if tool_name in ("write_file", "edit_file"):
        # 获取目标文件路径
        path = tool_args.get("path", "")
        # 检查文件是否在WORKDIR工作目录下
        if not (WORKDIR / path).resolve().is_relative_to(WORKDIR):
            # 如果不在工作区，提示警告
            print(f"\n\x1b[33m⚠  在工作区外写入\x1b[0m")
            # 显示尝试操作的工具及参数
            print(f"   工具: {tool_name}({tool_args})")
            # 询问用户是否允许
            choice = input("   允许？[y/N] ").strip().lower()
            # 如果不是允许，拒绝权限
            if choice not in ("y", "yes"):
                # 返回用户拒绝权限
                return "用户拒绝权限"
    # 如果所有检查都通过，则放行，返回None
    return None


# 日志钩子函数，记录工具使用日志
def log_hook(tool_name: str, tool_args: dict):
    """
    记录工具使用日志
    """
    # 取参数前两项并转换为字符串用于预览
    args_preview = str(list(tool_args.values())[:2])[:60]
    # 打印钩子触发信息
    print(f"\x1b[90m[HOOK] {tool_name}({args_preview})\x1b[0m")
    # 无特殊行为，直接返回None
    return None


# 钩子，处理工具输出过大的情况
def large_output_hook(tool_name: str, output):
    # 判断输出长度是否超过10万字符
    if len(str(output)) > 10:
        # 打印输出过大警告
        print(f"\x1b[33m[HOOK] ⚠ {tool_name} 输出过大：{len(str(output))} 字符\x1b[0m")
    # 返回None
    return None


# 会话统计钩子函数
def summary_hook(messages: list):
    # 统计工具调用的次数
    tool_count = sum(1 for m in messages if m.get("role") == "tool")
    # 打印工具调用次数信息
    print(f"\x1b[90m[HOOK] Stop：本次会话共使用 {tool_count} 次工具调用\x1b[0m")
    # 无特殊返回，直接None
    return None


# 触发用户输入相关的钩子链
def trigger_user_prompt_hooks(query: str) -> str:
    # 当前待处理的查询
    current = query
    # 依次触发钩子
    for callback in HOOKS["UserPromptSubmit"]:
        # 调用每个钩子获取结果
        result = callback(current)
        # 如果返回字符串则更新current
        if isinstance(result, str):
            current = result
    # 返回处理后的查询
    return current


# 通用钩子触发函数
def trigger_hooks(event: str, *args):
    # 按注册顺序依次触发对应事件下的钩子
    for callback in HOOKS[event]:
        # 调用钩子并获取返回值
        result = callback(*args)
        # 如果返回非None则终止并返回
        if result is not None:
            return result
    # 所有钩子都返回None则返回None
    return None


# 注册“用户提交”事件的钩子
register_hook("UserPromptSubmit", workspace_inject_hook)
# 注册“工具使用前”权限检查钩子
register_hook("PreToolUse", permission_hook)
# 注册“工具使用前”日志记录钩子
register_hook("PreToolUse", log_hook)
# 注册“工具使用后”大输出检测钩子
register_hook("PostToolUse", large_output_hook)
# 注册停止事件的会话总结钩子
register_hook("Stop", summary_hook)
