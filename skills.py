from config import SKILLS_DIR, TEXT_ENCODING
from utils import parse_frontmatter

# 定义一个全局字典，用于存放技能信息，键为字符串，值为字典
SKILL_REGISTRY: dict[str, dict] = {}


# 定义一个私有函数，用于扫描技能目录下的所有技能
def _scan_skills():
    # 如果技能目录不存在，则直接返回
    if not SKILLS_DIR.exists():
        return
    # 遍历技能目录下的所有子目录，按名称排序
    for dir in sorted(SKILLS_DIR.iterdir()):
        # 如果子目录不是目录，则跳过
        if not dir.is_dir():
            continue
        # 构造manifest文件（SKILL.md）的路径
        manifest_path = dir / "SKILL.md"
        if not manifest_path.exists():
            continue
        # 读取manifest文件 error="replace" 通常用在文本读取函数中，指定当遇到编码错误时的处理方式

        # "replace" 表示用 �（U+FFFD）替换无法解码的字节 其他常见选项："strict"（抛出异常）、"ignore"（忽略错误字符）

        raw = manifest_path.read_text(encoding=TEXT_ENCODING, errors="replace")

        # 解析frontmatter，获取元信息和正文内容
        meta, _body = parse_frontmatter(raw)
        # 获取技能名称，优先元信息中的name字段，否则用目录名
        name = meta.get("name", dir.name)
        # 获取技能描述，优先元信息中的description字段，否则用第一行内容
        desc = meta.get("description", raw.split("\n")[0].lstrip("#").strip())
        # 将技能信息存入全局注册表
        SKILL_REGISTRY[name] = {"name": name, "description": desc, "content": raw}


# 定义一个函数，根据技能名加载技能内容
def load_skill(name: str) -> str:
    # 从注册表中获取技能信息
    skill = SKILL_REGISTRY.get(name)
    # 如果没有找到，返回提示信息
    if not skill:
        return f"未找到技能：{name}"
    # 在控制台打印加载提示（带颜色）
    print(f"\x1b[90m[技能] 已加载 {name}\x1b[0m")
    # 返回技能内容
    return skill["content"]


# 调用扫描函数，初始化技能注册表
_scan_skills()
