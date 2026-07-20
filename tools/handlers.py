# 导入os模块，用于与操作系统交互
import os

# 导入subprocess模块，用于执行子进程
import subprocess

# 从utils模块导入decode_subprocess_output函数，用于解码子进程输出
from utils import decode_subprocess_output


def run_bash_command(command: str) -> str:
    """
    执行bash命令
    """
    # os.name: nt是Windows，posix 是Linux
    if os.name == "nt" and command.strip().lower() == "date":
        # 将命令更改为Windows下同时输出日期和时间的命令
        command = "date /t & time /t"

    # 定义危险命令的列表
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    # 如果命令中包含任何一个危险命令
    if any(d in command for d in dangerous):
        # 返回错误提示，拦截执行危险命令
        return "错误：危险命令已被拦截"

    # 尝试执行命令，捕获异常
    try:
        # 使用subprocess.run运行命令
        r = subprocess.run(
            command,  # 要执行的命令
            shell=True,  # 在shell中执行
            cwd=os.getcwd(),  # 当前工作目录设置为当前路径
            capture_output=True,  # 捕获标准输出和标准错误
            timeout=120,  # 超时时间为120秒
        )
        # 解码输出内容，合并stdout和stderr，并去除首尾空白
        out = decode_subprocess_output((r.stdout or b"") + (r.stderr or b"")).strip()
        # 返回输出内容的前50000个字符，如果无输出则返回'（无输出）'
        return out[:50000] if out else "（无输出）"
    # 捕获超时异常，返回超时错误信息
    except subprocess.TimeoutExpired:
        return "错误：超时（120 秒）"
    # 捕获文件未找到或OS错误，返回详细错误信息
    except (FileNotFoundError, OSError) as e:
        return f"错误：{e}"


tool_handlers = {
    "bash": run_bash_command,
}
