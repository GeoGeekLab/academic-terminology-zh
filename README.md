# academic-terminology-zh:中文学术写作规范校正

[![CI](https://github.com/GeoGeekLab/academic-terminology-zh/actions/workflows/tests.yml/badge.svg)](https://github.com/GeoGeekLab/academic-terminology-zh/actions/workflows/tests.yml)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-compatible-222222)](https://agentskills.io/specification)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-stdlib_only-4c6ef5)
![Dataset](https://img.shields.io/badge/terms-2%2C060-009688)

<!-- GeoGeekLab VIS: BEGIN -->
<p align="center">
  <a href="https://github.com/GeoGeekLab/geogeeklab-visual-identity/tree/main/new-mascots/academic-terminology-zh"><img src="https://raw.githubusercontent.com/GeoGeekLab/geogeeklab-visual-identity/main/new-mascots/academic-terminology-zh/concept-readme-hero.svg" alt="Ink Crane, the Academic Terminology mascot" width="740"></a>
</p>
<!-- GeoGeekLab VIS: END -->


## 解决什么问题？

通用大语言模型生成的中文论文常存在用词不规范、英文机械直译以及语言口语化等问题，难以达到学术出版的要求。

## 核心功能与优势

`academic-terminology-zh` 是一款基于 GB 国标学术术语库的 [Agent Skill](https://agentskills.io/specification)。它为模型提供明确的学术表达基准：

- **术语标准化**：根据上下文将非标词汇自动修正为国家标准定名。
- **语体学术化**：压制口语与直译腔调，统一全文专业用语。
- **数据无损**：仅优化文字表达，不改变变量、公式、数据与研究结论。

## ⚡ What Can You Do With It?

你可以从一段方法描述开始，也可以让 Agent 检查一整篇论文。Skill 把专业术语检索接入写作过程，让术语选择和语言润色一起完成。

| 你需要什么 | Skill 如何帮助 |
| --- | --- |
| **专业术语支持** | 覆盖海洋学、人工智能、遥感、统计学四个领域 |
| **随时查询** | 仓库自带 2,060 条术语索引，可在本地离线检索 |
| **轻量运行** | Python 3.10+、标准库实现，无需服务端组件 |
| **结合语境选词** | Agent 判断学科与段落语境；CLI 提供可复现的词面检索 |
| **加入自己的术语** | 支持 CSV / JSONL 导入，并自动发现新增领域 |

这里有一个关键分工：**CLI 帮你找到术语，Agent 帮你把术语用对。**

## 🚀 Quick Start

先看看词表里有什么。从仓库根目录运行以下命令，即可列出当前可用的领域及术语数量。

```bash
git clone https://github.com/GeoGeekLab/academic-terminology-zh.git
cd academic-terminology-zh
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
```

当前四个内置领域的预期计数：

```text
artificial_intelligence: 75
oceanography: 1175
remote_sensing: 594
statistics: 216
```

### Prompt-driven install

使用 Codex？可以直接让它完成安装、复制词表和验证。将下面的 Prompt 交给 Codex：

```text
从 https://github.com/GeoGeekLab/academic-terminology-zh 安装 `academic-terminology-zh` 到当前项目。将 `.agents/skills/academic-terminology-zh/` 和 `data/gb_terminology_databases/` 放入项目对应目录；运行 `lookup.py --stats` 和单元测试，确认四个领域合计 2,060 条记录。
```

### 1-minute demo

想看看它如何修改一段中文学术文字？在支持 Agent Skills 的 Codex 工作区中，使用下面的示例：

```text
$academic-terminology-zh
请对以下中文学术论文的方法部分进行专业润色，
规范术语及学术表达，保持研究方法、概念、变量、
公式、数值和结论不变。直接输出修改稿。

[粘贴正文]
```

如果你想先核对某个术语，也可以直接运行 CLI。例如，查询“散射系数”，或同时从统计学与人工智能领域查找“回归分析”：

```bash
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "散射系数" --detail
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "回归分析" --domain statistics --domain artificial_intelligence --json
```

## 📊 Dataset

这些术语来自四个学科的 8 项 GB/T 标准，并整理为便于检索的结构化索引。你可以查看中文名、英文名、缩写、别名与来源信息，再结合研究语境作出选择。

| Domain | Slug | Terms |
| --- | --- | ---: |
| 海洋学 | `oceanography` | 1,175 |
| 人工智能 | `artificial_intelligence` | 75 |
| 遥感 | `remote_sensing` | 594 |
| 统计学 | `statistics` | 216 |
| **Total** | **4 domains · 8 GB/T standards** | **2,060** |

**Public index schema:** `id`, `zh`, `en`, `abbr`, `aliases_zh`, `aliases_en`, `standard`, `clause`, `physical_pdf_pages`, `verification`.

公开索引聚焦术语及其来源信息。需要进一步查看完整定义时，可以使用 `--db` 加载另行获取的完整本地数据库。原始国标 PDF、定义全文和审校中间文件不随公开索引发布。

## ⚙️ Architecture

写作时，Skill 会根据任务选择相关领域，并在需要时调用术语检索。你可以专注于论文内容，检索工具负责提供候选术语与来源字段。

```text
Academic writing prompt
        │
        ▼
   SKILL.md                 ← writing behavior / domain routing
        │
        ├── on-demand lookup ──► scripts/lookup.py
        │                            │
        │                            ├── data/gb_terminology_databases/
        │                            └── custom_terms/<domain>/
        │
        └──► Agent writing / polishing / translation / review
                         │
                         ▼
                   Academic text
```

仓库将写作规则、检索脚本、测试和术语数据分开组织，便于独立使用或扩展。

**Repository layout**

```text
.
├── .agents/skills/academic-terminology-zh/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── lookup.py
│   │   └── import_terms.py
│   ├── references/usage.md
│   ├── tests/
│   └── evals/
├── data/gb_terminology_databases/
│   ├── oceanography/indexes/terms.csv
│   ├── artificial_intelligence/indexes/terms.csv
│   ├── remote_sensing/indexes/terms.csv
│   └── statistics/indexes/terms.csv
└── custom_terms/
```

## 🛠 CLI

需要检查具体术语、查看来源字段，或切换本地数据库？这些操作都可以直接在命令行完成。

```bash
# List domains and entry counts
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats

# Inspect source fields, definitions when available
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "频率" --detail

# Load an external full database
python .agents/skills/academic-terminology-zh/scripts/lookup.py --db path/to/gb_terminology_databases.zip --q "回归分析" --json
```

| Flag | Function |
| --- | --- |
| `--q TERM` | 检索中文 / 英文术语；可重复 |
| `--domain SLUG` | 领域过滤；可重复 |
| `--detail` | 输出定义和来源等扩展字段（取决于数据源） |
| `--json` | 结构化输出 |
| `--stats` | 领域及记录数 |
| `--limit N` | 每个查询最多返回 `1–20` 条；默认 `5` |
| `--db PATH` | 切换 CSV 目录或数据库 ZIP |

完整参数与数据库加载规则见 [CLI reference](.agents/skills/academic-terminology-zh/references/usage.md)。

## 🧩 Extensions

你的研究方向不在内置的四个领域里？可以把经过核对的术语整理为 CSV 或 JSONL，然后导入自定义词表。新领域会自动进入检索范围。

下面以 `climate_science` 为例：

```bash
python .agents/skills/academic-terminology-zh/scripts/import_terms.py \
  --domain climate_science \
  --input sources/new_domain/terms.csv \
  --source "自定义术语来源"

python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
```

源数据入口：[国家标准全文公开系统](https://openstd.samr.gov.cn/) · [全国标准信息公共服务平台](https://std.samr.gov.cn/) · [术语在线](https://www.termonline.cn/)。

你也可以让 Codex 协助整理合法取得的专业资料：先核对术语与来源，再生成 CSV / JSONL，最后通过 `import_terms.py` 导入。字段规范和示例见 [Extension guide](.agents/skills/academic-terminology-zh/references/usage.md#-custom-domains)。

## 🧪 Testing & CI

修改术语库或检索脚本后，运行单元测试，确认写作工具与词表仍能正常配合。

```bash
python -m unittest discover -s .agents/skills/academic-terminology-zh/tests -v
```

GitHub Actions：Python **3.10 / 3.12**；单元测试、脚本编译、四领域数据计数验证。

## 🤝 Contributing

专业术语库会随着学科和研究实践不断扩展。如果你发现值得补充的术语、希望支持新的领域，或对检索及写作测试有改进建议，欢迎提交 Issue 或 Pull Request。

提交前请运行上述测试，并为新增词表记录清晰的来源信息。这有助于其他研究者理解和复用术语。

仓库目前尚未发布 `LICENSE` 文件。源码使用权限以仓库后续公布的许可条款为准。

---

**“清水出芙蓉，天然去雕饰。” —— 李白**
