#!/usr/bin/env python3
"""剧本杀 PDF 解析器

辅助解析剧本杀相关 PDF 文件（玩家本、DM手册、NPC人物小传），
提取结构化内容供 SKILL.md 主流程使用。

注意：Claude Code 的 Read 工具已原生支持 PDF 读取。
本脚本主要用于：
1. 较长 PDF 的预处理和章节拆分
2. 提取并标注文档结构（标题、段落、列表）
3. 按角色名过滤相关内容

Usage:
    python3 pdf_parser.py --file <path> --type <type> --character <name> --output <output_path>

Types:
    player_script  - 玩家本
    npc_bio        - NPC人物小传
    dm_manual      - DM手册
    other_script   - 其他角色的玩家本
"""

import argparse
import json
import re
import os
import sys
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """从 PDF 中提取纯文本

    尝试多种方式提取：
    1. PyPDF2（如果安装了）
    2. pdfplumber（如果安装了）
    3. 回退到提示用户使用 Read 工具
    """
    text = ""

    # 尝试 PyPDF2
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        if text.strip():
            return text
    except ImportError:
        pass
    except Exception as e:
        print(f"PyPDF2 解析失败: {e}", file=sys.stderr)

    # 尝试 pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        if text.strip():
            return text
    except ImportError:
        pass
    except Exception as e:
        print(f"pdfplumber 解析失败: {e}", file=sys.stderr)

    # 都没安装或都失败了
    if not text.strip():
        print("提示：未安装 PDF 解析库。建议：", file=sys.stderr)
        print("  pip3 install PyPDF2  或  pip3 install pdfplumber", file=sys.stderr)
        print("  或直接使用 Claude Code 的 Read 工具读取 PDF", file=sys.stderr)
        return ""

    return text


def detect_sections(text: str) -> list:
    """检测文本中的章节结构"""
    sections = []
    lines = text.split('\n')
    current_section = {"title": "开头", "content": [], "line_start": 0}

    # 常见的章节标题模式
    section_patterns = [
        r'^第[一二三四五六七八九十\d]+[章节幕]',   # 第一章、第1节
        r'^[一二三四五六七八九十]+[、.]',           # 一、二、
        r'^\d+[、.\s]',                            # 1、 2.
        r'^【.+】',                                 # 【人物关系】
        r'^━+',                                    # 分隔线
        r'^-{3,}',                                 # ---
        r'^={3,}',                                 # ===
        r'^人物(?:关系|背景|介绍|小传)',
        r'^(?:背景|前情|真相|结局|尾声)',
        r'^(?:关系网|时间线|大事记)',
    ]

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            current_section["content"].append("")
            continue

        is_section_header = False
        for pattern in section_patterns:
            if re.match(pattern, stripped):
                is_section_header = True
                break

        # 也检测全大写或特别短的行（可能是标题）
        if not is_section_header and len(stripped) < 20 and stripped.endswith(('：', ':', '）', ')')):
            is_section_header = True

        if is_section_header:
            if current_section["content"]:
                sections.append(current_section)
            current_section = {"title": stripped, "content": [], "line_start": i}
        else:
            current_section["content"].append(stripped)

    if current_section["content"]:
        sections.append(current_section)

    return sections


def filter_by_character(sections: list, character_name: str) -> list:
    """过滤出与指定角色相关的内容"""
    relevant_sections = []

    for section in sections:
        content_text = '\n'.join(section["content"])
        # 检查章节标题或内容中是否包含角色名
        if character_name in section["title"] or character_name in content_text:
            section["relevance"] = "direct"  # 直接提到角色
            relevant_sections.append(section)
        else:
            # 检查是否包含关系类关键词
            relation_keywords = ['关系', '人物', '背景', '真相', '秘密', '时间线']
            if any(kw in section["title"] for kw in relation_keywords):
                section["relevance"] = "contextual"  # 上下文相关
                relevant_sections.append(section)

    return relevant_sections


