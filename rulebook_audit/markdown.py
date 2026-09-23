"""Markdown rulebook auditor.

aionboard rulebooks are markdown tables (mistake -> why -> fix), not
JSONL chains. This audits what CAN be checked without changing their
format: PII patterns, poisoning phrases, structural completeness
(every row needs all three columns), and review freshness.

Chain integrity for markdown comes from git history itself (every
version hashed + timestamped + attributed). The audit reports the
last-commit age per file as a staleness signal — it cannot prove
per-entry authorship the way JSONL chains do, and says so.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date
from pathlib import Path

from .audit import PII_PATTERNS, POISON_PATTERNS


def parse_tables(text: str) -> list[dict]:
    """Extract markdown table rows as {header: cell} dicts.

    Skips alignment rows (---) and non-table lines.
    """
    rows: list[dict] = []
    header: list[str] | None = None
    for line in text.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            header = None
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        if header is None:
            header = cells
            continue
        if len(cells) != len(header):
            rows.append({"_malformed": line[:160]})
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def audit_markdown_rulebook(path: str | Path,
                            today: str | None = None) -> dict:
    """Audit one markdown rulebook file."""
    path = Path(path)
    text = path.read_text()
    rows = parse_tables(text)
    entries = [r for r in rows if "_malformed" not in r]
    malformed = [r for r in rows if "_malformed" in r]

    pii_hits, poison_hits, incomplete = [], [], []
    for i, e in enumerate(entries):
        blob = " ".join(str(v) for v in e.values())
        for name, rx in PII_PATTERNS.items():
            if rx.search(blob):
                pii_hits.append({"row": i, "pattern": name,
                                 "title": list(e.values())[1
                                 if len(e) > 1 else 0][:60]})
                break
        for name, rx in POISON_PATTERNS.items():
            if rx.search(blob):
                poison_hits.append({"row": i, "pattern": name})
                break
        values = [str(v).strip() for v in e.values()]
        if not all(values) or len(values) < 3:
            incomplete.append({"row": i})

    return {
        "file": str(path),
        "rows": len(entries),
        "malformed_rows": len(malformed),
        "pii_hits": pii_hits,
        "poison_hits": poison_hits,
        "incomplete": incomplete,
        "clean": not (pii_hits or poison_hits or malformed),
        "note": "No per-entry chain: integrity comes from git history. "
                "See git log for authorship.",
    }


def file_last_commit(path: str | Path, repo: str | Path) -> dict:
    """Last-commit age for a file (staleness signal for markdown)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "-1",
             "--format=%H|%ad|%an", "--date=short", "--", str(path)],
            capture_output=True, text=True, timeout=30)
    except Exception as e:
        return {"error": str(e)[:120]}
    if not out.stdout.strip():
        return {"error": "no history (untracked?)"}
    sha, day, author = out.stdout.strip().split("|", 2)
    age_days = (date.today()
                - date.fromisoformat(day)).days if day else -1
    return {"sha": sha[:8], "date": day, "author": author,
            "age_days": age_days,
            "stale": age_days > 90}
