# CLI & Data Reference

`academic-terminology-zh` · Python 3.10+ · stdlib only · local-first

## ⚡ Lookup

从仓库根目录执行：

```bash
SKILL=.agents/skills/academic-terminology-zh
python "$SKILL/scripts/lookup.py" --stats
python "$SKILL/scripts/lookup.py" --q "散射系数" --domain oceanography --domain remote_sensing --json
python "$SKILL/scripts/lookup.py" --q "回归分析" --detail
```

Windows PowerShell 可直接使用完整脚本路径：

```powershell
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
```

### Flags

| Option | Behavior | Default |
| --- | --- | --- |
| `--q TERM` | 中英文术语检索；支持重复参数 | — |
| `--domain SLUG` | 领域过滤；支持多个值 | 全部领域 |
| `--limit N` | 单次查询返回上限，范围 `1–20` | `5` |
| `--detail` | 扩展字段：定义、注释、核验标记等 | 关闭 |
| `--json` | JSON 输出 | 文本 |
| `--stats` | 输出领域计数 | 关闭 |
| `--in-definition` | 搜索 `definition` 字段；仅在数据包含定义时有效 | 关闭 |
| `--db PATH` | 使用指定 ZIP / 解压数据库目录 | 自动发现 |

`--q` 和 `--stats` 至少指定一个。`--detail` 展示字段取决于所加载的 CSV；公开索引没有定义全文。

### Query examples

```bash
# Multiple terms; same domain filter applies to each query
python .agents/skills/academic-terminology-zh/scripts/lookup.py \
  --q "频率" --q "回归分析" --domain statistics --json

# Search every configured domain
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "散射系数" --detail
```

检索使用 NFKC 归一化后的中英文词面匹配；优先精确名称和别名，随后匹配前缀与包含关系。多领域同名术语保留为多条候选，由 Agent 根据上下文判断。

## ⚙️ Data loading

```text
--db PATH
   ↓ (when unset)
GB_TERMINOLOGY_DB_ROOT
   ↓ (when unset)
Auto-discovery: repository / current working directory and parents
   ├── data/gb_terminology_databases.zip
   ├── gb_terminology_databases.zip
   ├── gb_terminology_databases/
   └── data/gb_terminology_databases/
```

公开仓库自带：

```text
data/gb_terminology_databases/
├── oceanography/indexes/terms.csv           # 1,175
├── artificial_intelligence/indexes/terms.csv #    75
├── remote_sensing/indexes/terms.csv          #   594
└── statistics/indexes/terms.csv              #   216
```

| Domain | Slug |
| --- | --- |
| 海洋学 | `oceanography` |
| 人工智能 | `artificial_intelligence` |
| 遥感 | `remote_sensing` |
| 统计学 | `statistics` |

指定完整本地数据库：

```bash
python .agents/skills/academic-terminology-zh/scripts/lookup.py \
  --db ./data/gb_terminology_databases.zip --q "回归分析" --detail
```

```powershell
$env:GB_TERMINOLOGY_DB_ROOT = "C:\research\gb_terminology_databases.zip"
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
```

## 🧩 Custom domains

新增领域无需改动内置数据库或修改领域列表。

### Input schema

CSV 表头示例：

```csv
zh,en,standard,clause,definition
数据同化,data assimilation,team-glossary-v1,,
```

最少提供 `zh` 或 `en` 之一，并提供 `standard`（或在导入命令中提供 `--source`）。其余字段按实际资料填写。

建议保留：`zh`, `en`, `standard`, `clause`, `definition`, `aliases_zh`, `aliases_en`, `physical_pdf_pages`, `source_url`, `verification`。

### Import

```bash
python .agents/skills/academic-terminology-zh/scripts/import_terms.py \
  --domain climate_science \
  --input sources/new_domain/terms.csv \
  --source "自定义术语来源"
```

导入位置：

```text
custom_terms/climate_science/indexes/terms.csv
```

| Import option | Purpose |
| --- | --- |
| `--domain SLUG` | 小写英文字母开头，可包含数字、`_` 和 `-` |
| `--input PATH` | CSV / JSONL 源文件 |
| `--source TEXT` | 输入没有 `standard` 时使用的来源名称 |
| `--out DIR` | 自定义词库根目录，默认 `custom_terms/` |

自动生成稳定 ID；依据 `standard + clause + zh + en` 去重。重复导入相同数据不会重复新增记录。未提供 `verification` 时标记 `imported_unverified`。

```bash
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
python .agents/skills/academic-terminology-zh/scripts/lookup.py --domain climate_science --q "数据同化" --json
```

### Source-to-index workflow

```text
Official source / domain glossary
             │
             ▼
      Extract + verify
             │
             ▼
         CSV / JSONL
             │
             ▼
        import_terms.py
             │
             ▼
custom_terms/<domain>/indexes/terms.csv
             │
             ▼
          lookup.py
```

资料入口：[国家标准全文公开系统](https://openstd.samr.gov.cn/) · [全国标准信息公共服务平台](https://std.samr.gov.cn/) · [术语在线](https://www.termonline.cn/)。PDF 先解析并核对为 CSV/JSONL，再执行导入。

**Prompt-driven extension**

> 根据 `sources/new_domain/` 中已取得的术语资料，为 `climate_science` 建立词表。抽取中文名、英文名、来源与条款，核对结果并写入 CSV/JSONL；使用 `import_terms.py` 导入，最后通过 `lookup.py --stats` 和示例术语检索验证。

## 🧪 Verification

```bash
python -m unittest discover -s .agents/skills/academic-terminology-zh/tests -v
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats --json
```

CI：Python 3.10 / 3.12；脚本编译、单元测试与四领域术语计数检查。
