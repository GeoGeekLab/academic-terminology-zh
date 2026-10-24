# academic-terminology-zh

[![Agent Skills](https://img.shields.io/badge/Agent-Skill-111827)](https://agentskills.io/specification)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-local--first-555555)

面向中文学术论文起草、润色、英译中和全文术语一致性检查的 Agent Skill。按需检索专业词表，在原有研究方法、变量、数值和结论不变的前提下改善中文学术表达。

目前支持四个逻辑领域：**海洋学、机器学习相关的人工智能术语、遥感、统计学**。用户也可添加其他学科词表。

## Install

从项目根目录克隆仓库，Codex 可识别 `.agents/skills/academic-terminology-zh/SKILL.md`：

```bash
git clone https://github.com/GeoGeekLab/academic-terminology-zh.git
cd academic-terminology-zh
```

也可以向 Codex 输入：

> 请将 https://github.com/GeoGeekLab/academic-terminology-zh 安装到当前项目，配置 `academic-terminology-zh` Skill，并运行基础测试与术语检索检查。

**数据状态：** 当前公开仓库部署的是 Skill 源码。四领域数据库归档尚未同步到 GitHub。已有本地数据库的用户可将 `gb_terminology_databases.zip` 放入 `data/`，或使用 `--db` 指向解压目录；请勿将原始国标 PDF 在未确认公开分发权限的情况下上传。

## Usage

在 Codex 中：

```text
$academic-terminology-zh
请对以下中文学术论文的方法部分进行专业润色。
优化学术表达及术语使用，保持研究方法、专业概念、变量、
公式、数值和结论准确，直接输出润色后的正文。
```

查询术语：

```bash
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "散射系数" --detail
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "回归分析" --domain statistics --domain artificial_intelligence --json
```

通过 `--db path/to/gb_terminology_databases.zip` 或环境变量 `GB_TERMINOLOGY_DB_ROOT` 指定数据库。Python 3.10+，脚本仅使用标准库。

## Data model

本地数据快照目前包含 2,060 条记录，涵盖八份国家标准：

| Domain | Slug | Entries |
|---|---|---:|
| 海洋学 | `oceanography` | 1,175 |
| 机器学习相关的 AI 术语 | `artificial_intelligence` | 75 |
| 遥感 | `remote_sensing` | 594 |
| 统计学 | `statistics` | 216 |

保留中英文术语、别名、定义、标准号、条款、PDF 来源页码和核验信息。词表是写作参照；跨领域同名概念会保留独立记录。

## Custom domains

将整理好的 CSV/JSONL 导入 `custom_terms/<domain>/indexes/terms.csv`。新领域会被检索器自动发现：

```bash
python .agents/skills/academic-terminology-zh/scripts/import_terms.py --domain climate_science --input sources/new_domain/terms.csv --source "词表名称"
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
```

源材料可从 [国家标准全文公开系统](https://openstd.samr.gov.cn/)、[全国标准信息公共服务平台](https://std.samr.gov.cn/)和[术语在线](https://www.termonline.cn/)查询。官方 PDF 需先提取和校对为结构化术语表，再调用导入脚本。

可向 Codex 输入：

> 请依据 `sources/new_domain/` 中的合法取得的权威资料创建 `climate_science` 术语库；提取并核对中英文术语及来源，生成 CSV/JSONL，运行 `import_terms.py` 导入 `custom_terms/climate_science/`，最后完成查询测试。

## Tests

```bash
python -m unittest discover -s .agents/skills/academic-terminology-zh/tests -v
```

## Repository layout

```text
.agents/skills/academic-terminology-zh/
    SKILL.md
    scripts/lookup.py
    scripts/import_terms.py
    references/usage.md
    tests/
    evals/
custom_terms/
data/
README.md
```

代码与数据可在同一仓库组织；实际发布的数据范围以相应来源的授权条件为准。源码许可证尚待项目维护者选择。
