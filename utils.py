# 工具函数，可以把pydantic类型的大模型回复消息对象转成字典
from pathlib import Path

from config import WORKDIR


def assistant_message_dict(message) -> dict:
    # 使用model_dump可以把对象转字典，排除值为None的项
    data = message.model_dump(exclude_none=True)
    # 把角色的类型设置为助手
    data["role"] = "assistant"
    return data


# 定义一个函数decode_subprocess_output，参数为data（字节类型或None），返回字符串类型
def decode_subprocess_output(data: bytes | None) -> str:
    # 如果data为None或者为空字节，则返回空字符串
    if not data:
        return ""
    # 依次尝试三种编码方式进行解码
    for encoding in ("utf-8", "gbk", "cp936"):
        try:
            # 使用当前编码方式尝试解码，成功则返回结果
            return data.decode(encoding)
        # 如果解码时出现UnicodeDecodeError，则继续尝试下一个编码
        except UnicodeDecodeError:
            continue
    # 如果以上编码都无法解码，则使用utf-8编码并使用replace策略处理错误，并返回结果
    return data.decode("utf-8", errors="replace")


# 此函数接收一个路径，返回一个Path
def safe_path(p: str) -> Path:
    # 通过WORKDIR与p拼接，并调用resolve方法，得到p的绝对路径
    path = (WORKDIR / p).resolve()
    # 判断path是不是在WORKDIR工作区内的子路径，如果不是则抛异常
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"超出工作区:{p}")
    # 返回最终安全生成的路径对象
    return path


# 定义一个extract_text函数，参数为content，返回字符串类型
def extract_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return str(content)


# 定义parse_frontmatter函数，参数为text，返回一个元组(字典,字符串)
def parse_frontmatter(text: str) -> tuple[dict, str]:
    if "---" not in text:
        return {}, text
    # 用'---'分割文本，最多分割2次，得到3段内容
    parts = text.split("---", 2)
    # 如果分割出来的部分不足3个，说明无有效frontmatter，返回空字典和原始文本
    if len(parts) < 3:
        return {}, text
    meta = {}
    # 第一段是frontmatter，第二段是正文
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            # 去掉键和值两端空白，并将值两端的引号去除，存入字典
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, parts[2].strip()
