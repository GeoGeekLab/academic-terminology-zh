# v1.3: six paper-grounded, high-difficulty Chinese terminology review cases

**Source vs test input must not be confused.** Each record references one
real, attributed CC BY 4.0 research article, and retains a short *verbatim*
English excerpt under `excerpt`. The actual A/B task is the independently
**constructed Chinese editorial scenario** in `input_text`. These deliberately
injected issues **must not be attributed to the paper's authors or presented
as quotations from their papers**.

Six different skills are tested:

| Case | Article's subject | Constructed editorial challenge |
| --- | --- | --- |
| challenge-01-radiometry | Remote-sensing water quality | Spectral radiance, irradiance and reflectance; bilingual mismatch |
| challenge-02-gamma-test-leakage | Deep-learning image enhancement | Synthetic low-light imagery, test-set tuning and unsupported generalization |
| challenge-03-density-transport | Subtropical nutrient relay | Lateral transport along density surfaces vs vertical mixing, 10–100 km |
| challenge-04-inference-interval | Cross-prediction inference | Population confidence interval vs individual prediction interval |
| challenge-05-lulc-document | Time-series LULC mapping | Preserve land-cover-only vs compound LULC labels across document sections |
| challenge-06-metrics-pairs | MARS-Net building extraction | IoU/F1 figures and dataset pairing, no false accuracy/generalization claim |

A conventional LLM may answer all six correctly. The task is to *measure*
whether the indexed Skill improves performance, not to create a deliberately
weak baseline. Cases 05 and 06 include out-of-index terminology, so the
Skill must neither hallucinate GB/T provenance nor force unsupported terms.

## Reproduce the controlled A/B experiment

1. Freeze a model name/version, runtime, sampling temperature, token budget,
   tool policy and system prompts. Register experiment metadata separately.
2. Run the same `task_prompt` in a clean **baseline** session without the
   Skill or term index.
3. Run the same `task_prompt` in a separate clean **Skill** session with
   academic-terminology-zh enabled. Capture actual tool/lookup logs.
4. Capture the two outputs *verbatim* and retain execution trace identifiers.
5. Ask at least two independent domain reviewers, blinded to treatment, to
   evaluate each item in `expected_checks` and record unsupported alterations,
   inappropriate standard claims, numbers, and unchanged-but-correct answers.
6. Compute proxy metrics and then report the pre-registered **human pass rates**
   with uncertainty. If outputs tie, report a tie. If the Skill is worse, report
   that result. Do not select only winning examples.

The benchmark does **not** run a language model; it validates inputs,
generates a paired response template, and scores simple string proxies.

From the repository root:

```bash
python evals/benchmark.py validate
python evals/benchmark.py template --out results/paired.jsonl
# The "task_prompt" field contains the identical input for both arms.
# Save genuine baseline/Skill responses in each row (never fabricated examples).
python evals/benchmark.py compare --outputs results/paired.jsonl --out results/report.json
```

The `results/` folder is ignored by Git; it may contain confidential drafts.
Do not commit any non-public manuscript, model log, or unlicensed excerpt.

## Evaluation scope

- **Primary outcome:** expert-reviewed pass/fail or rubric score for each
  `expected_checks` criterion. The repo does not currently automate this.
- **Secondary diagnostics:** concept phrase coverage, numeric/acronym literal
  retention, cross-case comparison. These diagnostics use substring matching.
  A semantically *incorrect* sentence can score 100%; this is *not* accuracy.
- **Source provenance:** source paper, DOI, authors and CC BY 4.0 source link.
  Article facts are referenced only where independently verified.
- **Legal distinction:** the cited English excerpts are CC BY 4.0; the
  created Chinese challenge inputs are **not** quotations or revisions from
  those papers. All six gold labels remain `gold_reviewed=false`.
- **Accuracy limitation:** only six scenarios, unbalanced difficulty; do not
  claim population-level accuracy, statistical significance, or a universal
  benefit until a larger independently reviewed sample and repeated model
  runs have been completed.

For source-data reuse and GB/T terms, see ../DATA_RIGHTS.md.
