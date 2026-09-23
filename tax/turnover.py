"""Rolling turnover tracker. User figures in, bands out.

The owner enters monthly taxable turnover and supplies the threshold
they verified at gov.uk. We compute the rolling 12-month total and
report which band it sits in: comfortable (<80%), watch (80-90%),
act now (90-100%), likely over (>=100%). Bands trigger owner actions,
never filings.
"""

from __future__ import annotations

import json
from pathlib import Path


def load_ledger(path: str | Path) -> dict:
    """Load {YYYY-MM: amount} ledger. Missing file = empty ledger."""
    p = Path(path)
    if not p.exists():
        return {}
    with open(p) as f:
        data = json.load(f)
    return {k: float(v) for k, v in data.items()}


def save_ledger(path: str | Path, ledger: dict) -> None:
    """Save ledger with 600 permissions (financial data)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump({k: float(v) for k, v in sorted(ledger.items())}, f, indent=2)
    p.chmod(0o600)


def add_month(ledger: dict, year_month: str, amount: float) -> dict:
    """Record one month's taxable turnover. Returns updated ledger."""
    if len(year_month) != 7 or year_month[4] != "-":
        raise ValueError(f"expected YYYY-MM, got {year_month!r}")
    if amount < 0:
        raise ValueError("turnover cannot be negative")
    return {**ledger, year_month: float(amount)}


def rolling_12m(ledger: dict, through: str | None = None) -> float:
    """Sum of the 12 months ending at `through` (default: latest entry)."""
    if not ledger:
        return 0.0
    months = sorted(ledger)
    end = through or months[-1]
    window = [m for m in months if m <= end][-12:]
    return round(sum(ledger[m] for m in window), 2)


def threshold_status(rolling_total: float, threshold: float | None) -> dict:
    """Band + owner action for a rolling total against THEIR threshold.

    threshold=None means the owner hasn't confirmed one — the only
    correct output is a pointer to check it.
    """
    if threshold is None:
        return {
            "band": "unknown",
            "action": "Confirm the current VAT threshold at "
                      "https://www.gov.uk/vat-registration-thresholds "
                      "before interpreting this figure.",
            "rolling_total": rolling_total,
        }
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    ratio = rolling_total / threshold
    if ratio >= 1.0:
        return {"band": "likely_over", "rolling_total": rolling_total,
                "ratio": round(ratio, 2),
                "action": "You may have exceeded the threshold. Check the "
                          "live threshold, then ask an accountant immediately "
                          "— registration is time-limited."}
    if ratio >= 0.9:
        return {"band": "act_now", "rolling_total": rolling_total,
                "ratio": round(ratio, 2),
                "action": "Within 10% of the threshold. Start preparing "
                          "records for registration and ask an accountant."}
    if ratio >= 0.8:
        return {"band": "watch", "rolling_total": rolling_total,
                "ratio": round(ratio, 2),
                "action": "Monitor monthly. Review which supplies count "
                          "toward the threshold."}
    return {"band": "comfortable", "rolling_total": rolling_total,
            "ratio": round(ratio, 2),
            "action": "No action. Keep recording monthly figures."}
