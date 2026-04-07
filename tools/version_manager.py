#!/usr/bin/env python3
"""版本管理器

管理剧本杀角色 Skill 的版本存档与回滚。

Usage:
    python3 version_manager.py --action backup --slug <slug> [--base-dir ./characters]
    python3 version_manager.py --action rollback --slug <slug> --version <version> [--base-dir ./characters]
    python3 version_manager.py --action list --slug <slug> [--base-dir ./characters]
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime


def get_current_version(meta_path: Path) -> str:
    """获取当前版本号"""
    if not meta_path.exists():
        return "v0"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    return meta.get('version', 'v1')


def increment_version(version: str) -> str:
    """版本号 +1"""
    num = int(version.replace('v', ''))
    return f"v{num + 1}"


def backup_version(base_dir: str, slug: str) -> str:
    """备份当前版本"""
    skill_dir = Path(base_dir) / slug
    meta_path = skill_dir / 'meta.json'

    if not skill_dir.exists():
        print(f"错误：未找到角色 Skill「{slug}」", file=sys.stderr)
        sys.exit(1)

    current_version = get_current_version(meta_path)
    versions_dir = skill_dir / 'versions' / current_version
    versions_dir.mkdir(parents=True, exist_ok=True)

    # 备份核心文件
    files_to_backup = ['SKILL.md', 'story.md', 'persona.md', 'meta.json']
    backed_up = []

    for fname in files_to_backup:
        src = skill_dir / fname
        if src.exists():
            dst = versions_dir / fname
            shutil.copy2(str(src), str(dst))
            backed_up.append(fname)

    # 更新 meta.json 的版本号
    new_version = increment_version(current_version)
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta['version'] = new_version
        meta['updated_at'] = datetime.now().isoformat()
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"已备份 {current_version} → versions/{current_version}/")
    print(f"  备份文件：{', '.join(backed_up)}")
    print(f"  当前版本：{new_version}")
    return new_version


def rollback_version(base_dir: str, slug: str, target_version: str) -> None:
    """回滚到指定版本"""
    skill_dir = Path(base_dir) / slug
    versions_dir = skill_dir / 'versions' / target_version

    if not versions_dir.exists():
        print(f"错误：版本 {target_version} 不存在", file=sys.stderr)
        available = list_versions(base_dir, slug)
        if available:
            print(f"可用版本：{', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    # 先备份当前版本
    meta_path = skill_dir / 'meta.json'
    current_version = get_current_version(meta_path)
    print(f"回滚前先备份当前版本 {current_version}...")

    current_backup_dir = skill_dir / 'versions' / current_version
    current_backup_dir.mkdir(parents=True, exist_ok=True)

    files_to_backup = ['SKILL.md', 'story.md', 'persona.md', 'meta.json']
    for fname in files_to_backup:
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(str(src), str(current_backup_dir / fname))

    # 恢复目标版本
    restored = []
    for fname in files_to_backup:
        src = versions_dir / fname
        if src.exists():
            dst = skill_dir / fname
            shutil.copy2(str(src), str(dst))
            restored.append(fname)

    # 更新 meta.json 标记回滚
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta['updated_at'] = datetime.now().isoformat()
        meta['rollback_from'] = current_version
        meta['rollback_to'] = target_version
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"已回滚到 {target_version}")
    print(f"  恢复文件：{', '.join(restored)}")
    print(f"  之前的 {current_version} 已备份到 versions/{current_version}/")


def list_versions(base_dir: str, slug: str) -> list:
    """列出所有可用版本"""
    skill_dir = Path(base_dir) / slug
    versions_dir = skill_dir / 'versions'

    if not versions_dir.exists():
        return []

    versions = []
    for item in sorted(versions_dir.iterdir()):
        if item.is_dir() and item.name.startswith('v'):
            files = [f.name for f in item.iterdir() if f.is_file()]
            versions.append({
                'version': item.name,
                'files': files,
                'path': str(item),
            })

    return versions


def format_version_list(versions: list, slug: str) -> str:
    """格式化版本列表输出"""
    if not versions:
        return f"角色「{slug}」暂无历史版本。"

    output = [f"角色「{slug}」的历史版本：\n"]

    for v in versions:
        output.append(f"  {v['version']}")
        output.append(f"    文件：{', '.join(v['files'])}")
        output.append("")

    output.append(f"回滚命令：/larp-rollback {slug} <version>")
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='剧本杀角色 Skill 版本管理器')
    parser.add_argument('--action', required=True,
                        choices=['backup', 'rollback', 'list'],
                        help='操作类型')
    parser.add_argument('--slug', required=True, help='角色 slug')
    parser.add_argument('--version', help='目标版本（rollback 操作需要）')
    parser.add_argument('--base-dir', default='./characters',
                        help='角色 Skill 基础目录（默认 ./characters）')

    args = parser.parse_args()

    if args.action == 'backup':
        backup_version(args.base_dir, args.slug)

    elif args.action == 'rollback':
        if not args.version:
            print("错误：rollback 操作需要指定 --version", file=sys.stderr)
            sys.exit(1)
        rollback_version(args.base_dir, args.slug, args.version)

    elif args.action == 'list':
        versions = list_versions(args.base_dir, args.slug)
        print(format_version_list(versions, args.slug))


if __name__ == '__main__':
    main()
