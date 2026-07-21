# 导入os模块，用于与操作系统交互
import os

# 导入subprocess模块，用于执行子进程
import subprocess

# 从utils模块导入decode_subprocess_output函数，用于解码子进程输出
from utils import decode_subprocess_output, safe_path

# 导入glob模块，用于全局搜索
import glob as g

from config import Config

config = Config()


def run_bash_command(command: str) -> str:
    """
    执行bash命令
    """
    # os.name: nt是Windows，posix 是Linux
    if os.name == "nt" and command.strip().lower() == "date":
        # 将命令更改为Windows下同时输出日期和时间的命令
        command = "date /t & time /t"

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


def run_read_file(path: str, limit: int | None = None) -> str:
    """
    读取文件
    """
    try:
        # 使用safe_path校验并获取文件的路径，并指定编码读取内容并按行分割
        lines = safe_path(path).read_text(encoding=config.TEXT_ENCODING).splitlines()
        if limit and len(lines) > limit:
            lines = lines[:limit]
            # 截取前limit行，并添加提示信息
            lines = lines[:limit] + [f"...（还有 {len(lines) - limit} 行）"]
        # 将行列表转换为字符串，每行之间添加换行符
        return "\n".join(lines)
    # 捕获其他异常，返回错误信息
    except Exception as e:
        return f"读取错误：{e}"


def run_write_file(path: str, old_content: str, new_content: str) -> str:
    """
    写入文件
    """
    try:
        file_path = safe_path(path)
        text = file_path.read_text()
        if old_content not in text:
            return f"错误：在 {path} 中未找到指定文本"
        # 替换第一次出现的旧文本为新文本，并写回文件
        file_path.write_text(
            text.replace(old_content, new_content, 1), encoding=config.TEXT_ENCODING
        )
        # 返回编辑成功的提示
        return f"文件 {path} 编辑成功"
    except Exception as e:
        return f"写入文件错误：{e}"


def run_global_search(pattern: str) -> str:
    """
    全局搜索
    """
    try:
        results = []
        # 使用glob模块全局搜索匹配的文件或目录
        for match in g.glob(pattern, root_dir=config.WORKDIR):
            # 检查匹配到的路径是否是相对于WORKDIR的子路径
            if (config.WORKDIR / match).resolve().is_relative_to(config.WORKDIR):
                results.append(match)
        return "\n".join(results) if results else "(无匹配)"
    except Exception as e:
        return f"全局搜索错误：{e}"


tool_handlers = {
    "bash": run_bash_command,
    "read_file": run_read_file,
    "write_file": run_write_file,
    "glob": run_global_search,
}
