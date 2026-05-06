# PHASE 5: Generate Synthetic Banking Datasets

## Task
Create a Python script that generates 70-80 synthetic banking/finance datasets for testing DataScout.

## Output Location
`/home/kali/datascout/data/synthetic/`

## Dataset Categories (with examples)

### 1. Transaction Data (15 datasets)
- credit_card_transactions.csv - Card purchases with merchant info
- bank_transfers.csv - Wire transfers between accounts
- atm_withdrawals.csv - ATM usage with locations
- payment_history.csv - Bill payments
- forex_transactions.csv - Currency exchanges

### 2. Customer Data (15 datasets)
- customer_demographics.csv - Age, income, location
- account_holders.csv - Account types, balances
- credit_scores.csv - Credit history
- customer_segments.csv - Marketing segments
- kyc_records.csv - Know Your Customer data

### 3. Loan Data (15 datasets)
- mortgage_applications.csv - Home loans
- personal_loans.csv - Unsecured loans
- auto_loans.csv - Vehicle financing
- loan_defaults.csv - Default records
- credit_line_usage.csv - Credit utilization

### 4. Risk & Fraud Data (15 datasets)
- fraud_alerts.csv - Suspicious activities
- risk_assessments.csv - Customer risk scores
- chargebacks.csv - Disputed transactions
- aml_flags.csv - Anti-money laundering alerts
- identity_verification.csv - ID check results

### 5. Operations Data (10 datasets)
- branch_performance.csv - Branch metrics
- employee_data.csv - Staff records (with PII)
- call_center_logs.csv - Customer support
- complaint_records.csv - Customer complaints
- audit_logs.csv - System audit trails

### 6. Investment Data (10 datasets)
- portfolio_holdings.csv - Investment positions
- trade_history.csv - Buy/sell orders
- market_data.csv - Price histories
- fund_performance.csv - Mutual fund returns
- dividend_payments.csv - Dividend records

## Dataset Requirements

### Size Variation
- Small: 100-1,000 rows (20 datasets)
- Medium: 1,000-10,000 rows (30 datasets)
- Large: 10,000-100,000 rows (20 datasets)
- Very Large: 100,000-500,000 rows (10 datasets)

### Column Types to Include
- Numeric: amounts, counts, scores, percentages
- Categorical: status, type, category, region
- Date/Time: timestamps, dates, periods
- Text: descriptions, notes, names
- Boolean: flags, indicators
- ID: account numbers, customer IDs

### Data Quality Variations
- Clean datasets (90%+ completeness): 40 datasets
- Moderate quality (70-90% completeness): 25 datasets
- Poor quality (50-70% completeness): 15 datasets

### PII Inclusion
- Datasets with PII (names, SSN, email, phone): 25 datasets
- Datasets without PII: 55 datasets

## Script Requirements

Create `backend/scripts/generate_synthetic_data.py`:

1. Use libraries: pandas, numpy, faker
2. Generate realistic banking data
3. Include proper data types
4. Add some intentional quality issues (nulls, outliers)
5. Save as CSV files
6. Create a manifest.json listing all datasets

## Example Data Patterns

### Credit Card Transaction
```
transaction_id, card_number, merchant_name, amount, timestamp, category, is_fraud
TXN001, **** **** **** 1234, Amazon, 156.99, 2024-01-15 14:32:00, retail, 0
```

### Customer Demographics
```
customer_id, first_name, last_name, email, phone, dob, income_bracket, state
C001, John, Smith, john.smith@email.com, 555-0123, 1985-03-15, 75000-100000, CA
```

### Loan Application
```
application_id, customer_id, loan_type, amount_requested, term_months, interest_rate, status, credit_score
LA001, C001, mortgage, 350000, 360, 6.5, approved, 720
```

## Execution
After creating the script, run it to generate all datasets:
```bash
cd /home/kali/datascout/backend
python scripts/generate_synthetic_data.py
```

Make the datasets realistic and varied for comprehensive testing!
