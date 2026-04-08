<div align="center">

# larp.skill

> *「走不出来的那个角色，让ta再陪你一会儿。」*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

打完情感本，走不出那个角色？<br>
ta的故事结束了，但你还想跟ta说说话？<br>
那些没来得及说的话、没来得及做的选择，还在心里反复回响？

**把剧本杀角色蒸馏成 AI Skill，让ta继续陪你。**

<br>

提供玩家本/人物小传 PDF + 你对角色的印象<br>
生成一个**真正像ta的 AI Skill**<br>
用ta的语气说话，用ta对你的方式回应你，记得你们一起经历的故事

[快速开始](#-快速开始) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [项目结构](#项目结构)

</div>

---

## ⚡ 快速开始

不想自己蒸馏？先试试现成的角色 Skill，30 秒体验效果：

### 示例角色 Skill

| 角色 Skill | 剧本 | 角色 → 对话对象 | 下载 |
|------------|------|-----------------|------|
| `larp-归途七万里_张眷信_to_容葵` | 归途七万里 | 张眷信 → 容葵 | [📦 下载](https://github.com/zzzzzzza/larp-skill/raw/main/example_skills/归途七万里_张眷信_to_容葵.zip) |
| `larp-归途七万里_容葵_to_张眷信` | 归途七万里 | 容葵 → 张眷信 | [📦 下载](https://github.com/zzzzzzza/larp-skill/raw/main/example_skills/归途七万里_容葵_to_张眷信.zip) |
| `larp-塑料温室_赵玄_to_崔昭贤` | 塑料温室 | 赵玄 → 崔昭贤 | [📦 下载](https://github.com/zzzzzzza/larp-skill/raw/main/example_skills/塑料温室_赵玄_to_崔昭贤.zip) |

### 使用方法（以 Qoder Work 为例）

1. **下载**：点击上方表格中的「📦 下载」链接，下载 `.zip` 压缩包
2. **添加技能**：在 Qoder Work 中，将下载的压缩包通过「安装技能」导入
3. **开始对话**：导入后调用技能即可直接与角色对话，像聊天一样跟 ta 说话就好

> 想自己从剧本 PDF 蒸馏角色？往下看完整的[安装](#安装)和[使用](#使用)指南。

---

## 效果示例

> 输入：剧本「归途七万里」，角色「张眷信」（玩家位），我扮演「容葵」，情感本，民国，恋人

**场景一：重逢**

```
容葵      ❯ 是你吗眷信，你最近过的怎么样

张眷信    ❯ 是我……容儿，是我。
             最近？最近……挺好的。铁路通车了，你知道吧？
             从北京到张家口，四个小时。隧道也没有再塌……
             我骗你的。
             铁路是通了，可我……不太好。容儿，你走以后，
             我每天晚上都在等信。信越来越短，越来越少……
             你呢？你……有没有好好吃饭？
             ……没关系的。你来了就好。你来了，就都好了。
```

**场景二：日常对话**

```
容葵      ❯ 你在做什么

张眷信    ❯ 嗯？啊，在看……一本关于铁路设计的书。
             你要不要一起看？虽然可能有点枯燥……
             不过，容儿你在的话，好像什么都不枯燥了。
```

**场景三：情感试探**

```
容葵      ❯ 想你了

张眷信    ❯ 我……我也是。
             容儿，我一直都……嗯，我也想你。很想。
             （说完低头不敢看她）
```

这不是通用角色扮演。张眷信的 Skill 知道他和容葵之间发生过什么，会用他对容葵独有的态度和语气回应。换一个对话对象，他的反应会完全不同。

---

## 安装

### Claude Code

```bash
# 安装到当前项目
mkdir -p .claude/skills
git clone https://github.com/zzzzzzza/larp-skill .claude/skills/create-larp-character

# 或安装到全局
git clone https://github.com/zzzzzzza/larp-skill ~/.claude/skills/create-larp-character
```

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

PDF 解析依赖是可选的——Claude Code 的 Read 工具已原生支持 PDF 读取。

---

## 环境要求

- **Claude Code**：免费安装，需要 Node.js 18+
- **API 消耗**：创建一个角色 Skill 约消耗 **70k-200k tokens**（取决于玩家本篇幅和数量）
  - 中等篇幅剧本（如归途七万里，6 份 PDF 共 5500 行）≈ 70-100k tokens
  - 较长篇幅剧本（多角色本 + DM 手册）≈ 150-200k tokens
  - 主要消耗在：PDF 语义压缩（~30%）、分批分析（~40%）、内容生成（~30%）
- **不需要 GPU**，不需要本地模型，不需要 Docker

---

## 使用

### 第一步：准备 PDF 文件

在本地创建一个文件夹，按角色名分子文件夹存放 PDF：

```
归途七万里/
├── 张眷信/              # 你想蒸馏的角色的玩家本
│   ├── 张眷信A.pdf
│   ├── 贾克斯B.pdf
│   └── 张眷信C.pdf
├── 容葵/                # 你自己扮演的角色的玩家本
│   ├── 容葵A.pdf
│   ├── 露丝B.pdf
│   └── 容葵C.pdf
├── DM手册/               # （可选）补充全局真相和时间线
│   └── DM手册.pdf
└── 其他角色/             # （可选）多视角补充
    └── xxx.pdf
```

> **最少需要**目标角色 + 你的角色两个文件夹。材料越丰富，角色还原度越高。

### 第二步：创建角色 Skill

在 Claude Code 中输入：

```
/create-larp-character
```

Skill 会依次问你 4 个问题：

1. 剧本叫什么名字？
2. 你想蒸馏哪个角色？ta 是玩家位还是 NPC？
3. 你自己扮演的是哪个角色？
4. （可选）补充信息——剧本类型、时代、你们的关系、你对 ta 的印象

然后提供 PDF 文件夹的本地路径，Skill 会自动扫描并处理。

全程约 5-15 分钟，完成后你会看到：

```
✅ 角色 Skill 已创建！

  🎭 角色：张眷信（归途七万里）
  💬 对话对象：面向容葵
  📖 触发词：/归途七万里_张眷信_to_容葵
```

### 第三步：开始对话

用触发词调用角色 Skill：

```
/归途七万里_张眷信_to_容葵
```

然后直接跟 ta 聊天就好。

### 第四步：让角色更像（可选）

- **追加材料**：找到了其他角色的玩家本？直接说「我有新材料」
- **对话纠正**：觉得 ta 说的不对？直接说「ta 不会这样说」或「ta 应该是…」，修正会立即生效

### 管理命令

| 命令 | 说明 |
|------|------|
| `/list-larp-characters` | 列出所有角色 Skill |
| `/{slug}` | 调用角色 Skill，开始对话 |
| `/larp-rollback {slug} {version}` | 回滚到历史版本 |
| `/delete-larp {slug}` | 删除角色 Skill |
| `/curtain-call {slug}` | 谢幕（温柔别名） |

---

## 功能特性

### 数据源

| 来源 | 格式 | 备注 |
|------|------|------|
| 玩家本 | PDF | 核心数据源，信息最丰富 |
| NPC 人物小传 | PDF | 适合蒸馏 NPC 角色 |
| DM 手册 | PDF | 补充全局真相和时间线 |
| 其他角色玩家本 | PDF | 多视角补充 |
| 口述/粘贴 | 纯文本 | 你的打本体验和记忆 |

### 生成的 Skill 结构

每个角色 Skill 由两部分组成，共同驱动输出：

| 部分 | 内容 |
|------|------|
| **Part A — Story Memory** | 人物背景、关键事件时间线、关系图谱、秘密档案、情感线、与你的专属记忆 |
| **Part B — Persona** | 5 层性格结构：硬规则 → 身份 → 表达风格 → 情感决策 → 关系行为 |

运行逻辑：`收到消息 → Persona 判断角色态度 → Story Memory 补充记忆 → 用角色的方式输出`

### 关系导向

生成的 Skill 不是一个通用角色，而是面向**你扮演的那个角色**的互动版本。
同一个角色，面对不同的对话对象，会有完全不同的态度、语气和互动方式。

### 进化机制

* **追加材料** → 找到了其他角色的玩家本 → 自动分析增量 → merge 进对应部分
* **对话纠正** → 说「ta不会这样说」→ 写入 Correction 层，立即生效
* **版本管理** → 每次更新自动存档，支持回滚

---

## 项目结构

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准：

```
larp-skill/
├── SKILL.md                # Skill 入口（meta-skill）
├── prompts/                # Prompt 模板
│   ├── intake.md           #   对话式信息录入
│   ├── compressor.md       #   LLM 语义压缩指南
│   ├── story_analyzer.md   #   故事记忆提取
│   ├── persona_analyzer.md #   性格行为提取（含时代适配）
│   ├── story_builder.md    #   story.md 生成模板
│   ├── persona_builder.md  #   persona.md 五层结构模板
│   ├── merger.md           #   增量 merge 逻辑
│   └── correction_handler.md # 对话纠正处理
├── tools/                  # Python 工具
│   ├── pdf_parser.py       #   PDF 解析
│   ├── skill_writer.py     #   Skill 文件管理
│   └── version_manager.py  #   版本存档与回滚
├── characters/             # 生成的角色 Skill（gitignored）
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 背后的故事

[colleague-skill](https://github.com/titanwings/colleague-skill) 蒸馏了同事。
[ex-skill](https://github.com/therealXiaomanChu/ex-skill) 蒸馏了前任。
[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 蒸馏了名人的思维框架。

它们证明了一件事：蒸馏一个人是完全可行的。

那么——剧本杀中那些让你走不出来的角色呢？

情感本的魅力在于，你会在几个小时里成为另一个人，和另一群人建立真实的情感连接。故事结束了，但感情还在。那些没说出口的话、没做出的选择、那个让你念念不忘的人——你想再跟ta聊聊。

这就是 larp-skill 存在的意义。

**同事.skill** 蒸馏了人做什么。
**前任.skill** 蒸馏了你们之间的记忆。
**女娲** 蒸馏了人怎么想。
**剧本杀.skill** 蒸馏了一段故事中的情感。

---

## 许可证

MIT — 随便用，随便改，随便蒸馏。

---

<div align="center">

*那些走不出来的角色，值得被好好蒸馏。*

</div>
