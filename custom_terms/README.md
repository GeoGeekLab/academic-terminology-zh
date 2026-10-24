# Custom terminology domains

用 `.agents/skills/academic-terminology-zh/scripts/import_terms.py` 导入已经整理和核对的 CSV/JSONL。

每个领域位于 `custom_terms/<domain>/indexes/terms.csv`，例如 `custom_terms/climate_science/indexes/terms.csv`。

检索器自动发现新领域；不需要修改四个内置领域。新增内容默认为 `imported_unverified`，除非明确提供并有依据支持核验状态。
