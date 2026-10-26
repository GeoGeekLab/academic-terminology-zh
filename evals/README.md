# Paired evaluation on real, licensed research excerpts (v1.3)

This benchmark uses **genuine short English excerpts** from six independently
published CC BY 4.0 papers. Metadata includes source URLs, DOIs, and licenses.
These are real-paper translation tasks, **not** a claim of evaluation on full
Chinese manuscripts. Chinese academic polishing requires independently
licensed Chinese text, or material supplied with permission; do not scrape
copyrighted papers to expand the dataset.

## Design: a controlled, paired experiment

1. Fix the model version, decoding settings, and evaluation samples.
2. **Baseline:** start a clean model session without this Skill. Give the
   paper excerpt and its exact prompt. Save the response verbatim.
3. **Skill:** start another clean session with academic-terminology-zh loaded
   and with the same prompt/settings. Confirm lookup is usable. Save response.
4. Blind human reviewers to which arm produced each response. Have a
   domain expert check terminology choice, meaning preservation, factual
   alterations, correct formulae/numbers and style. Record reviewer IDs,
   errors and disagreements; resolve disagreements independently.
5. Use the comparison script to compute transparent mechanical proxy metrics.
   Publish the qualitative review separately. Do not call the proxy "accuracy."

## Commands

Run in the repository root.

    python evals/benchmark.py validate
    python evals/benchmark.py template --out results/paired.jsonl

Fill baseline and skill with actual model text for each record. Then run:

    python evals/benchmark.py compare --outputs results/paired.jsonl --out results/report.json

Do not put private manuscripts or non-public model outputs in the repository.
The project gitignore should keep results/ out of version control.

## Evaluation schema

Each line in real_papers.jsonl has: id, source title/URL, DOI, CC BY license,
excerpt, prompt, domain, concepts with multiple acceptable Chinese variants,
protected_literals, and gold_reviewed. As of this draft, all gold annotations
are *provisional* (gold_reviewed=false). They require independent review before
publication of performance claims.

Both arms receive exactly the same input task; only availability of the Skill
changes. Keep system prompts, context budget and model settings consistent.
If a model cannot use tools, treat it as a different experiment.

## Measures and interpretation

- Concept coverage: share of annotated concepts with an accepted phrase in
  each output; **not** semantic precision or recall.
- Literal retention: share of protected numbers/units/acronyms present.
- Paired delta: Skill coverage (%) minus baseline coverage (%).
- Human review: semantic correctness, unsupported edits, and fluency.
- Track out-of-index concepts separately. The Skill does not guarantee
  canonical terminology for terms missing from the bundled GB/T indexes.

The scorer uses normalized substring matching. It can match a phrase in the
wrong context. Six cases are too few for statistical generalization. Add
discipline-balanced sources, preregister success criteria and obtain independent
gold review before extrapolating. No benchmark scores are shipped.

## Attribution and reuse

The original excerpts remain CC BY 4.0, attributed to the original authors
through the full titles, DOIs, URLs and license links in each record. The
benchmark does not relicense them under the repository's MIT LICENSE.
Adaptations/translations must give attribution and identify modifications.
