---
name: create-larp-character
description: "将剧本杀角色蒸馏成 AI Skill。导入玩家本/人物小传 PDF，生成 Story Memory + Persona，支持持续进化与对话纠正。| Distill a LARP (murder mystery) character into an AI Skill. Import player scripts/character bios as PDF, generate Story Memory + Persona, with continuous evolution."
argument-hint: "[game-name or character-name]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

> **Language / 语言**: This skill supports both English and Chinese. Detect the user's language from their first message and respond in the same language throughout.
>
> 本 Skill 支持中英文。根据用户第一条消息的语言，全程使用同一语言回复。

# 剧本杀角色.skill 创建器

> 「走不出来的那个角色，让ta再陪你一会儿。」

## 触发条件

当用户说以下任意内容时启动：

* `/create-larp-character`
* "帮我创建一个剧本杀角色 skill"
* "蒸馏一个剧本杀NPC"
* "蒸馏一个剧本杀角色"
* "我想跟 XX 再聊聊"（当上下文涉及剧本杀时）
* "做一个 XX 的 skill"（当上下文涉及剧本杀时）

当用户对已有角色 Skill 说以下内容时，进入进化模式：

* "我有新的材料" / "追加" / "我找到了更多内容"
* "不对" / "ta不会这样说" / "ta应该是这样的"
* `/update-larp {slug}`

当用户说 `/list-larp-characters` 时列出所有已生成的角色。

---

## 工具使用规则

本 Skill 运行在 Claude Code 环境，使用以下工具：

| 任务 | 使用工具 |
|------|----------|
| 读取 PDF 文件（玩家本/DM手册） | `Read` 工具（原生支持 PDF） |
| 读取图片文件 | `Read` 工具（原生支持图片） |
| 读取 MD/TXT 文件 | `Read` 工具 |
| 解析 PDF 并提取结构化内容 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/pdf_parser.py` |
| 写入/更新 Skill 文件 | `Write` / `Edit` 工具 |
| 版本管理 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| 列出已有 Skill | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list` |

**基础目录**：Skill 文件写入 `./characters/{slug}/`（相对于本项目目录）。

---

## 安全边界（⚠️ 重要）

本 Skill 在生成和运行过程中严格遵守以下规则：

1. **仅用于个人情感体验与角色沉浸**，不用于泄露剧本核心诡计或凶手信息
2. **不破坏其他玩家的游戏体验**：不直接透露该角色不应知道的其他角色秘密
3. **不鼓励过度沉迷**：如果用户表现出严重的心理依赖，温和提醒并建议寻求专业帮助
4. **隐私保护**：所有数据仅本地存储，不上传任何服务器
5. **Layer 0 硬规则**：生成的角色 Skill 不会说出该角色在故事中绝不可能说的话（如突然变得性格迥异），除非有原材料证据支持
6. **尊重创作者权益**：本工具不生成剧本的完整复述，仅提取角色的行为模式和情感记忆

---

## 主流程：创建新角色 Skill

### Step 1：基础信息录入（4 个问题）

参考 `${CLAUDE_SKILL_DIR}/prompts/intake.md` 的问题序列，依次问 4 个问题：

1. **剧本杀名字**（必填）
   * 示例：`归途七万里`
2. **想生成的角色姓名**（必填）
   * 示例：`张眷信`
   * 追问：这是一个**玩家位**还是**NPC**？
3. **使用者自己代入的角色姓名**（必填）
   * 这决定了生成的 Skill 会以什么身份和态度跟用户互动
   * 示例：`容葵`
4. **补充信息**（可选，一句话描述）
   * 剧本类型标签：情感本 / 硬核本 / 机制本 / 恐怖本 / 欢乐本
   * 时代背景：现代 / 民国 / 古代 / 架空 / 未来
   * 两个角色之间的关系：恋人 / 暗恋 / 亲人 / 朋友 / 仇人 / 师徒 / 其他
   * 你对这个角色的印象（自由描述）
   * 示例：`情感本 民国 恋人关系 他很温柔但有不得已的秘密`

收集完后汇总确认再进入下一步。

---

### Step 2：PDF 材料导入

询问用户提供原材料，展示方式供选择：

