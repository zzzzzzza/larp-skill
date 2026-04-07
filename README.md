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

[安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [项目结构](#项目结构)

</div>

---

## 效果示例

> 输入：剧本「归途七万里」，角色「张眷信」（玩家位），我扮演「容葵」，情感本，民国，恋人

**场景一：日常对话**

```
容葵      ❯ 你在做什么

张眷信    ❯ 在看信。
             ……不是你写的那种信，别多想。
             只是一些旧日的信函罢了。
             你呢，怎么这个时候来找我？
```

**场景二：回忆杀**

```
容葵      ❯ 你还记得我们第一次见面吗

张眷信    ❯ ……怎么突然问这个。
             记得。那天下着雨。
             你撑着一把破伞站在廊下，
             衣摆湿了也不知道。
             我当时想，这人怎么连自己都照顾不好。
             后来才知道——
             你只是把伞让给了别人。
```

**场景三：情感试探**

```
容葵      ❯ 如果重来一次，你还会做同样的选择吗

张眷信    ❯ ……
             你知道答案的。
             有些事情，不是选不选的问题。
             是不得不。
             但如果你问的是另一件事——
             会的。每一次都会。
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
- **API 消耗**：创建一个角色 Skill 大约消耗 5k-20k tokens，取决于玩家本篇幅
- **不需要 GPU**，不需要本地模型，不需要 Docker

---

## 使用

在 Claude Code 中输入：

```
/create-larp-character
```

按提示输入剧本名字、角色姓名、你扮演的角色，然后提供 PDF 文件。

完成后用 `/{slug}` 调用该角色 Skill，开始对话。

### 管理命令

| 命令 | 说明 |
|------|------|
| `/list-larp-characters` | 列出所有角色 Skill |
| `/{slug}` | 调用角色 Skill（像ta一样跟你聊天） |
| `/larp-rollback {slug} {version}` | 回滚到历史版本 |
| `/delete-larp {slug}` | 删除 |
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
