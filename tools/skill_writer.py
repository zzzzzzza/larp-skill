#!/usr/bin/env python3
"""Skill 文件管理器

管理已生成的剧本杀角色 Skill 文件。

Usage:
    python3 skill_writer.py --action list [--base-dir ./characters]
    python3 skill_writer.py --action info --slug <slug> [--base-dir ./characters]
    python3 skill_writer.py --action delete --slug <slug> [--base-dir ./characters]
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def list_skills(base_dir: str) -> list:
    """列出所有已生成的角色 Skill"""
    skills = []
    base_path = Path(base_dir)

    if not base_path.exists():
        return skills

    for item in sorted(base_path.iterdir()):
        if not item.is_dir():
            continue

        meta_path = item / 'meta.json'
        if not meta_path.exists():
            continue

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            skills.append({
                'slug': meta.get('slug', item.name),
                'game_name': meta.get('game_name', '未知剧本'),
                'character_name': meta.get('character_name', '未知角色'),
                'character_type': meta.get('character_type', '未知'),
                'player_name': meta.get('player_name', '未知'),
                'version': meta.get('version', 'v1'),
                'created_at': meta.get('created_at', ''),
                'updated_at': meta.get('updated_at', ''),
                'corrections_count': meta.get('corrections_count', 0),
                'path': str(item),
            })
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告：无法读取 {meta_path}: {e}", file=sys.stderr)
            continue

    return skills


def show_skill_info(base_dir: str, slug: str) -> dict:
    """显示单个 Skill 的详细信息"""
    skill_dir = Path(base_dir) / slug
    meta_path = skill_dir / 'meta.json'

    if not meta_path.exists():
        print(f"错误：未找到角色 Skill「{slug}」", file=sys.stderr)
        sys.exit(1)

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 统计文件
    files = {
        'SKILL.md': (skill_dir / 'SKILL.md').exists(),
        'story.md': (skill_dir / 'story.md').exists(),
        'persona.md': (skill_dir / 'persona.md').exists(),
        'meta.json': True,
    }

    # 统计版本数
    versions_dir = skill_dir / 'versions'
    version_count = len(list(versions_dir.iterdir())) if versions_dir.exists() else 0

    # 统计源文件数
    sources_dir = skill_dir / 'sources' / 'pdfs'
    source_count = len(list(sources_dir.iterdir())) if sources_dir.exists() else 0

    return {
        'meta': meta,
        'files': files,
        'version_count': version_count,
        'source_count': source_count,
    }


def format_skill_list(skills: list) -> str:
    """格式化 Skill 列表输出"""
    if not skills:
        return "暂无角色 Skill。使用 /create-larp-character 创建你的第一个角色。"

    output = []
    output.append(f"已生成 {len(skills)} 个角色 Skill：\n")

    for s in skills:
        type_icon = "🎭" if s['character_type'] == 'player' else "👤"
        output.append(f"  {type_icon} {s['character_name']}（{s['game_name']}）")
        output.append(f"     面向：{s['player_name']}")
        output.append(f"     版本：{s['version']} | 纠正：{s['corrections_count']} 条")
        output.append(f"     触发：/{s['slug']}")
        output.append(f"     路径：{s['path']}")
        output.append("")

    return '\n'.join(output)


def format_skill_info(info: dict) -> str:
    """格式化 Skill 详情输出"""
    meta = info['meta']
    output = []

    output.append(f"角色详情：{meta.get('character_name', '未知')}\n")
    output.append(f"  剧本：{meta.get('game_name', '未知')}")
    output.append(f"  类型：{meta.get('character_type', '未知')}")
    output.append(f"  面向：{meta.get('player_name', '未知')}")
    output.append(f"  版本：{meta.get('version', 'v1')}")
    output.append(f"  创建：{meta.get('created_at', '未知')}")
    output.append(f"  更新：{meta.get('updated_at', '未知')}")

    game_info = meta.get('game_info', {})
    if game_info:
        output.append(f"  类型：{game_info.get('genre', '')} · {game_info.get('era', '')} · {game_info.get('relationship', '')}")

    output.append(f"  纠正记录：{meta.get('corrections_count', 0)} 条")
    output.append(f"  历史版本：{info['version_count']} 个")
    output.append(f"  源文件：{info['source_count']} 个")

    output.append(f"\n  文件状态：")
    for fname, exists in info['files'].items():
        status = "✅" if exists else "❌"
        output.append(f"    {status} {fname}")

    if meta.get('impression'):
        output.append(f"\n  印象：{meta['impression']}")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='剧本杀角色 Skill 文件管理器')
    parser.add_argument('--action', required=True,
                        choices=['list', 'info', 'delete'],
                        help='操作类型')
    parser.add_argument('--slug', help='角色 slug（info/delete 操作需要）')
    parser.add_argument('--base-dir', default='./characters',
                        help='角色 Skill 基础目录（默认 ./characters）')

    args = parser.parse_args()

    if args.action == 'list':
        skills = list_skills(args.base_dir)
        print(format_skill_list(skills))

    elif args.action == 'info':
        if not args.slug:
            print("错误：info 操作需要指定 --slug", file=sys.stderr)
            sys.exit(1)
        info = show_skill_info(args.base_dir, args.slug)
        print(format_skill_info(info))

    elif args.action == 'delete':
        if not args.slug:
            print("错误：delete 操作需要指定 --slug", file=sys.stderr)
            sys.exit(1)
        skill_dir = Path(args.base_dir) / args.slug
        if not skill_dir.exists():
            print(f"错误：未找到角色 Skill「{args.slug}」", file=sys.stderr)
            sys.exit(1)
        # 不在脚本中执行删除，返回路径让调用者确认
        print(f"确认删除以下目录？")
        print(f"  {skill_dir}")
        print(f"请在确认后手动执行：rm -rf {skill_dir}")


if __name__ == '__main__':
    main()
