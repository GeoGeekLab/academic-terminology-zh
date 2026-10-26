# v1.3: six GB/T terminology-standardization A/B cases

The six A/B test cases measure **only** Chinese scientific terminology quality
and GB/T index grounding. They do **not** test research methods, data leakage,
causal inference, numeric result evaluation, manuscript claim strength or
full-paper translation quality.

Each case is an **independently constructed Chinese editorial scenario**,
related to one source paper as background. It is **not quoted from that paper**
and does **not** imply the paper or its authors made any of the simulated
terminology mistakes. A brief attributed CC BY 4.0 English excerpt is retained
solely as a bibliographic source anchor.

## The six cases

| Case | GB/T terminology focus | Example source-index references |
| --- | --- | --- |
| 01 · Radiometry | Cross-standard canonical forms; radiance vs irradiance and bracket notation | GB/T 15920—2010 §3.2.13/17; GB/T 36299—2018 §2.9/11 |
| 02 · Remote-sensing image processing | Image enhancement, image fusion, geometric/radiometric correction; recorded aliases | GB/T 14950—2009 §5.190/195/198/199 |
| 03 · Oceanography | water mass, water system, oceanic front, seawater nutrients; distinct source clauses | GB/T 15920—2010 §2.1.44/45/59; GB/T 15921—2010 §3.2.25 |
| 04 · Statistics | confidence interval, prediction interval, sample mean and accepted aliases | GB/T 3358.1—2009 §1.15/28/30 |
| 05 · Resolution | image, ground and radiometric resolution vs IFOV, including alias scope | GB/T 14950—2009 §4.76/77/103/104 |
| 06 · Artificial intelligence | validation/test data, training, deep learning; alias recognition and missing-index limits | GB/T 41867—2022 §3.2.3/18/27/35 |

The committed CSV indexes include **23 explicitly referenced term records**.
`python evals/benchmark.py validate` now verifies the complete tuples
(domain, English name, Chinese main term, standard number, clause) against the
**committed index files**. This is an internal consistency check, **not**
independent verification against original official standard PDFs.

## Scoring rubric (human expert review is primary)

For each case, blind-review both model outputs against its four
`expected_checks` with 0 = fails, 1 = partly correct, 2 = correct:

- Standard Chinese term and English equivalence correct, without merging
  different physical/technical concepts.
- GB/T **standard number and clause are exact** and appropriate for the domain.
- Aliases present in the index are distinguished from primary terms; the
  evaluation must **not** penalize legitimate recorded aliases as errors.
- No fabricated GB/T sources, invented official definitions, or claim that a
  term absent from the *current index* is prohibited by all national standards.

Some cases include more than one of these checks; follow each item's
`expected_checks` rather than assuming a simple identical scoring formula.
`gold_reviewed=false` on every case, pending domain-expert review.

The existing `benchmark.py compare` routine generates only lexical proxy
metrics: whether accepted phrases or protected acronyms appear in an output.
These do **not** measure accurate clause-to-term pairing, source integrity or
actual professionalism. Do not present them as **accuracy**. The rubric review
must supply primary A/B findings.

## Controlled A/B setup

1. Use the **same model version**, task input, temperature, token budget and
   system prompts in two fresh sessions.
2. **Baseline:** run without the Skill or external term index.
3. **Skill:** run with academic-terminology-zh available, and capture actual
   lookup traces from the included GB/T term index.
4. Save complete unmodified outputs for both sessions. Do not engineer
   deliberately weak baseline answers.
5. Have at least two expert assessors review anonymously. A fully correct
   baseline result is a valid tie; an inferior Skill result must also be shown.
6. Report term and source-clause correctness with denominators. Provide
   illustrative excerpts only from actual captured runs.

Run:

```bash
python evals/benchmark.py validate
python evals/benchmark.py template --out results/paired.jsonl
# Populate actual baseline and Skill outputs, unchanged.
python evals/benchmark.py compare --outputs results/paired.jsonl --out results/report.json
```

**No actual model A/B outputs or measured improvements ship with this branch.**

The six references are real attributed CC BY 4.0 papers. The written Chinese
cases are synthetic examples not taken from those papers. GB/T source indexes
have a separate unresolved redistribution-rights inventory; see
[DATA_RIGHTS.md](../DATA_RIGHTS.md).
