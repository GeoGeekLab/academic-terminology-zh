---
name: academic-terminology-zh
description: 为中文学术论文起草、专业润色、英译中与术语一致性审校提供基于专业术语库的写作支持。适用于海洋学、机器学习、遥感、统计学及用户新增学科。Use for academic drafting, polishing, translation into Chinese, and terminology consistency review. Exclude casual writing and PDF database construction unless explicitly requested.
---

# 中文学术写作术语

面向论文正文输出：根据研究语境使用专业名称、中英文译名与缩写，保留方法、变量、公式、数值和结论。

1. 根据段落识别相关领域，可同时检索多个领域；尊重论文现有的术语约定。
2. 对影响概念准确性的术语按需小批量查询 `scripts/lookup.py`，通常一次 3–8 个词。普通语言润色不必逐词查库。
3. 内置四库和 `custom_terms/` 扩展库可同时检索。用 `--stats` 列出可用领域；库外术语依据专业语境处理。
4. 将检索结果作为用词参考；同名异义依语境区分。别名不能直接等同于错词。明显拼写错误和不一致可直接修正；涉及研究事实的歧义应保持原意并简要提示。
5. 默认直接交付正文。用户要求解释规范来源时再使用 `--detail` 并查看来源记录。

## Lookup

```bash
python .agents/skills/academic-terminology-zh/scripts/lookup.py --stats
python .agents/skills/academic-terminology-zh/scripts/lookup.py --q "回归分析" --domain statistics --domain artificial_intelligence --detail
```

可通过 `--db` 或 `GB_TERMINOLOGY_DB_ROOT` 指向本地数据库 ZIP/目录。新增领域位于 `custom_terms/<domain>/indexes/terms.csv`，无需修改脚本。见 `references/usage.md`。

正常写作不修改底层数据。扩展术语库时使用 `scripts/import_terms.py`；若来源是 PDF，应先核对并整理为 CSV/JSONL。


## Research-writing workflow integration

When another academic-writing Skill requests terminology support, use
scripts/handoff.py via stdin or --input. It emits read-only JSON mentions
with standard/clause and verification labels. Inspect labels and context;
do not mechanically replace aliases or override disciplinary conventions.
The host writing Skill remains responsible for editing text and verifying
facts. Integration/install instructions: repository integrations/README.md.