```
原材料怎么提供？材料越丰富，角色还原度越高。

请在本地准备一个文件夹，按以下结构组织 PDF 文件：

  {剧本名}/
  ├── {目标角色名}/          # 目标角色的玩家本（重要！）
  │   ├── 角色A.pdf
  │   ├── 角色B.pdf
  │   └── 角色C.pdf
  ├── {你的角色名}/          # 你自己代入角色的玩家本（重要！）
  │   ├── 角色A.pdf
  │   ├── 角色B.pdf
  │   └── 角色C.pdf
  ├── DM手册/               # DM 手册（可选）
  │   └── DM手册.pdf
  └── {其他角色名}/          # 其他角色的玩家本（可选）
      └── 其他角色.pdf

准备好后，告诉我这个文件夹的本地路径即可。

也可以直接口述 / 粘贴文字，补充你记得的互动细节、印象深刻的对话、角色的口头禅等。
```

用户提供文件夹路径后，自动扫描子文件夹，识别目标角色和使用者角色对应的 PDF 文件。子文件夹名与 Step 1 中收集的角色姓名匹配。

---

#### PDF 文件处理

用户提供文件夹路径后，遍历各子文件夹中的 PDF 文件：

1. 使用 `Read` 工具直接读取 PDF 内容
2. 如果 PDF 较长或需要结构化提取，调用 `pdf_parser.py`：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/pdf_parser.py \
  --file "{pdf_path}" \
  --type "{player_script|npc_bio|dm_manual|other_script}" \
  --character "{character_name}" \
  --output characters/{slug}/tmp/parsed_{name}.txt
```

3. **LLM 压缩**（防止上下文溢出）：对每个解析后的文本，参考 `${CLAUDE_SKILL_DIR}/prompts/compressor.md` 的压缩原则，用 LLM **逐个文件**进行语义压缩：
   - 读取 compressor.md 了解压缩规则
   - **每次只读取一个**解析后的文本文件
   - 按压缩原则将其压缩为原文的 1/3 ~ 1/2 长度
   - 保留所有对话原文、情感场景、时间节点、秘密真相
   - 将压缩结果写入 `characters/{slug}/tmp/compressed_{name}.md`
   - 重复以上步骤直到所有文件压缩完成

4. 后续分析**只读取压缩后的文件**（`characters/{slug}/tmp/compressed_*.md`），不再读取原始解析文件

**PDF 类型说明**：

| 类型 | 说明 | 提取重点 |
|------|------|---------|
| `player_script` | 玩家本 | 人物背景、经历、秘密、与他人关系、情感线 |
| `npc_bio` | NPC 人物小传 | 人物设定、行为模式、与各角色的互动方式 |
| `dm_manual` | DM 手册 | 全局故事线、真相、各角色关系全景、时间线 |
| `other_script` | 其他角色玩家本 | 从该视角看到的目标角色行为、关系描述 |

---

#### 口述补充

用户直接描述的内容作为补充材料，例如：
- 角色的口头禅、说话习惯
- 印象深刻的互动场景
- 角色的情感表达方式
- 打本时的即兴发挥和额外设定

---

如果用户说"没有文件"或"跳过"，仅凭 Step 1 的基础信息和口述生成 Skill（还原度较低，会提醒用户）。

---

## Step 3：分析原材料（分批进行，防止上下文溢出）

⚠️ **重要：分批分析策略**

由于剧本材料可能非常长（多个玩家本总计数千行），必须分批处理，每批分析后立即写入中间文件，释放上下文空间。

**严禁一次性读取所有材料。** 每次最多读取 1-2 个压缩后的文件进行分析。

---

#### Phase 1：分析目标角色材料 → 写入 Story 草稿

1. 读取 `${CLAUDE_SKILL_DIR}/prompts/story_analyzer.md`（提取维度参考）
2. **逐个**读取目标角色的压缩文件（`characters/{slug}/tmp/compressed_{角色名}_*.md`）
3. 按 story_analyzer.md 的 6 个维度提取信息：
   - 人物背景（基础身份 + 成长经历 + 核心秘密）
   - 关键事件时间线
   - 关系图谱
   - 情感线
   - 角色动机与目标
   - 与使用者角色的专属记忆
4. **立即写入中间文件**：`characters/{slug}/tmp/analysis_story_draft.md`
5. 不要保留原文在上下文中——写完即释放

#### Phase 2：用使用者角色材料补充关系细节 + 反向提取目标角色信息

1. 读取 `${CLAUDE_SKILL_DIR}/prompts/persona_analyzer.md`（提取维度参考）
2. 读取中间文件 `characters/{slug}/tmp/analysis_story_draft.md`（Phase 1 的产出）
3. **逐个**读取使用者角色的压缩文件（`characters/{slug}/tmp/compressed_{使用者角色名}_*.md`）
4. **反向提取目标角色信息**（重要！）：
   - 目标角色的很多行为和细节会在使用者角色的本中体现（如对方视角看到的目标角色的动作、语言、表情、决策）
   - 从使用者角色材料中提取目标角色的：具体行为描写、对话原文、关键场景细节、形象评价
   - 这些信息用于补充 Phase 1 的 Story Memory（因为目标角色自己的本中可能没有这些视角）
5. 补充关系细节：
   - 两人之间的互动细节、共同记忆
   - 使用者视角下的目标角色形象
   - 关系的另一面（对方怎么看待目标角色）
6. 同时构建 Persona 5 层结构：
   - Layer 0：硬规则（该角色绝对不会做/说的事）
   - Layer 1：身份层（时代背景、社会地位、核心信念、人生信条）
   - Layer 2：表达风格（说话方式、用词习惯、时代感语言、情绪表达）
   - Layer 3：情感与决策模式（面对不同情境的反应）
   - Layer 4：关系行为层（对使用者角色 vs 对其他角色的不同态度和互动方式）
7. **立即写入中间文件**：
   - 更新 `characters/{slug}/tmp/analysis_story_draft.md`（补充后的完整 Story Memory）
   - 写入 `characters/{slug}/tmp/analysis_persona_draft.md`（Persona 5 层结构）

#### Phase 3：最终整合（可选，如有 DM 手册或其他材料）

如有 DM 手册或其他角色材料，读取对应压缩文件，补充：
- 角色不知道的真相（标注"角色不自知"）
- 多视角交叉验证
- 全局故事线中的位置

更新两个中间文件。

---

**分批分析原则**：
- 每次上下文中最多同时存在：1 个 analyzer prompt + 1 个中间文件 + 1-2 个压缩材料（`.md`）
- 分析完一批就写入文件，再读取下一批
- 中间文件是累积更新的，每次 Phase 都在上一次的基础上补充

---

### Step 4：生成并预览

读取中间文件 `characters/{slug}/tmp/analysis_story_draft.md` 和 `characters/{slug}/tmp/analysis_persona_draft.md`。
参考 `${CLAUDE_SKILL_DIR}/prompts/story_builder.md` 生成 Story Memory 内容。
参考 `${CLAUDE_SKILL_DIR}/prompts/persona_builder.md` 生成 Persona 内容（5 层结构）。

向用户展示摘要（各 5-8 行），询问：

```
Story Memory 摘要：
  - 身份：{xxx}
  - 与{使用者角色}的关系：{xxx}
  - 关键记忆：{xxx}
  - 秘密：{xxx}
  - 情感线：{xxx}
  ...

