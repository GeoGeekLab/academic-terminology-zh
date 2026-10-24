# 使用说明

## 数据定位

克隆后默认使用仓库自带的 `data/gb_terminology_databases/` 四领域索引。也支持通过 `--db` 或环境变量 `GB_TERMINOLOGY_DB_ROOT` 切换到自己持有的完整数据库 ZIP 或解压目录。公开仓库不包含原始 PDF 和标准定义全文。

数据库的四个逻辑领域：

- `oceanography`：海洋学
- `artificial_intelligence`：用于机器学习写作的人工智能术语基础
- `remote_sensing`：遥感
- `statistics`：统计学

仓库索引有 2,060 条记录，来自八份 GB/T 标准；包含条款、英文、别名、来源页和核验标记。完整定义请使用单独取得的本地数据库。

## 命令

`python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats` 查看领域。用 `--q` 重复输入查询词，`--domain` 多次指定领域。不指定领域检索全部。用 `--detail` 查看更多来源字段（只有配置完整数据库时才有定义），用 `--json` 输出 JSON。

扩展词表按 `custom_terms/<domain>/indexes/terms.csv` 读取。建议在仓库根目录运行命令。

## 导入扩展领域

先合法取得源材料，将结构化 CSV/JSONL 保存于 `sources/new_domain/`。使用 `import_terms.py --domain <slug> --input <file> --source <名称>`。如来源是 PDF，先提取并校对形成结构化词表。

推荐字段：`zh,en,definition,standard,clause,physical_pdf_pages,aliases_zh,aliases_en,source_url,verification`。每条至少填写中文或英文词和来源。无法确认的内容保留待核状态。

导入只修改 `custom_terms/`，不修改现有四库。运行 `lookup.py --stats` 与实际查询验证。
