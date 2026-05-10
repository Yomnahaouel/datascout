# DataScout Test Datasets

These CSV files are small synthetic datasets made for local testing.

Recommended upload order:

1. `06_clean_products_operations_baseline.csv` — clean baseline, no expected PII.
2. `02_missing_values_quality_test.csv` — missing values and quality score.
3. `01_pii_banking_contacts.csv` — email, phone, credit card, names, missing balances.
4. `04_compliance_kyc_ssn_test.csv` — SSN and compliance/KYC domain.
5. `05_hr_employee_pii_test.csv` — employee names, work emails, salary missing values.
6. `03_risk_fraud_domain_test.csv` — risk/fraud domain classification.

Expected checks:

- PII columns should appear as `is_pii = true` in the column profile table.
- Domain tags should update the global Domains counter.
- Missing values should reduce quality score and appear in column profiles.
- Clean baseline should have no PII and a high quality score.
