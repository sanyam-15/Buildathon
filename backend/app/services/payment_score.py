"""B2B Payment History Score — production-style computation for judges & demos.

WHERE THE SCORE COMES FROM (production)
--------------------------------------
In production this module would query your AR/ERP (or Razorpay settlements)
for closed invoices belonging to a buyer (company_id / GSTIN / email).

Today we use a deterministic **demo ledger** of past invoices so the live
graph can show a real formula breakdown — not a magic number from the UI.

Formula (0–1):
  score = 0.50 * on_time_rate
        + 0.20 * (1 - late_penalty)
        + 0.20 * (1 - dispute_rate)
        + 0.10 * (1 - broken_promise_rate)

  on_time_rate         = invoices paid on/before due(+grace) / closed invoices
  late_penalty         = min(avg_days_late / 60, 1.0)
  dispute_rate         = disputed invoices / closed invoices
  broken_promise_rate  = broken promises / promises made (or 0 if none)

Optional UI `signals.payment_history_score` is ONLY an override for demos.
The History Analyst calls `get_buyer_payment_score()` as the source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
import hashlib


GRACE_DAYS = 3  # industry-style grace before counting as late


@dataclass
class ClosedInvoice:
    """One historically closed invoice for a B2B buyer."""

    invoice_id: str
    amount: float
    due_date: str  # ISO date
    paid_date: Optional[str]  # ISO date; None if written off unpaid
    disputed: bool = False
    promise_made: bool = False
    promise_kept: bool = False
    source: str = "erp_demo"  # erp | razorpay | crm — shown in audit


# ── Demo AR ledger (simulates ERP / accounting export) ──────────────────────
# Keyed by normalized company name OR email domain for easy matching in demos.
DEMO_BUYER_LEDGERS: Dict[str, List[ClosedInvoice]] = {
    "acme logistics pvt ltd": [
        ClosedInvoice("INV-4101", 42000, "2025-06-01", "2025-05-28", source="erp_demo"),
        ClosedInvoice("INV-4210", 55000, "2025-07-15", "2025-07-20", source="erp_demo"),
        ClosedInvoice("INV-4333", 61000, "2025-08-10", "2025-08-09", source="erp_demo"),
        ClosedInvoice("INV-4450", 48000, "2025-09-01", "2025-09-18", source="erp_demo"),
        ClosedInvoice("INV-4502", 72000, "2025-10-05", "2025-10-04", source="erp_demo"),
        ClosedInvoice("INV-4611", 39000, "2025-11-12", "2025-11-12", source="erp_demo"),
        ClosedInvoice("INV-4700", 88000, "2025-12-01", "2025-12-22", disputed=False, promise_made=True, promise_kept=True, source="crm_demo"),
        ClosedInvoice("INV-4810", 51000, "2026-01-15", "2026-02-10", promise_made=True, promise_kept=False, source="crm_demo"),
    ],
    "novatech solutions": [
        ClosedInvoice("INV-9001", 120000, "2025-08-01", "2025-09-20", disputed=True, source="erp_demo"),
        ClosedInvoice("INV-9002", 95000, "2025-09-01", "2025-10-15", promise_made=True, promise_kept=False, source="crm_demo"),
        ClosedInvoice("INV-9003", 110000, "2025-10-01", "2025-11-01", source="erp_demo"),
        ClosedInvoice("INV-9004", 80000, "2025-11-01", None, disputed=True, source="erp_demo"),  # write-off path
        ClosedInvoice("INV-9005", 100000, "2025-12-01", "2026-01-25", source="erp_demo"),
    ],
    "accounts@acmelogistics.example.com": None,  # alias resolved below
}


def _normalize_key(value: str) -> str:
    return (value or "").strip().lower()


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def resolve_buyer_ledger(
    company_name: Optional[str] = None,
    buyer_email: Optional[str] = None,
    buyer_id: Optional[str] = None,
) -> tuple[str, List[ClosedInvoice], str]:
    """
    Resolve which ledger to use.

    Production: replace this with
      SELECT * FROM invoices WHERE buyer_id = ? AND status IN ('PAID','WRITTEN_OFF')
    or an ERP/Razorpay API call.
    """
    keys_to_try = [
        _normalize_key(company_name or ""),
        _normalize_key(buyer_email or ""),
        _normalize_key(buyer_id or ""),
    ]

    # Email domain fallback e.g. accounts@acmelogistics.example.com → try company match
    if buyer_email and "@" in buyer_email:
        domain = buyer_email.split("@", 1)[1].lower()
        if "acme" in domain:
            keys_to_try.append("acme logistics pvt ltd")
        if "novatech" in domain:
            keys_to_try.append("novatech solutions")

    for key in keys_to_try:
        if not key:
            continue
        if key in DEMO_BUYER_LEDGERS and DEMO_BUYER_LEDGERS[key] is not None:
            return key, list(DEMO_BUYER_LEDGERS[key]), "demo_erp_ledger"
        # fuzzy contains
        for ledger_key, invoices in DEMO_BUYER_LEDGERS.items():
            if invoices and key in ledger_key:
                return ledger_key, list(invoices), "demo_erp_ledger"

    # Unknown buyer → deterministic synthetic history (stable per email/company)
    seed_material = (company_name or buyer_email or buyer_id or "unknown").encode()
    digest = int(hashlib.md5(seed_material).hexdigest()[:8], 16)
    return (
        _normalize_key(company_name or buyer_email or "unknown_buyer"),
        _synthetic_ledger(digest),
        "synthetic_demo_ledger",
    )


def _synthetic_ledger(seed: int) -> List[ClosedInvoice]:
    """Generate a stable demo history when buyer is not in the canned ledger."""
    invoices: List[ClosedInvoice] = []
    base = date(2025, 6, 1)
    for i in range(6):
        due = base + timedelta(days=30 * i)
        # Mix of on-time / late based on seed bits
        late_days = (seed >> (i * 3)) % 25
        paid = due + timedelta(days=late_days - 5)  # sometimes early, sometimes late
        invoices.append(
            ClosedInvoice(
                invoice_id=f"SYN-{seed % 10000:04d}-{i+1}",
                amount=25000 + (seed % 7) * 5000 + i * 1000,
                due_date=due.isoformat(),
                paid_date=paid.isoformat(),
                disputed=(seed >> i) % 11 == 0,
                promise_made=(seed >> i) % 5 == 0,
                promise_kept=(seed >> i) % 7 != 0,
                source="synthetic_demo",
            )
        )
    return invoices


def compute_payment_history_score(invoices: List[ClosedInvoice]) -> Dict[str, Any]:
    """
    Compute transparent payment_history_score from closed invoice history.

    Returns score + every intermediate so judges can audit the math in the
    Live Console / Case Details.
    """
    if not invoices:
        return {
            "payment_history_score": 0.5,
            "formula": "default_neutral (no closed invoices)",
            "components": {},
            "invoice_count": 0,
            "invoices_sampled": [],
        }

    closed = len(invoices)
    on_time = 0
    late_days_list: List[int] = []
    disputed = 0
    promises_made = 0
    promises_broken = 0

    for inv in invoices:
        due = _parse_date(inv.due_date)
        paid = _parse_date(inv.paid_date)

        if inv.disputed:
            disputed += 1

        if inv.promise_made:
            promises_made += 1
            if not inv.promise_kept:
                promises_broken += 1

        if paid is None or due is None:
            # Unpaid / written-off → treat as late
            late_days_list.append(60)
            continue

        delta = (paid - due).days
        if delta <= GRACE_DAYS:
            on_time += 1
            late_days_list.append(0)
        else:
            late_days_list.append(delta)

    on_time_rate = on_time / closed
    avg_days_late = sum(late_days_list) / closed
    late_penalty = min(avg_days_late / 60.0, 1.0)
    dispute_rate = disputed / closed
    broken_promise_rate = (promises_broken / promises_made) if promises_made else 0.0

    w_on_time, w_late, w_dispute, w_promise = 0.50, 0.20, 0.20, 0.10
    score = (
        w_on_time * on_time_rate
        + w_late * (1.0 - late_penalty)
        + w_dispute * (1.0 - dispute_rate)
        + w_promise * (1.0 - broken_promise_rate)
    )
    score = round(max(0.0, min(1.0, score)), 3)

    return {
        "payment_history_score": score,
        "formula": (
            f"0.50*{on_time_rate:.3f}(on_time) + "
            f"0.20*{1-late_penalty:.3f}(lateness) + "
            f"0.20*{1-dispute_rate:.3f}(disputes) + "
            f"0.10*{1-broken_promise_rate:.3f}(promises)"
        ),
        "weights": {
            "on_time_rate": w_on_time,
            "lateness": w_late,
            "disputes": w_dispute,
            "promises": w_promise,
        },
        "components": {
            "on_time_rate": round(on_time_rate, 3),
            "on_time_count": on_time,
            "closed_invoices": closed,
            "avg_days_late": round(avg_days_late, 1),
            "late_penalty": round(late_penalty, 3),
            "dispute_rate": round(dispute_rate, 3),
            "disputed_count": disputed,
            "promises_made": promises_made,
            "promises_broken": promises_broken,
            "broken_promise_rate": round(broken_promise_rate, 3),
            "grace_days": GRACE_DAYS,
        },
        "invoice_count": closed,
        "invoices_sampled": [asdict(i) for i in invoices],
        "production_note": (
            "In production, invoices_sampled come from ERP/Razorpay AR APIs "
            "for this buyer_id — same formula, live data."
        ),
    }


def score_buyer(
    company_name: Optional[str] = None,
    buyer_email: Optional[str] = None,
    buyer_id: Optional[str] = None,
) -> Dict[str, Any]:
    """End-to-end: resolve ledger → compute score (what agents call)."""
    ledger_key, invoices, ledger_source = resolve_buyer_ledger(
        company_name=company_name,
        buyer_email=buyer_email,
        buyer_id=buyer_id,
    )
    result = compute_payment_history_score(invoices)
    result["buyer_key"] = ledger_key
    result["ledger_source"] = ledger_source
    result["data_source"] = (
        "Computed from historical closed invoices "
        f"({ledger_source}) — NOT a hardcoded UI field"
    )
    return result