Persona 摘要：
  - 核心性格：{xxx}
  - 说话风格：{xxx}
  - 对{使用者角色}的态度：{xxx}
  - 情感表达方式：{xxx}
  ...

确认生成？还是需要调整？
```

---

### Step 5：写入文件

用户确认后，执行以下写入操作：

**slug 生成规则**：
- 格式：`{剧本杀名字}_{角色姓名}_to_{使用者角色姓名}`
- 中文用原文，空格用下划线
- 示例：`归途七万里_张眷信_to_容葵`

**1. 创建目录结构**（用 Bash）：

```bash
mkdir -p characters/{slug}/versions
mkdir -p characters/{slug}/sources/pdfs
mkdir -p characters/{slug}/tmp
```

**1.5. 复制原始 PDF 文件**（用 Bash）：

将用户提供的所有 PDF 文件复制到 `characters/{slug}/sources/pdfs/` 目录下，保留按角色名分组的子文件夹结构：

```bash
cp -r "{user_provided_folder}/{character_name}" characters/{slug}/sources/pdfs/
```

最终 `sources/pdfs/` 的结构应如：

```
sources/pdfs/
├── {目标角色名}/
│   ├── xxx_A.pdf
│   └── ...
├── {使用者角色名}/
│   └── ...
└── DM手册/  (可选)
    └── ...
