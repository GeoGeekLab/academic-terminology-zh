# academic-terminology-zh

[![CI](https://github.com/GeoGeekLab/academic-terminology-zh/actions/workflows/tests.yml/badge.svg)](https://github.com/GeoGeekLab/academic-terminology-zh/actions/workflows/tests.yml)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-compatible-222222)](https://agentskills.io/specification)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-stdlib_only-4c6ef5)
![Dataset](https://img.shields.io/badge/terms-2%2C060-009688)

**Agent Skill for terminology-aware Chinese academic writing.**

面向中文学术论文的起草、润色、英译中与术语一致性检查。Agent 按需检索本地专业词表，根据上下文选择术语，并保持技术方法、变量、公式和数值准确。

## ⚡ Features

| Capability | Implementation |
| --- | --- |
| Four domains | 海洋学 · 人工智能 · 遥感 · 统计学 |
| Local-first | 2,060 条术语索引随仓库提供；离线检索 |
| Low overhead | Python 3.10+；标准库；无服务端组件 |
| Context-aware writing | Agent 负责语境判断；CLI 提供可复现的词面检索 |
| Extensible | CSV / JSONL 导入；自动发现自定义领域 |

## 🚀 Quick Start

```bash
git clone https://github.com/GeoGeekLab/academic-terminology-zh.git
cd academic-terminology-zh
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
```

预期领域计数：

```text
artificial_intelligence: 75
oceanography: 1175
remote_sensing: 594
statistics: 216
```

### Prompt-driven install

将以下 Prompt 交给 Codex，即可把 Skill 和随仓库发布的术语索引接入当前项目：

> 从 https://github.com/GeoGeekLab/academic-terminology-zh 安装 `academic-terminology-zh` 到当前项目。将 `.agents/skills/academic-terminology-zh/` 和 `data/gb_terminology_databases/` 放入项目对应目录；运行 `lookup.py --stats` 和单元测试，确认四个领域合计 2,060 条记录。

### 1-minute demo

在支持 Agent Skills 的 Codex 工作区中：

```text
$academic-terminology-zh
请对以下中文学术论文的方法部分进行专业润色，
规范术语及学术表达，保持研究方法、概念、变量、
公式、数值和结论不变。直接输出修改稿。

[粘贴正文]
```

也可直接查询：

```bash
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "散射系数" --detail
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "回归分析" --domain statistics --domain artificial_intelligence --json
```

## 📊 Dataset

| Domain | Slug | Terms |
| --- | --- | ---: |
| 海洋学 | `oceanography` | 1,175 |
| 人工智能 | `artificial_intelligence` | 75 |
| 遥感 | `remote_sensing` | 594 |
| 统计学 | `statistics` | 216 |
| **Total** | **4 domains · 8 GB/T standards** | **2,060** |

**Public index schema:** `id`, `zh`, `en`, `abbr`, `aliases_zh`, `aliases_en`, `standard`, `clause`, `physical_pdf_pages`, `verification`.

原始国标 PDF、定义全文及审校中间文件不在公开索引内。需要完整定义时，可使用 `--db` 加载另行获取的完整本地数据库。

## ⚙️ Architecture

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

新增学科使用 CSV / JSONL。导入后自动纳入检索范围：

```bash
python .agents/skills/academic-terminology-zh/scripts/import_terms.py \
  --domain climate_science \
  --input sources/new_domain/terms.csv \
  --source "自定义术语来源"

python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
```

源数据入口：[国家标准全文公开系统](https://openstd.samr.gov.cn/) · [全国标准信息公共服务平台](https://std.samr.gov.cn/) · [术语在线](https://www.termonline.cn/)。

新建领域时，可让 Codex 先将合法取得的源资料整理、核对为 CSV/JSONL，再调用 `import_terms.py`。字段规范及示例见 [Extension guide](.agents/skills/academic-terminology-zh/references/usage.md#-custom-domains)。

## 🧪 Testing & CI

```bash
python -m unittest discover -s .agents/skills/academic-terminology-zh/tests -v
```

GitHub Actions：Python **3.10 / 3.12**；单元测试、脚本编译、四领域数据计数验证。

## 🤝 Contributing

Issue / PR 可用于补充术语领域、改进检索和完善写作测试。提交前运行上述测试；新增词表应包含明确的来源信息。

仓库目前未配置 `LICENSE` 文件；源码许可条款以实际仓库后续发布内容为准。
