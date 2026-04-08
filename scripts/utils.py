"""xiaohu-wechat-format 共享配置工具。"""

import json
import sys
from pathlib import Path


def _read_json_dict(config_path: Path) -> dict:
    """读取 JSON 配置并确保顶层为对象。"""
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误：配置文件格式无效 - {e}", file=sys.stderr)
        print(f"  位置：{config_path}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(cfg, dict):
        print("错误：配置文件顶层必须是 JSON 对象", file=sys.stderr)
        print(f"  位置：{config_path}", file=sys.stderr)
        sys.exit(1)
    return cfg


def load_config_file(config_path: Path, *, required: bool = True,
                     example_path: Path | None = None) -> dict:
    """按路径加载配置文件。

    `required=False` 时，缺少配置直接返回空字典。
    """
    if config_path.exists():
        return _read_json_dict(config_path)

    if not required:
        return {}

    print(f"错误：未找到配置文件 {config_path.name}", file=sys.stderr)
    if example_path and example_path.exists():
        print(f"  请执行：cp {example_path.name} {config_path.name}", file=sys.stderr)
        print(f"  然后编辑 {config_path.name} 填入你的配置", file=sys.stderr)
    elif example_path:
        print(f"  同目录下也不存在示例文件：{example_path.name}", file=sys.stderr)
    print(f"  位置：{config_path.parent}", file=sys.stderr)
    sys.exit(1)


def load_config(skill_dir: Path, *, required: bool = True) -> dict:
    """加载技能根目录下的 `config.json`。"""
    return load_config_file(
        skill_dir / "config.json",
        required=required,
        example_path=skill_dir / "config.example.json",
    )