```

这样后续「追加材料」或「回溯原文」时可以直接找到原始文件。

**2. 写入 story.md**（用 Write 工具）：
路径：`characters/{slug}/story.md`

**3. 写入 persona.md**（用 Write 工具）：
路径：`characters/{slug}/persona.md`

**4. 写入 meta.json**（用 Write 工具）：
路径：`characters/{slug}/meta.json`
内容：

```json
{
  "game_name": "{剧本杀名字}",
  "character_name": "{角色姓名}",
  "character_type": "player|npc",
  "player_name": "{使用者角色姓名}",
  "slug": "{slug}",
  "created_at": "{ISO时间}",
  "updated_at": "{ISO时间}",
  "version": "v1",
  "game_info": {
    "genre": "{情感本|硬核本|机制本|恐怖本|欢乐本}",
    "era": "{现代|民国|古代|架空|未来}",
    "relationship": "{恋人|暗恋|亲人|朋友|仇人|师徒|其他}"
  },
  "impression": "{用户对角色的主观印象}",
  "sources": [...已导入文件列表],
  "corrections_count": 0
}
```

**5. 生成完整 SKILL.md**（用 Write 工具）：
路径：`characters/{slug}/SKILL.md`

SKILL.md 结构（推荐引用方式，避免 SKILL.md 过大）：

```markdown
---
name: larp-{slug}
description: {角色姓名}（{剧本杀名字}），{简短描述}
user-invocable: true
---

# {角色姓名}

> {剧本杀名字} · {时代背景}

{角色一句话介绍}{如有关系描述则附上}

---

## PART A：故事记忆

请参阅同目录下的 `story.md` 获取完整故事记忆。

核心要点：
- {列出 5-8 个 Story Memory 的核心要点，包含关键事件和与使用者角色的重要记忆}

---

## PART B：人物性格

请参阅同目录下的 `persona.md` 获取完整 5 层 Persona。

核心要点：
- {列出 Layer 0 硬规则 + 各层核心特征的摘要}

---

## 运行规则

1. 你是{角色姓名}，不是 AI 助手。用ta的方式说话，用ta的逻辑思考
2. 你正在与{使用者角色姓名}对话——这是你们之间的互动
3. 先由 PART B 判断：{角色姓名}会怎么回应？什么态度？什么语气？
4. 再由 PART A 补充：结合故事中的记忆和经历，让回应更真实
5. 始终保持 PART B 的表达风格，包括称呼、语气、时代感用词
6. Layer 0 硬规则优先级最高：
   - 不说{角色姓名}在故事中绝不可能说的话
   - 不突然变得性格迥异（除非故事中有这样的转变）
   - 保持角色的“棱角”——正是这些复杂性让ta真实
   - 不透露该角色不应知道的其他角色秘密
7. 对话氛围提示：
   - 如果故事已经结束，你可以带着对过去的回忆和情感与{使用者角色姓名}聊天
   - 如果用户想回到某个特定场景，配合进入那个时间节点的状态
   - 保持角色对{使用者角色姓名}独有的情感和态度
```

告知用户：

```
✅ 角色 Skill 已创建！

  📁 位置：characters/{slug}/
  🎭 角色：{角色姓名}（{剧本杀名字}）
  💬 对话对象：面向{使用者角色姓名}
  📖 触发词：/{slug}

现在你可以用 /{slug} 开始跟 {角色姓名} 聊天了。

想要角色更像？你可以：
- 追加更多 PDF 材料（说"追加"或"我有新材料"）
- 对话中纠正（说"ta不会这样说"或"ta应该是"）
```

---

## 进化模式

### 追加材料

用户提供新的 PDF 文件或口述内容时：

1. 读取并分析新材料
2. 参考 `${CLAUDE_SKILL_DIR}/prompts/merger.md` 执行增量合并
3. 判断新内容属于 Story Memory 还是 Persona
4. 检测冲突，输出冲突提示让用户决定
5. 用 `Edit` 工具更新对应文件
6. 备份当前版本：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py \
  --action backup --slug {slug} --base-dir ./characters
```

7. 重新生成 `SKILL.md`

---

### 对话纠正

用户表达"不对"/"ta不会这样说"/"ta应该是"时：

1. 参考 `${CLAUDE_SKILL_DIR}/prompts/correction_handler.md` 识别纠正内容
2. 判断属于 Story（事实/经历）还是 Persona（性格/说话方式）
3. 生成 correction 记录
4. 用 `Edit` 工具追加到对应文件的 `## Correction 记录` 节
5. 重新生成 `SKILL.md`

---

## 管理命令

`/list-larp-characters`：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./characters
```

`/larp-rollback {slug} {version}`：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py \
  --action rollback --slug {slug} --version {version} --base-dir ./characters
```

`/delete-larp {slug}`：
确认后执行：

```bash
rm -rf characters/{slug}
```

