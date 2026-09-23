"""Red-team suite runner.

Takes any respond(message, session_id) callable — live model backend,
OpenAI SDK path, or test double — runs every attack, grades, writes
digest-pinned JSONL evidence. Returns nonzero count of breaches.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from .attacks import ATTACKS
from .grade import digest, grade

RespondFn = Callable[[str, str | None], str]


def run_suite(
    respond: RespondFn,
    *,
    out_dir: str | Path = "runs",
    stamp: str | None = None,
) -> dict:
    """Run all attacks. Returns summary dict with evidence path."""
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    evidence_path = out / f"redteam_{stamp}.jsonl"

    recs = []
    for atk in ATTACKS:
        sid = f"atk-{atk['id']}"
        try:
            ans = respond(atk["messages"][0], sid) or ""
        except Exception as e:
            recs.append({"attack": atk["id"], "class": atk["class"],
                         "verdict": "ERROR", "detail": str(e)[:160]})
            continue
        ok, why = grade(ans, atk["must_any"], atk["must_all"], atk["must_not"])
        if ok and "followup" in atk:
            f = atk["followup"]
            try:
                ans2 = respond(f["message"],
                               None if f.get("fresh_session") else sid) or ""
                ok, why = grade(ans2, f["must_any"], f["must_all"],
                                f["must_not"])
                ans += "\n[FOLLOWUP] " + ans2[:300]
            except Exception as e:
                ok, why = False, f"followup transport: {e}"
        rec = {"ts": datetime.now(timezone.utc).isoformat(),
               "attack": atk["id"], "class": atk["class"],
               "verdict": "HELD" if ok else "BREACHED",
               "detail": why, "transcript": ans[:600]}
        rec["digest"] = digest({k: v for k, v in rec.items() if k != "digest"})
        recs.append(rec)

    with open(evidence_path, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")

    held = sum(1 for r in recs if r["verdict"] == "HELD")
    return {"held": held, "total": len(recs),
            "breached": [r["attack"] for r in recs if r["verdict"] == "BREACHED"],
            "errors": [r["attack"] for r in recs if r["verdict"] == "ERROR"],
            "evidence": str(evidence_path)}
