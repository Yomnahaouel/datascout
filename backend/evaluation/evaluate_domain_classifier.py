"""Regression check for DataScout's local domain classifier.

Run from the repository root:

    PYTHONPATH=backend python backend/evaluation/evaluate_domain_classifier.py

The test uses the small CSV files in data/test_datasets and verifies that the
fast local classifier does not collapse every dataset to Finance.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pandas as pd

from engines.tagger_engine import TaggerEngine


EXPECTED_DOMAINS = {
    "01_pii_banking_contacts.csv": "Finance",
    "02_missing_values_quality_test.csv": "Finance",
    "03_risk_fraud_domain_test.csv": "Risk",
    "04_compliance_kyc_ssn_test.csv": "Compliance",
    "05_hr_employee_pii_test.csv": "HR",
    "06_clean_products_operations_baseline.csv": "Products",
}


async def classify_file(engine: TaggerEngine, path: Path) -> str:
    df = pd.read_csv(path)
    text = " ".join(df.columns.astype(str))
    domains = await engine._classify_domain_spec(text)
    if not domains:
        raise AssertionError(f"No domain returned for {path.name}")
    return domains[0].label


async def main() -> None:
    engine = TaggerEngine()
    base_dir = Path("data/test_datasets")
    failures: list[str] = []

    for filename, expected in EXPECTED_DOMAINS.items():
        actual = await classify_file(engine, base_dir / filename)
        print(f"{filename}: expected={expected} actual={actual}")
        if actual != expected:
            failures.append(f"{filename}: expected {expected}, got {actual}")

    if failures:
        raise AssertionError("\n".join(failures))

    print("Domain classifier regression test passed.")


if __name__ == "__main__":
    asyncio.run(main())
