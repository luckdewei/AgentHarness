# 定义禁止执行的命令列表
from config import WORKDIR


DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if=", "> /dev/sda"]

# 定义需要用户确认的危险命令关键字列表（增加cmd的删除命令）
DESTRUCTIVE = ["rm ", "> /etc/", "chmod 777", "del ", "erase "]


def check_permission(tool_name: str, tool_args: dict) -> bool:
    """
    检查工具执行权限
    """
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