def classify_content(sections: list, doc_type: str) -> dict:
    """根据文档类型对内容进行分类"""
    classified = {
        "background": [],      # 人物背景
        "relationships": [],   # 人物关系
        "timeline": [],        # 时间线/事件
        "secrets": [],         # 秘密
        "personality": [],     # 性格描述
        "dialogue": [],        # 对话/语言风格
        "other": []            # 其他
    }

    classify_keywords = {
        "background": ['背景', '身世', '出身', '经历', '过去', '家庭', '成长'],
        "relationships": ['关系', '人物', '之间', '爱', '恨', '朋友', '敌人', '师', '徒'],
        "timeline": ['时间', '事件', '年', '月', '日', '当时', '后来', '之前', '之后'],
        "secrets": ['秘密', '真相', '隐藏', '不为人知', '暗中', '实际上'],
        "personality": ['性格', '特点', '习惯', '脾气', '态度', '爱好'],
        "dialogue": ['说', '道', '口头禅', '语气', '称呼', '说话'],
    }

    for section in sections:
        title = section["title"]
        content = '\n'.join(section["content"])
        combined = title + content

        categorized = False
        for category, keywords in classify_keywords.items():
            if any(kw in combined for kw in keywords):
                classified[category].append(section)
                categorized = True
                break

        if not categorized:
            classified["other"].append(section)

    return classified


def format_output(classified: dict, character_name: str, doc_type: str, file_path: str) -> str:
    """格式化输出结果"""
    output_lines = []
    output_lines.append(f"# PDF 解析结果")
    output_lines.append(f"")
    output_lines.append(f"- 文件：{Path(file_path).name}")
    output_lines.append(f"- 类型：{doc_type}")
    output_lines.append(f"- 角色：{character_name}")
    output_lines.append(f"")
    output_lines.append(f"---")
    output_lines.append(f"")

    category_names = {
        "background": "人物背景",
        "relationships": "人物关系",
        "timeline": "时间线与事件",
        "secrets": "秘密与真相",
        "personality": "性格描述",
        "dialogue": "对话与语言风格",
        "other": "其他内容"
    }

    for category, sections in classified.items():
        if not sections:
            continue

        output_lines.append(f"## {category_names.get(category, category)}")
        output_lines.append(f"")

        for section in sections:
            relevance_tag = ""
            if hasattr(section, 'get') and section.get("relevance") == "direct":
                relevance_tag = " [直接相关]"
            elif hasattr(section, 'get') and section.get("relevance") == "contextual":
                relevance_tag = " [上下文相关]"

            output_lines.append(f"### {section['title']}{relevance_tag}")
            output_lines.append(f"")
            for line in section["content"]:
                if line:
                    output_lines.append(line)
                else:
                    output_lines.append("")
            output_lines.append(f"")

    return '\n'.join(output_lines)


def main():
    parser = argparse.ArgumentParser(description='剧本杀 PDF 解析器')
    parser.add_argument('--file', required=True, help='PDF 文件路径')
    parser.add_argument('--type', required=True,
                        choices=['player_script', 'npc_bio', 'dm_manual', 'other_script'],
                        help='文档类型')
    parser.add_argument('--character', required=True, help='目标角色名')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--format', default='markdown', choices=['markdown', 'json'],
                        help='输出格式（默认 markdown）')

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.file):
        print(f"错误：文件不存在 - {args.file}", file=sys.stderr)
        sys.exit(1)

    # 检查文件扩展名
    ext = Path(args.file).suffix.lower()
    if ext != '.pdf':
        print(f"警告：文件扩展名为 {ext}，非 .pdf。尝试继续处理...", file=sys.stderr)

    print(f"正在解析：{args.file}")
    print(f"文档类型：{args.type}")
    print(f"目标角色：{args.character}")

    # 提取文本
    text = extract_text_from_pdf(args.file)

    if not text:
        # 如果无法提取文本，输出提示
        result = f"# PDF 解析结果\n\n"
        result += f"⚠️ 无法自动提取 PDF 文本。\n"
        result += f"请使用 Claude Code 的 `Read` 工具直接读取此文件：\n"
        result += f"  文件路径：{args.file}\n"

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"已输出提示到：{args.output}")
        sys.exit(0)

    # 检测章节结构
    sections = detect_sections(text)

    # 按角色过滤
    if args.character:
        relevant = filter_by_character(sections, args.character)
        # 如果过滤后没有内容，保留全部
        if not relevant:
            print(f"未找到直接包含「{args.character}」的内容，保留全部章节", file=sys.stderr)
            relevant = sections
    else:
        relevant = sections

    # 分类内容
    classified = classify_content(relevant, args.type)

    # 格式化输出
    if args.format == 'json':
        result = json.dumps(classified, ensure_ascii=False, indent=2, default=str)
    else:
        result = format_output(classified, args.character, args.type, args.file)

    # 写入输出文件
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"解析完成！结果已写入：{args.output}")
    print(f"  - 总章节数：{len(sections)}")
    print(f"  - 相关章节数：{len(relevant)}")

    # 输出分类统计
    for category, items in classified.items():
        if items:
            print(f"  - {category}：{len(items)} 个章节")


if __name__ == '__main__':
    main()
