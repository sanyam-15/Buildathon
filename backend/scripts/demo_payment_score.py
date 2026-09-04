#!/usr/bin/env python3
"""
Demo script for judges — show WHERE payment_history_score comes from.

Run from backend folder:
  python -m scripts.demo_payment_score
  OR
  python scripts/demo_payment_score.py

This prints the same formula Relay uses in the B2B History Analyst tool
`get_buyer_payment_score` (see app/services/payment_score.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running as a file from backend/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.payment_score import score_buyer, compute_payment_history_score, DEMO_BUYER_LEDGERS


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def main() -> None:
    banner("RAZORPAY RELAY — B2B Payment History Score (Judge Demo)")
    print(
        """
In production this score is computed from closed invoices in your AR/ERP
(or Razorpay settlements) for that buyer — NOT typed into the dashboard.

Formula:
  score = 0.50 * on_time_rate
        + 0.20 * (1 - late_penalty)      # late_penalty = min(avg_days_late/60, 1)
        + 0.20 * (1 - dispute_rate)
        + 0.10 * (1 - broken_promise_rate)
"""
    )

    demos = [
        {"label": "Good payer (Acme Logistics)", "company_name": "Acme Logistics Pvt Ltd", "buyer_email": "accounts@acmelogistics.example.com"},
        {"label": "Risky payer (NovaTech)", "company_name": "NovaTech Solutions", "buyer_email": "ap@novatech.example.com"},
        {"label": "Unknown buyer -> synthetic ledger", "company_name": "BrightPath Retail", "buyer_email": "finance@brightpath.example.com"},
    ]

    for demo in demos:
        banner(demo["label"])
        result = score_buyer(
            company_name=demo["company_name"],
            buyer_email=demo["buyer_email"],
        )
        print(f"Buyer key      : {result['buyer_key']}")
        print(f"Ledger source  : {result['ledger_source']}")
        print(f"Data source    : {result['data_source']}")
        print(f"Invoice count  : {result['invoice_count']}")
        print(f"SCORE          : {result['payment_history_score']:.1%}")
        print(f"Formula expand : {result['formula']}")
        print("Components:")
        for k, v in result["components"].items():
            print(f"  - {k}: {v}")
        print("\nSample invoices (first 3):")
        for inv in result["invoices_sampled"][:3]:
            print(f"  {inv['invoice_id']}: due={inv['due_date']} paid={inv['paid_date']} "
                  f"disputed={inv['disputed']} source={inv['source']}")

    banner("Canned demo ledgers available")
    for key, invoices in DEMO_BUYER_LEDGERS.items():
        if invoices:
            s = compute_payment_history_score(invoices)
            print(f"  * {key}: {len(invoices)} invoices -> score {s['payment_history_score']:.1%}")

    banner("JSON dump (Acme) — same payload agents emit to Live Console")
    print(json.dumps(score_buyer(company_name="Acme Logistics Pvt Ltd"), indent=2, default=str))

    print(
        """
Talking point for judges:
  The History Analyst calls get_buyer_payment_score(). That tool loads the
  buyer's closed-invoice history (ERP/demo ledger) and applies a fixed
  weighted formula. You can see the breakdown live in the orchestration log.
"""
    )


if __name__ == "__main__":
    main()
