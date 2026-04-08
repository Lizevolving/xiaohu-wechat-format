"""xiaohu-wechat-format 共享工具模块

提供配置文件加载等各脚本共用的功能。
"""

import json
import sys
from pathlib import Path


def load_config(skill_dir: Path) -> dict:
    """加载配置文件，提供清晰的错误信息。

    优先读取 config.json；不存在时给出从 config.example.json 复制的提示。
    """
    config_path = skill_dir / "config.json"
    example_path = skill_dir / "config.example.json"

    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
        except json.JSONDecodeError as e:
            print(f"错误：config.json 格式无效 - {e}", file=sys.stderr)
            print(f"  位置：{config_path}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(cfg, dict):
            print(f"错误：config.json 顶层必须是 JSON 对象", file=sys.stderr)
            print(f"  位置：{config_path}", file=sys.stderr)
            sys.exit(1)
        return cfg

    # config.json 不存在
    if example_path.exists():
        print(f"错误：未找到 config.json", file=sys.stderr)
        print(f"  请执行：cp config.example.json config.json", file=sys.stderr)
        print(f"  然后编辑 config.json 填入你的配置", file=sys.stderr)
        print(f"  位置：{skill_dir}", file=sys.stderr)
    else:
        print(f"错误：未找到 config.json 和 config.example.json", file=sys.stderr)
        print(f"  位置：{skill_dir}", file=sys.stderr)
    sys.exit(1)