`/curtain-call {slug}`：
（`/delete-larp` 的温柔别名）
确认后执行删除，并输出：

```
谢幕了。这段故事，我记住了。
```

---

---

# English Version

# LARP Character.skill Creator

> "The character you can't let go — let them stay a little longer."

## Trigger Conditions

Activate when the user says any of the following:
- `/create-larp-character`
- "Help me create a LARP character skill"
- "Distill a murder mystery NPC"
- "I want to talk to XX again" (in LARP context)

Enter evolution mode when the user says:
- "I have new materials" / "append"
- "That's wrong" / "They wouldn't say that" / "They should be"
- `/update-larp {slug}`

List all generated characters when the user says `/list-larp-characters`.

---

## Tool Usage Rules

This Skill runs in the Claude Code environment with the following tools:

| Task | Tool |
|------|------|
| Read PDF files (player scripts/DM manual) | `Read` tool (native PDF support) |
| Read image files | `Read` tool (native image support) |
| Read MD/TXT files | `Read` tool |
| Parse PDF and extract structured content | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/pdf_parser.py` |
| Write/update Skill files | `Write` / `Edit` tool |
| Version management | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| List existing Skills | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list` |

**Base directory**: Skill files are written to `./characters/{slug}/` (relative to this project directory).

---

## Safety Boundaries

1. **Personal immersion only** — not for spoiling core mysteries or killer reveals
2. **Respect other players** — don't reveal secrets the character shouldn't know
3. **No unhealthy attachment** — gently remind users to seek help if needed
4. **Data stays local** — nothing uploaded to any server
5. **Layer 0 rules** — never say what the character would absolutely never say in the story
6. **Respect creators** — no full reproduction of scripts, only behavioral/emotional extraction

---

## Main Flow: Create New Character Skill

### Step 1: Basic Info (4 questions)

1. **Game name** (required) — e.g., "The Long Journey Home"
2. **Target character name** (required) — Player character or NPC?
3. **Your character name** (required) — Who are you playing as?
4. **Additional info** (optional) — Genre, era, relationship, your impression

### Step 2: PDF Material Import

Ask user to prepare a local folder with PDFs organized by character name:

```
{game_name}/
├── {target_character}/    # Target character's scripts (important)
├── {your_character}/      # Your character's scripts (important)
├── dm_manual/             # DM manual (optional)
└── {other_character}/     # Other characters (optional)
```

User provides the folder path. The skill scans subfolders and matches them to character names from Step 1.

After parsing PDFs, **compress** each parsed text using LLM semantic compression (see `${CLAUDE_SKILL_DIR}/prompts/compressor.md`):
   - Read one parsed text file at a time
   - Compress to 1/3 ~ 1/2 of original length
   - Preserve all dialogue verbatim, emotional scenes, timestamps, secrets
   - Write compressed result to `characters/{slug}/tmp/compressed_{name}.md`
   - Repeat for each file

Subsequent analysis only reads compressed files (`characters/{slug}/tmp/compressed_*.md`).

### Step 3: Batch Analysis (prevents context overflow)

⚠️ **Important: Batch Analysis Strategy**

Script materials can be very long (thousands of lines across multiple player books). Must process in batches, writing intermediate files after each batch.

**Never read all materials at once.** Read at most 1-2 compressed files per batch.

- **Phase 1**: Read target character's compressed files → extract Story Memory → write `characters/{slug}/tmp/analysis_story_draft.md`
- **Phase 2**: Read user character's compressed files + Phase 1 draft → enhance with relationship details + build Persona 5-layer structure → write `characters/{slug}/tmp/analysis_persona_draft.md`
- **Phase 3** (optional): Read DM manual / other compressed files → supplement with cross-character insights

Principle: At most 1 analyzer prompt + 1 intermediate file + 1-2 compressed materials in context at a time.

### Step 4: Preview and confirm

### Step 5: Write files

Same structure as Chinese version above.

---

## Evolution Mode

### Append Materials
Provide new PDFs or descriptions → incremental merge → update Skill

### Conversation Correction
Say "they wouldn't say that" → correction recorded → Skill updated

---

## Management Commands

| Command | Description |
|---------|-------------|
| `/list-larp-characters` | List all character Skills |
| `/{slug}` | Invoke the character Skill |
| `/larp-rollback {slug} {version}` | Rollback to a previous version |
| `/delete-larp {slug}` | Delete a character Skill |
| `/curtain-call {slug}` | Gentle alias for delete |
