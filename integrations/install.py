#!/usr/bin/env python3
"""Copy the Skill into an existing agent workspace, without touching other skills."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

NAME = "academic-terminology-zh"
SKILL_ROOTS = {"codex": ".agents/skills", "claude": ".claude/skills", "opencode": ".agents/skills"}


def install(source_root: Path, project_root: Path, agent: str, *,
            with_data: bool = False, force: bool = False, dry_run: bool = False) -> list[str]:
    if agent not in SKILL_ROOTS:
        raise ValueError(f"unsupported agent: {agent}")
    source_root = source_root.resolve()
    project_root = project_root.resolve()
    sources = [(source_root / ".agents/skills" / NAME,
                project_root / SKILL_ROOTS[agent] / NAME)]
    if with_data:
        sources.append((source_root / "data/gb_terminology_databases",
                        project_root / "data/gb_terminology_databases"))
    actions = []
    for source, target in sources:
        if not source.is_dir():
            raise FileNotFoundError(f"missing install source: {source}")
        if target.is_symlink():
            raise ValueError(f"refusing to overwrite symlink: {target}")
        if source.resolve() == target.resolve():
            actions.append(f"already in place: {target}")
            continue
        if target.exists() and not force:
            raise FileExistsError(f"destination exists (use --force to replace): {target}")
        if target.exists() and not target.is_dir():
            raise ValueError(f"not a directory: {target}")
        actions.append(f"{'replace' if target.exists() else 'copy'}: {source} -> {target}")
    if dry_run:
        return actions
    for source, target in sources:
        if source.resolve() == target.resolve():
            continue
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
    return actions


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--agent", choices=sorted(SKILL_ROOTS), required=True)
    p.add_argument("--project", type=Path, default=Path.cwd(), help="Target workspace root")
    p.add_argument("--with-data", action="store_true",
                   help="Opt in to a local data copy; this grants NO redistribution rights")
    p.add_argument("--force", action="store_true", help="Replace this Skill's existing destination")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    try:
        source = Path(__file__).resolve().parents[1]
        actions = install(source, args.project, args.agent,
                          with_data=args.with_data, force=args.force, dry_run=args.dry_run)
        print("\n".join(actions))
        if args.with_data:
            print("NOTICE: local data copy only; redistribution rights remain unverified. Read DATA_RIGHTS.md.")
        else:
            print("NOTE: set GB_TERMINOLOGY_DB_ROOT to a lawfully available local database.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"install error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
