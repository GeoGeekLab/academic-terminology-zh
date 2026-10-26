# Integrating with research writing Skills

This repository is an additive component. The installer does not modify,
replace or fork any third-party research Skill. Existing writing workflows can
call its read-only local handoff CLI. External projects have not endorsed,
installed, or accepted this integration unless they explicitly do so.

## Install into a research workspace

From the source repository, choose exactly one agent:

    python integrations/install.py --agent codex --project /path/to/paper-workspace
    python integrations/install.py --agent claude --project /path/to/paper-workspace
    python integrations/install.py --agent opencode --project /path/to/paper-workspace

Codex and OpenCode discover project .agents/skills/, while Claude Code uses
.claude/skills/. Test OpenCode against its documented .agents compatibility.

By default, only Skill code is copied. Set GB_TERMINOLOGY_DB_ROOT to a lawfully
available local CSV directory or ZIP before invoking the Skill.

For a local workspace where the user has reviewed the source-data rights,
there is an explicit, optional local copy:

    python integrations/install.py --agent claude --project /path/to/workspace --with-data

This switch grants **no redistribution rights** to the GB/T-based indexes.
Read ../DATA_RIGHTS.md. Do not publish the copied data as part of another
Skill without a separate rights determination. The installer never modifies
another named Skill. Existing same-name targets require --force.

## Read-only handoff interface

The skill provides a local inspection step. For a written manuscript file:

    python .agents/skills/academic-terminology-zh/scripts/handoff.py --input manuscript.txt --domain oceanography

For Claude Code replace .agents/ with .claude/. For installed data use
GB_TERMINOLOGY_DB_ROOT. Input text can also be passed over stdin, which
avoids putting private manuscript text in shell arguments.

The output is JSON with an array of candidate mentions, each containing
zh/en terms, domain, standard, clause, page and verification status. It
does **not** modify user files or silently force replacements.

## Composition with any academic-writing Skill

Your existing Skill can add this optional step to its review workflow:

    1. Extract a paragraph for terminology review.
    2. Call the handoff CLI with stdin or --input, optionally narrowing domain.
    3. Use the returned source-labelled candidates as references only.
    4. Confirm terminology meaning and distinguish homonyms in context.
    5. Preserve numerical results, formulas, methods and author's preferred conventions.
    6. Only present changes with uncertainty warnings when a conflict remains.

Other Skills can also call scripts/lookup.py --q TERM --json for an explicit
single-term query. Do not silently trust unreviewed source-index labels.

## Compatibility checks

- Codex: project .agents/skills/ (native).
- Claude Code: project .claude/skills/ (installer copy).
- OpenCode: project .agents/skills/ (documented compatibility).
- Python: 3.10+; standard library only; no network call or manuscript upload.
- Local tests cover install paths, protected overwrite, JSON handoff and
  source references. Actual integration acceptance by third-party maintainers
  remains an external milestone.
