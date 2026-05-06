#!/usr/bin/env python3
"""
DataScout Synthetic Banking Data Generator
Generates 80 realistic banking/finance datasets for testing.
"""

import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = Path("/home/kali/datascout/data/synthetic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Dataset configurations
DATASETS = []

def add_nulls(df: pd.DataFrame, pct: float = 0.05) -> pd.DataFrame:
    """Add random null values to a DataFrame."""
    mask = np.random.random(df.shape) < pct
    df = df.mask(mask)
    return df

def add_outliers(series: pd.Series, pct: float = 0.02) -> pd.Series:
    """Add outliers to numeric series."""
    n_outliers = int(len(series) * pct)
    outlier_idx = np.random.choice(len(series), n_outliers, replace=False)
    series = series.copy()
    series.iloc[outlier_idx] = series.mean() + series.std() * np.random.uniform(3, 10, n_outliers)
    return series

# ============== TRANSACTION DATA ==============

def gen_credit_card_transactions(n_rows: int) -> pd.DataFrame:
    """Credit card transaction data with fraud labels."""
    data = {
        'transaction_id': [f'TXN{i:08d}' for i in range(n_rows)],
        'card_number': [f'**** **** **** {random.randint(1000,9999)}' for _ in range(n_rows)],
        'merchant_name': [fake.company() for _ in range(n_rows)],
        'merchant_category': np.random.choice(['retail', 'food', 'travel', 'entertainment', 'services', 'gas'], n_rows),
        'amount': np.round(np.random.exponential(100, n_rows), 2),
        'currency': np.random.choice(['USD', 'EUR', 'GBP'], n_rows, p=[0.8, 0.15, 0.05]),
        'timestamp': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'is_fraud': np.random.choice([0, 1], n_rows, p=[0.98, 0.02]),
        'country': [fake.country_code() for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_bank_transfers(n_rows: int) -> pd.DataFrame:
    """Wire transfer records."""
    data = {
        'transfer_id': [f'TRF{i:08d}' for i in range(n_rows)],
        'from_account': [f'ACC{random.randint(10000000, 99999999)}' for _ in range(n_rows)],
        'to_account': [f'ACC{random.randint(10000000, 99999999)}' for _ in range(n_rows)],
        'amount': np.round(np.random.exponential(5000, n_rows), 2),
        'currency': np.random.choice(['USD', 'EUR', 'GBP', 'JPY'], n_rows),
        'transfer_type': np.random.choice(['domestic', 'international', 'instant'], n_rows),
        'status': np.random.choice(['completed', 'pending', 'failed', 'cancelled'], n_rows, p=[0.85, 0.08, 0.05, 0.02]),
        'initiated_at': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'completed_at': [fake.date_time_between(start_date='-1y') if random.random() > 0.1 else None for _ in range(n_rows)],
        'fee': np.round(np.random.uniform(0, 50, n_rows), 2),
    }
    return pd.DataFrame(data)

def gen_atm_withdrawals(n_rows: int) -> pd.DataFrame:
    """ATM withdrawal records."""
    data = {
        'withdrawal_id': [f'ATM{i:08d}' for i in range(n_rows)],
        'card_number': [f'**** **** **** {random.randint(1000,9999)}' for _ in range(n_rows)],
        'atm_id': [f'ATM_{fake.city()[:3].upper()}{random.randint(100,999)}' for _ in range(n_rows)],
        'location': [fake.city() for _ in range(n_rows)],
        'amount': np.random.choice([20, 40, 60, 80, 100, 200, 300, 500], n_rows),
        'fee': np.where(np.random.random(n_rows) > 0.7, np.random.uniform(2, 5, n_rows), 0),
        'timestamp': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'balance_after': np.round(np.random.uniform(100, 50000, n_rows), 2),
    }
    return pd.DataFrame(data)

def gen_payment_history(n_rows: int) -> pd.DataFrame:
    """Bill payment records."""
    categories = ['utilities', 'rent', 'insurance', 'subscription', 'credit_card', 'loan', 'tax']
    data = {
        'payment_id': [f'PAY{i:08d}' for i in range(n_rows)],
        'account_id': [f'ACC{random.randint(10000000, 99999999)}' for _ in range(n_rows)],
        'payee': [fake.company() for _ in range(n_rows)],
        'category': np.random.choice(categories, n_rows),
        'amount': np.round(np.random.exponential(200, n_rows), 2),
        'payment_date': [fake.date_between(start_date='-1y') for _ in range(n_rows)],
        'due_date': [fake.date_between(start_date='-1y') for _ in range(n_rows)],
        'status': np.random.choice(['paid', 'pending', 'overdue', 'scheduled'], n_rows, p=[0.75, 0.1, 0.1, 0.05]),
        'is_recurring': np.random.choice([True, False], n_rows, p=[0.6, 0.4]),
    }
    return pd.DataFrame(data)

def gen_forex_transactions(n_rows: int) -> pd.DataFrame:
    """Currency exchange records."""
    pairs = ['USD/EUR', 'USD/GBP', 'EUR/GBP', 'USD/JPY', 'EUR/JPY', 'GBP/JPY']
    data = {
        'forex_id': [f'FX{i:08d}' for i in range(n_rows)],
        'currency_pair': np.random.choice(pairs, n_rows),
        'amount_from': np.round(np.random.exponential(1000, n_rows), 2),
        'amount_to': np.round(np.random.exponential(1000, n_rows), 2),
        'exchange_rate': np.round(np.random.uniform(0.5, 2.0, n_rows), 6),
        'timestamp': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'fee_pct': np.round(np.random.uniform(0.1, 2.0, n_rows), 2),
    }
    return pd.DataFrame(data)

# ============== CUSTOMER DATA ==============

def gen_customer_demographics(n_rows: int, include_pii: bool = True) -> pd.DataFrame:
    """Customer demographic information."""
    data = {
        'customer_id': [f'C{i:06d}' for i in range(n_rows)],
        'age': np.random.randint(18, 85, n_rows),
        'gender': np.random.choice(['M', 'F', 'Other'], n_rows, p=[0.48, 0.48, 0.04]),
        'income_bracket': np.random.choice(['<25K', '25K-50K', '50K-75K', '75K-100K', '100K-150K', '150K+'], n_rows),
        'employment_status': np.random.choice(['employed', 'self-employed', 'unemployed', 'retired', 'student'], n_rows),
        'marital_status': np.random.choice(['single', 'married', 'divorced', 'widowed'], n_rows),
        'education': np.random.choice(['high_school', 'bachelors', 'masters', 'phd', 'other'], n_rows),
        'state': [fake.state_abbr() for _ in range(n_rows)],
        'city': [fake.city() for _ in range(n_rows)],
        'zip_code': [fake.zipcode() for _ in range(n_rows)],
        'account_open_date': [fake.date_between(start_date='-10y') for _ in range(n_rows)],
    }
    if include_pii:
        data['first_name'] = [fake.first_name() for _ in range(n_rows)]
        data['last_name'] = [fake.last_name() for _ in range(n_rows)]
        data['email'] = [fake.email() for _ in range(n_rows)]
        data['phone'] = [fake.phone_number() for _ in range(n_rows)]
        data['ssn'] = [fake.ssn() for _ in range(n_rows)]
    return pd.DataFrame(data)

def gen_account_holders(n_rows: int) -> pd.DataFrame:
    """Bank account information."""
    data = {
        'account_id': [f'ACC{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'account_type': np.random.choice(['checking', 'savings', 'money_market', 'cd', 'ira'], n_rows),
        'balance': np.round(np.random.exponential(5000, n_rows), 2),
        'currency': 'USD',
        'interest_rate': np.round(np.random.uniform(0.01, 5.0, n_rows), 2),
        'opened_date': [fake.date_between(start_date='-10y') for _ in range(n_rows)],
        'status': np.random.choice(['active', 'dormant', 'closed', 'frozen'], n_rows, p=[0.85, 0.08, 0.05, 0.02]),
        'overdraft_protection': np.random.choice([True, False], n_rows),
        'last_activity': [fake.date_between(start_date='-1y') for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_credit_scores(n_rows: int) -> pd.DataFrame:
    """Credit score records."""
    data = {
        'customer_id': [f'C{i:06d}' for i in range(n_rows)],
        'credit_score': np.clip(np.random.normal(700, 80, n_rows).astype(int), 300, 850),
        'score_date': [fake.date_between(start_date='-2y') for _ in range(n_rows)],
        'bureau': np.random.choice(['Experian', 'Equifax', 'TransUnion'], n_rows),
        'payment_history_pct': np.round(np.random.uniform(70, 100, n_rows), 1),
        'credit_utilization_pct': np.round(np.random.uniform(0, 100, n_rows), 1),
        'credit_age_months': np.random.randint(6, 360, n_rows),
        'num_accounts': np.random.randint(1, 20, n_rows),
        'num_inquiries': np.random.randint(0, 10, n_rows),
        'derogatory_marks': np.random.choice([0, 1, 2, 3], n_rows, p=[0.7, 0.15, 0.1, 0.05]),
    }
    return pd.DataFrame(data)

def gen_customer_segments(n_rows: int) -> pd.DataFrame:
    """Customer segmentation data."""
    segments = ['premium', 'standard', 'basic', 'new', 'at_risk', 'churned']
    data = {
        'customer_id': [f'C{i:06d}' for i in range(n_rows)],
        'segment': np.random.choice(segments, n_rows),
        'lifetime_value': np.round(np.random.exponential(5000, n_rows), 2),
        'tenure_months': np.random.randint(1, 240, n_rows),
        'num_products': np.random.randint(1, 8, n_rows),
        'engagement_score': np.round(np.random.uniform(0, 100, n_rows), 1),
        'churn_probability': np.round(np.random.uniform(0, 1, n_rows), 3),
        'last_contact': [fake.date_between(start_date='-1y') for _ in range(n_rows)],
        'preferred_channel': np.random.choice(['mobile', 'web', 'branch', 'phone', 'email'], n_rows),
        'segmented_date': [fake.date_between(start_date='-6m') for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_kyc_records(n_rows: int) -> pd.DataFrame:
    """Know Your Customer records with PII."""
    data = {
        'kyc_id': [f'KYC{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'full_name': [fake.name() for _ in range(n_rows)],
        'date_of_birth': [fake.date_of_birth(minimum_age=18, maximum_age=90) for _ in range(n_rows)],
        'nationality': [fake.country() for _ in range(n_rows)],
        'id_type': np.random.choice(['passport', 'drivers_license', 'national_id'], n_rows),
        'id_number': [fake.bothify('??######') for _ in range(n_rows)],
        'id_expiry': [fake.date_between(start_date='today', end_date='+10y') for _ in range(n_rows)],
        'address': [fake.address().replace('\n', ', ') for _ in range(n_rows)],
        'verification_status': np.random.choice(['verified', 'pending', 'rejected', 'expired'], n_rows, p=[0.8, 0.1, 0.05, 0.05]),
        'verification_date': [fake.date_between(start_date='-2y') for _ in range(n_rows)],
        'risk_rating': np.random.choice(['low', 'medium', 'high'], n_rows, p=[0.7, 0.25, 0.05]),
    }
    return pd.DataFrame(data)

# ============== LOAN DATA ==============

def gen_mortgage_applications(n_rows: int) -> pd.DataFrame:
    """Mortgage loan applications."""
    data = {
        'application_id': [f'MTG{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'property_value': np.round(np.random.uniform(100000, 2000000, n_rows), -3),
        'loan_amount': np.round(np.random.uniform(80000, 1500000, n_rows), -3),
        'down_payment_pct': np.round(np.random.uniform(5, 30, n_rows), 1),
        'interest_rate': np.round(np.random.uniform(3.0, 8.0, n_rows), 3),
        'term_years': np.random.choice([15, 20, 30], n_rows),
        'loan_type': np.random.choice(['conventional', 'fha', 'va', 'jumbo'], n_rows),
        'property_type': np.random.choice(['single_family', 'condo', 'townhouse', 'multi_family'], n_rows),
        'application_date': [fake.date_between(start_date='-2y') for _ in range(n_rows)],
        'status': np.random.choice(['approved', 'denied', 'pending', 'withdrawn'], n_rows, p=[0.6, 0.15, 0.2, 0.05]),
        'credit_score': np.clip(np.random.normal(720, 60, n_rows).astype(int), 500, 850),
        'dti_ratio': np.round(np.random.uniform(20, 50, n_rows), 1),
    }
    return pd.DataFrame(data)

def gen_personal_loans(n_rows: int) -> pd.DataFrame:
    """Personal/unsecured loans."""
    data = {
        'loan_id': [f'PL{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'loan_amount': np.round(np.random.uniform(1000, 50000, n_rows), -2),
        'interest_rate': np.round(np.random.uniform(6.0, 24.0, n_rows), 2),
        'term_months': np.random.choice([12, 24, 36, 48, 60], n_rows),
        'monthly_payment': np.round(np.random.uniform(100, 2000, n_rows), 2),
        'purpose': np.random.choice(['debt_consolidation', 'home_improvement', 'medical', 'vacation', 'other'], n_rows),
        'origination_date': [fake.date_between(start_date='-3y') for _ in range(n_rows)],
        'status': np.random.choice(['current', 'paid_off', 'delinquent', 'default', 'charged_off'], n_rows, p=[0.7, 0.15, 0.08, 0.05, 0.02]),
        'remaining_balance': np.round(np.random.uniform(0, 40000, n_rows), 2),
    }
    return pd.DataFrame(data)

def gen_auto_loans(n_rows: int) -> pd.DataFrame:
    """Auto/vehicle loans."""
    data = {
        'loan_id': [f'AUTO{i:07d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'vehicle_make': np.random.choice(['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes', 'Tesla'], n_rows),
        'vehicle_year': np.random.randint(2015, 2025, n_rows),
        'vehicle_price': np.round(np.random.uniform(15000, 80000, n_rows), -2),
        'loan_amount': np.round(np.random.uniform(10000, 70000, n_rows), -2),
        'interest_rate': np.round(np.random.uniform(3.0, 15.0, n_rows), 2),
        'term_months': np.random.choice([36, 48, 60, 72, 84], n_rows),
        'monthly_payment': np.round(np.random.uniform(200, 1500, n_rows), 2),
        'is_new_vehicle': np.random.choice([True, False], n_rows, p=[0.6, 0.4]),
        'origination_date': [fake.date_between(start_date='-5y') for _ in range(n_rows)],
        'status': np.random.choice(['current', 'paid_off', 'delinquent', 'repossessed'], n_rows, p=[0.75, 0.15, 0.08, 0.02]),
    }
    return pd.DataFrame(data)

def gen_loan_defaults(n_rows: int) -> pd.DataFrame:
    """Loan default records."""
    data = {
        'default_id': [f'DEF{i:08d}' for i in range(n_rows)],
        'loan_id': [f'LN{random.randint(10000000, 99999999)}' for _ in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'loan_type': np.random.choice(['mortgage', 'personal', 'auto', 'credit_card', 'student'], n_rows),
        'original_amount': np.round(np.random.uniform(5000, 500000, n_rows), -2),
        'default_amount': np.round(np.random.uniform(1000, 200000, n_rows), 2),
        'default_date': [fake.date_between(start_date='-3y') for _ in range(n_rows)],
        'days_past_due': np.random.randint(90, 365, n_rows),
        'recovery_amount': np.round(np.random.uniform(0, 50000, n_rows), 2),
        'recovery_status': np.random.choice(['in_progress', 'settled', 'written_off', 'legal_action'], n_rows),
        'reason': np.random.choice(['job_loss', 'medical', 'divorce', 'death', 'business_failure', 'unknown'], n_rows),
    }
    return pd.DataFrame(data)

def gen_credit_line_usage(n_rows: int) -> pd.DataFrame:
    """Credit line utilization data."""
    data = {
        'account_id': [f'CC{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'credit_limit': np.round(np.random.uniform(1000, 50000, n_rows), -2),
        'current_balance': np.round(np.random.uniform(0, 40000, n_rows), 2),
        'available_credit': np.round(np.random.uniform(0, 50000, n_rows), 2),
        'utilization_pct': np.round(np.random.uniform(0, 100, n_rows), 1),
        'minimum_payment': np.round(np.random.uniform(25, 500, n_rows), 2),
        'payment_due_date': [fake.date_between(start_date='today', end_date='+30d') for _ in range(n_rows)],
        'last_payment_date': [fake.date_between(start_date='-2m') for _ in range(n_rows)],
        'last_payment_amount': np.round(np.random.uniform(50, 5000, n_rows), 2),
        'apr': np.round(np.random.uniform(12.0, 28.0, n_rows), 2),
    }
    return pd.DataFrame(data)

# ============== RISK & FRAUD DATA ==============

def gen_fraud_alerts(n_rows: int) -> pd.DataFrame:
    """Fraud alert records."""
    alert_types = ['unusual_location', 'high_amount', 'rapid_transactions', 'new_merchant', 'card_not_present', 'velocity_check']
    data = {
        'alert_id': [f'FRD{i:08d}' for i in range(n_rows)],
        'transaction_id': [f'TXN{random.randint(10000000, 99999999)}' for _ in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'alert_type': np.random.choice(alert_types, n_rows),
        'risk_score': np.round(np.random.uniform(0.5, 1.0, n_rows), 3),
        'amount': np.round(np.random.exponential(500, n_rows), 2),
        'alert_timestamp': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'resolution': np.random.choice(['confirmed_fraud', 'false_positive', 'pending_review', 'customer_verified'], n_rows, p=[0.15, 0.5, 0.2, 0.15]),
        'resolved_by': [fake.name() if random.random() > 0.2 else None for _ in range(n_rows)],
        'resolution_time_hours': np.where(np.random.random(n_rows) > 0.2, np.random.uniform(0.5, 72, n_rows), None),
    }
    return pd.DataFrame(data)

def gen_risk_assessments(n_rows: int) -> pd.DataFrame:
    """Customer risk assessment data."""
    data = {
        'assessment_id': [f'RSK{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'assessment_date': [fake.date_between(start_date='-1y') for _ in range(n_rows)],
        'risk_category': np.random.choice(['low', 'medium', 'high', 'critical'], n_rows, p=[0.5, 0.3, 0.15, 0.05]),
        'risk_score': np.round(np.random.uniform(0, 100, n_rows), 1),
        'credit_risk': np.round(np.random.uniform(0, 100, n_rows), 1),
        'fraud_risk': np.round(np.random.uniform(0, 100, n_rows), 1),
        'aml_risk': np.round(np.random.uniform(0, 100, n_rows), 1),
        'operational_risk': np.round(np.random.uniform(0, 100, n_rows), 1),
        'next_review_date': [fake.date_between(start_date='today', end_date='+1y') for _ in range(n_rows)],
        'assessed_by': [fake.name() for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_chargebacks(n_rows: int) -> pd.DataFrame:
    """Chargeback/dispute records."""
    reasons = ['fraud', 'merchandise_not_received', 'not_as_described', 'duplicate', 'cancelled', 'unauthorized']
    data = {
        'chargeback_id': [f'CB{i:08d}' for i in range(n_rows)],
        'transaction_id': [f'TXN{random.randint(10000000, 99999999)}' for _ in range(n_rows)],
        'merchant_id': [f'MER{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'amount': np.round(np.random.exponential(200, n_rows), 2),
        'reason_code': np.random.choice(reasons, n_rows),
        'filed_date': [fake.date_between(start_date='-1y') for _ in range(n_rows)],
        'status': np.random.choice(['pending', 'won', 'lost', 'settled'], n_rows, p=[0.3, 0.25, 0.25, 0.2]),
        'resolution_date': [fake.date_between(start_date='-6m') if random.random() > 0.3 else None for _ in range(n_rows)],
        'merchant_response': np.random.choice([True, False], n_rows, p=[0.7, 0.3]),
    }
    return pd.DataFrame(data)

def gen_aml_flags(n_rows: int) -> pd.DataFrame:
    """Anti-money laundering alerts."""
    flag_types = ['structuring', 'high_risk_country', 'unusual_pattern', 'pep_match', 'sanctions_hit', 'large_cash']
    data = {
        'flag_id': [f'AML{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'flag_type': np.random.choice(flag_types, n_rows),
        'severity': np.random.choice(['low', 'medium', 'high', 'critical'], n_rows, p=[0.3, 0.4, 0.2, 0.1]),
        'flagged_date': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'flagged_amount': np.round(np.random.exponential(10000, n_rows), 2),
        'status': np.random.choice(['open', 'investigating', 'escalated', 'closed_no_action', 'closed_sar_filed'], n_rows),
        'assigned_to': [fake.name() for _ in range(n_rows)],
        'notes': [fake.sentence() if random.random() > 0.3 else None for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_identity_verification(n_rows: int) -> pd.DataFrame:
    """Identity verification results."""
    data = {
        'verification_id': [f'IDV{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'verification_date': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'method': np.random.choice(['document', 'biometric', 'database', 'video_call'], n_rows),
        'id_type': np.random.choice(['passport', 'drivers_license', 'national_id', 'utility_bill'], n_rows),
        'result': np.random.choice(['pass', 'fail', 'manual_review', 'expired'], n_rows, p=[0.75, 0.1, 0.1, 0.05]),
        'confidence_score': np.round(np.random.uniform(0.5, 1.0, n_rows), 3),
        'face_match_score': np.round(np.random.uniform(0.6, 1.0, n_rows), 3),
        'document_authenticity': np.round(np.random.uniform(0.7, 1.0, n_rows), 3),
        'ip_address': [fake.ipv4() for _ in range(n_rows)],
        'device_fingerprint': [fake.uuid4() for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

# ============== OPERATIONS DATA ==============

def gen_branch_performance(n_rows: int) -> pd.DataFrame:
    """Branch performance metrics."""
    data = {
        'branch_id': [f'BR{i:04d}' for i in range(n_rows)],
        'branch_name': [f'{fake.city()} Branch' for _ in range(n_rows)],
        'region': np.random.choice(['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West'], n_rows),
        'state': [fake.state_abbr() for _ in range(n_rows)],
        'num_employees': np.random.randint(5, 50, n_rows),
        'total_deposits': np.round(np.random.exponential(50000000, n_rows), -3),
        'total_loans': np.round(np.random.exponential(30000000, n_rows), -3),
        'num_accounts': np.random.randint(1000, 50000, n_rows),
        'customer_satisfaction': np.round(np.random.uniform(3.0, 5.0, n_rows), 2),
        'operating_costs': np.round(np.random.uniform(100000, 1000000, n_rows), -2),
        'profit_margin_pct': np.round(np.random.uniform(5, 25, n_rows), 1),
        'report_date': [fake.date_between(start_date='-1y') for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_employee_data(n_rows: int) -> pd.DataFrame:
    """Employee records with PII."""
    data = {
        'employee_id': [f'EMP{i:06d}' for i in range(n_rows)],
        'first_name': [fake.first_name() for _ in range(n_rows)],
        'last_name': [fake.last_name() for _ in range(n_rows)],
        'email': [fake.company_email() for _ in range(n_rows)],
        'phone': [fake.phone_number() for _ in range(n_rows)],
        'department': np.random.choice(['operations', 'sales', 'risk', 'compliance', 'it', 'hr', 'finance'], n_rows),
        'job_title': [fake.job() for _ in range(n_rows)],
        'hire_date': [fake.date_between(start_date='-15y') for _ in range(n_rows)],
        'salary': np.round(np.random.uniform(40000, 200000, n_rows), -3),
        'branch_id': [f'BR{random.randint(1, 500):04d}' for _ in range(n_rows)],
        'manager_id': [f'EMP{random.randint(1, 1000):06d}' if random.random() > 0.1 else None for _ in range(n_rows)],
        'status': np.random.choice(['active', 'on_leave', 'terminated'], n_rows, p=[0.9, 0.05, 0.05]),
    }
    return pd.DataFrame(data)

def gen_call_center_logs(n_rows: int) -> pd.DataFrame:
    """Customer support call logs."""
    topics = ['account_inquiry', 'transaction_dispute', 'card_replacement', 'loan_inquiry', 'technical_support', 'complaint', 'general']
    data = {
        'call_id': [f'CALL{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'agent_id': [f'AGT{random.randint(100, 999)}' for _ in range(n_rows)],
        'call_start': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'call_duration_seconds': np.random.randint(30, 1800, n_rows),
        'topic': np.random.choice(topics, n_rows),
        'resolution': np.random.choice(['resolved', 'escalated', 'callback_scheduled', 'transferred'], n_rows, p=[0.7, 0.1, 0.1, 0.1]),
        'satisfaction_score': np.random.choice([1, 2, 3, 4, 5, None], n_rows, p=[0.05, 0.05, 0.15, 0.3, 0.35, 0.1]),
        'wait_time_seconds': np.random.randint(0, 600, n_rows),
        'is_callback': np.random.choice([True, False], n_rows, p=[0.15, 0.85]),
    }
    return pd.DataFrame(data)

def gen_complaint_records(n_rows: int) -> pd.DataFrame:
    """Customer complaint records."""
    categories = ['service_quality', 'fees', 'fraud', 'technical_issue', 'staff_behavior', 'wait_time', 'product_issue']
    data = {
        'complaint_id': [f'CMP{i:08d}' for i in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'category': np.random.choice(categories, n_rows),
        'subcategory': [fake.word() for _ in range(n_rows)],
        'description': [fake.paragraph() for _ in range(n_rows)],
        'submitted_date': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'channel': np.random.choice(['phone', 'email', 'web', 'branch', 'social_media'], n_rows),
        'priority': np.random.choice(['low', 'medium', 'high', 'critical'], n_rows, p=[0.3, 0.4, 0.2, 0.1]),
        'status': np.random.choice(['open', 'in_progress', 'resolved', 'closed'], n_rows, p=[0.2, 0.3, 0.3, 0.2]),
        'assigned_to': [fake.name() for _ in range(n_rows)],
        'resolution_date': [fake.date_between(start_date='-6m') if random.random() > 0.3 else None for _ in range(n_rows)],
        'compensation_amount': np.where(np.random.random(n_rows) > 0.8, np.random.uniform(10, 500, n_rows), 0),
    }
    return pd.DataFrame(data)

def gen_audit_logs(n_rows: int) -> pd.DataFrame:
    """System audit trail."""
    actions = ['login', 'logout', 'view_account', 'transfer', 'update_profile', 'change_password', 'export_data', 'admin_action']
    data = {
        'log_id': [f'LOG{i:010d}' for i in range(n_rows)],
        'timestamp': [fake.date_time_between(start_date='-6m') for _ in range(n_rows)],
        'user_id': [f'USR{random.randint(10000, 99999)}' for _ in range(n_rows)],
        'action': np.random.choice(actions, n_rows),
        'resource_type': np.random.choice(['account', 'transaction', 'customer', 'loan', 'report'], n_rows),
        'resource_id': [f'RES{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'ip_address': [fake.ipv4() for _ in range(n_rows)],
        'user_agent': [fake.user_agent() for _ in range(n_rows)],
        'status': np.random.choice(['success', 'failure', 'blocked'], n_rows, p=[0.9, 0.08, 0.02]),
        'error_message': [fake.sentence() if random.random() > 0.9 else None for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

# ============== INVESTMENT DATA ==============

def gen_portfolio_holdings(n_rows: int) -> pd.DataFrame:
    """Investment portfolio holdings."""
    asset_types = ['stock', 'bond', 'mutual_fund', 'etf', 'reit', 'commodity']
    data = {
        'holding_id': [f'HLD{i:08d}' for i in range(n_rows)],
        'portfolio_id': [f'PRT{random.randint(10000, 99999)}' for _ in range(n_rows)],
        'customer_id': [f'C{random.randint(100000, 999999)}' for _ in range(n_rows)],
        'asset_type': np.random.choice(asset_types, n_rows),
        'symbol': [fake.lexify('????').upper() for _ in range(n_rows)],
        'quantity': np.round(np.random.uniform(1, 1000, n_rows), 2),
        'avg_cost': np.round(np.random.uniform(10, 500, n_rows), 2),
        'current_price': np.round(np.random.uniform(10, 600, n_rows), 2),
        'market_value': np.round(np.random.uniform(1000, 500000, n_rows), 2),
        'unrealized_gain_loss': np.round(np.random.uniform(-50000, 100000, n_rows), 2),
        'as_of_date': [fake.date_between(start_date='-7d') for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_trade_history(n_rows: int) -> pd.DataFrame:
    """Trade execution history."""
    data = {
        'trade_id': [f'TRD{i:08d}' for i in range(n_rows)],
        'portfolio_id': [f'PRT{random.randint(10000, 99999)}' for _ in range(n_rows)],
        'symbol': [fake.lexify('????').upper() for _ in range(n_rows)],
        'trade_type': np.random.choice(['buy', 'sell'], n_rows),
        'quantity': np.round(np.random.uniform(1, 500, n_rows), 2),
        'price': np.round(np.random.uniform(10, 500, n_rows), 2),
        'total_amount': np.round(np.random.uniform(100, 100000, n_rows), 2),
        'commission': np.round(np.random.uniform(0, 50, n_rows), 2),
        'execution_time': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'order_type': np.random.choice(['market', 'limit', 'stop', 'stop_limit'], n_rows),
        'status': np.random.choice(['executed', 'cancelled', 'partial', 'rejected'], n_rows, p=[0.85, 0.08, 0.05, 0.02]),
    }
    return pd.DataFrame(data)

def gen_market_data(n_rows: int) -> pd.DataFrame:
    """Historical market price data."""
    data = {
        'symbol': [fake.lexify('????').upper() for _ in range(n_rows)],
        'date': [fake.date_between(start_date='-2y') for _ in range(n_rows)],
        'open': np.round(np.random.uniform(10, 500, n_rows), 2),
        'high': np.round(np.random.uniform(10, 520, n_rows), 2),
        'low': np.round(np.random.uniform(10, 480, n_rows), 2),
        'close': np.round(np.random.uniform(10, 500, n_rows), 2),
        'volume': np.random.randint(10000, 10000000, n_rows),
        'adjusted_close': np.round(np.random.uniform(10, 500, n_rows), 2),
        'dividend': np.where(np.random.random(n_rows) > 0.9, np.random.uniform(0.1, 2, n_rows), 0),
        'split_factor': np.where(np.random.random(n_rows) > 0.98, np.random.choice([2, 3, 4], n_rows), 1),
    }
    return pd.DataFrame(data)

def gen_fund_performance(n_rows: int) -> pd.DataFrame:
    """Mutual fund performance data."""
    data = {
        'fund_id': [f'FND{i:06d}' for i in range(n_rows)],
        'fund_name': [f'{fake.company()} Fund' for _ in range(n_rows)],
        'category': np.random.choice(['equity', 'fixed_income', 'balanced', 'money_market', 'sector', 'international'], n_rows),
        'nav': np.round(np.random.uniform(10, 500, n_rows), 2),
        'expense_ratio': np.round(np.random.uniform(0.05, 2.0, n_rows), 2),
        'ytd_return_pct': np.round(np.random.uniform(-20, 40, n_rows), 2),
        '1yr_return_pct': np.round(np.random.uniform(-30, 50, n_rows), 2),
        '3yr_return_pct': np.round(np.random.uniform(-10, 80, n_rows), 2),
        '5yr_return_pct': np.round(np.random.uniform(0, 150, n_rows), 2),
        'total_assets': np.round(np.random.exponential(1000000000, n_rows), -6),
        'morningstar_rating': np.random.randint(1, 6, n_rows),
        'as_of_date': [fake.date_between(start_date='-30d') for _ in range(n_rows)],
    }
    return pd.DataFrame(data)

def gen_dividend_payments(n_rows: int) -> pd.DataFrame:
    """Dividend payment records."""
    data = {
        'dividend_id': [f'DIV{i:08d}' for i in range(n_rows)],
        'portfolio_id': [f'PRT{random.randint(10000, 99999)}' for _ in range(n_rows)],
        'symbol': [fake.lexify('????').upper() for _ in range(n_rows)],
        'ex_date': [fake.date_between(start_date='-2y') for _ in range(n_rows)],
        'pay_date': [fake.date_between(start_date='-2y') for _ in range(n_rows)],
        'dividend_per_share': np.round(np.random.uniform(0.1, 5, n_rows), 4),
        'shares_held': np.round(np.random.uniform(10, 1000, n_rows), 2),
        'total_amount': np.round(np.random.uniform(10, 5000, n_rows), 2),
        'dividend_type': np.random.choice(['regular', 'special', 'qualified'], n_rows, p=[0.85, 0.1, 0.05]),
        'reinvested': np.random.choice([True, False], n_rows, p=[0.4, 0.6]),
    }
    return pd.DataFrame(data)

# ============== DATASET DEFINITIONS ==============

DATASET_CONFIGS = [
    # Transaction Data (15)
    {"name": "credit_card_transactions", "generator": gen_credit_card_transactions, "rows": 100000, "quality": 0.95},
    {"name": "credit_card_small", "generator": gen_credit_card_transactions, "rows": 500, "quality": 0.98},
    {"name": "bank_transfers", "generator": gen_bank_transfers, "rows": 50000, "quality": 0.90},
    {"name": "bank_transfers_intl", "generator": gen_bank_transfers, "rows": 10000, "quality": 0.85},
    {"name": "atm_withdrawals", "generator": gen_atm_withdrawals, "rows": 30000, "quality": 0.95},
    {"name": "atm_withdrawals_regional", "generator": gen_atm_withdrawals, "rows": 5000, "quality": 0.92},
    {"name": "payment_history", "generator": gen_payment_history, "rows": 80000, "quality": 0.88},
    {"name": "payment_history_recent", "generator": gen_payment_history, "rows": 15000, "quality": 0.95},
    {"name": "forex_transactions", "generator": gen_forex_transactions, "rows": 25000, "quality": 0.90},
    {"name": "forex_transactions_daily", "generator": gen_forex_transactions, "rows": 2000, "quality": 0.98},
    {"name": "transactions_summary", "generator": gen_credit_card_transactions, "rows": 200000, "quality": 0.85},
    {"name": "transactions_q1_2024", "generator": gen_credit_card_transactions, "rows": 75000, "quality": 0.92},
    {"name": "transactions_q2_2024", "generator": gen_credit_card_transactions, "rows": 80000, "quality": 0.91},
    {"name": "wire_transfers_large", "generator": gen_bank_transfers, "rows": 8000, "quality": 0.88},
    {"name": "instant_payments", "generator": gen_bank_transfers, "rows": 45000, "quality": 0.93},
    
    # Customer Data (15)
    {"name": "customer_demographics", "generator": lambda n: gen_customer_demographics(n, True), "rows": 50000, "quality": 0.92, "has_pii": True},
    {"name": "customer_demographics_anon", "generator": lambda n: gen_customer_demographics(n, False), "rows": 50000, "quality": 0.95},
    {"name": "account_holders", "generator": gen_account_holders, "rows": 100000, "quality": 0.90},
    {"name": "account_holders_active", "generator": gen_account_holders, "rows": 30000, "quality": 0.96},
    {"name": "credit_scores", "generator": gen_credit_scores, "rows": 75000, "quality": 0.88},
    {"name": "credit_scores_monthly", "generator": gen_credit_scores, "rows": 10000, "quality": 0.95},
    {"name": "customer_segments", "generator": gen_customer_segments, "rows": 40000, "quality": 0.92},
    {"name": "customer_segments_premium", "generator": gen_customer_segments, "rows": 5000, "quality": 0.98},
    {"name": "kyc_records", "generator": gen_kyc_records, "rows": 60000, "quality": 0.85, "has_pii": True},
    {"name": "kyc_records_pending", "generator": gen_kyc_records, "rows": 3000, "quality": 0.75, "has_pii": True},
    {"name": "customer_master", "generator": lambda n: gen_customer_demographics(n, True), "rows": 150000, "quality": 0.82, "has_pii": True},
    {"name": "customer_contacts", "generator": lambda n: gen_customer_demographics(n, True), "rows": 80000, "quality": 0.78, "has_pii": True},
    {"name": "high_value_customers", "generator": gen_customer_segments, "rows": 2000, "quality": 0.99},
    {"name": "new_customers_2024", "generator": lambda n: gen_customer_demographics(n, True), "rows": 15000, "quality": 0.95, "has_pii": True},
    {"name": "customer_preferences", "generator": gen_customer_segments, "rows": 35000, "quality": 0.88},
    
    # Loan Data (15)
    {"name": "mortgage_applications", "generator": gen_mortgage_applications, "rows": 25000, "quality": 0.90},
    {"name": "mortgage_applications_approved", "generator": gen_mortgage_applications, "rows": 15000, "quality": 0.95},
    {"name": "personal_loans", "generator": gen_personal_loans, "rows": 40000, "quality": 0.88},
    {"name": "personal_loans_active", "generator": gen_personal_loans, "rows": 20000, "quality": 0.92},
    {"name": "auto_loans", "generator": gen_auto_loans, "rows": 35000, "quality": 0.90},
    {"name": "auto_loans_new", "generator": gen_auto_loans, "rows": 8000, "quality": 0.95},
    {"name": "loan_defaults", "generator": gen_loan_defaults, "rows": 5000, "quality": 0.85},
    {"name": "loan_defaults_historical", "generator": gen_loan_defaults, "rows": 15000, "quality": 0.78},
    {"name": "credit_line_usage", "generator": gen_credit_line_usage, "rows": 60000, "quality": 0.92},
    {"name": "credit_line_high_util", "generator": gen_credit_line_usage, "rows": 10000, "quality": 0.88},
    {"name": "loan_portfolio", "generator": gen_personal_loans, "rows": 100000, "quality": 0.82},
    {"name": "loan_applications_q1", "generator": gen_mortgage_applications, "rows": 12000, "quality": 0.90},
    {"name": "loan_applications_q2", "generator": gen_mortgage_applications, "rows": 14000, "quality": 0.89},
    {"name": "delinquent_loans", "generator": gen_loan_defaults, "rows": 8000, "quality": 0.80},
    {"name": "loan_modifications", "generator": gen_personal_loans, "rows": 3000, "quality": 0.85},
    
    # Risk & Fraud (15)
    {"name": "fraud_alerts", "generator": gen_fraud_alerts, "rows": 20000, "quality": 0.92},
    {"name": "fraud_alerts_confirmed", "generator": gen_fraud_alerts, "rows": 3000, "quality": 0.95},
    {"name": "risk_assessments", "generator": gen_risk_assessments, "rows": 50000, "quality": 0.88},
    {"name": "risk_assessments_high", "generator": gen_risk_assessments, "rows": 5000, "quality": 0.90},
    {"name": "chargebacks", "generator": gen_chargebacks, "rows": 15000, "quality": 0.85},
    {"name": "chargebacks_pending", "generator": gen_chargebacks, "rows": 4000, "quality": 0.80},
    {"name": "aml_flags", "generator": gen_aml_flags, "rows": 8000, "quality": 0.88},
    {"name": "aml_flags_escalated", "generator": gen_aml_flags, "rows": 1500, "quality": 0.92},
    {"name": "identity_verification", "generator": gen_identity_verification, "rows": 40000, "quality": 0.90},
    {"name": "identity_verification_failed", "generator": gen_identity_verification, "rows": 5000, "quality": 0.75},
    {"name": "suspicious_activity", "generator": gen_fraud_alerts, "rows": 12000, "quality": 0.85},
    {"name": "transaction_monitoring", "generator": gen_fraud_alerts, "rows": 100000, "quality": 0.88},
    {"name": "sanctions_screening", "generator": gen_aml_flags, "rows": 25000, "quality": 0.92},
    {"name": "fraud_investigation", "generator": gen_fraud_alerts, "rows": 6000, "quality": 0.82},
    {"name": "risk_scores_daily", "generator": gen_risk_assessments, "rows": 30000, "quality": 0.90},
    
    # Operations (10)
    {"name": "branch_performance", "generator": gen_branch_performance, "rows": 500, "quality": 0.95},
    {"name": "branch_performance_monthly", "generator": gen_branch_performance, "rows": 6000, "quality": 0.92},
    {"name": "employee_data", "generator": gen_employee_data, "rows": 5000, "quality": 0.90, "has_pii": True},
    {"name": "employee_directory", "generator": gen_employee_data, "rows": 2000, "quality": 0.95, "has_pii": True},
    {"name": "call_center_logs", "generator": gen_call_center_logs, "rows": 150000, "quality": 0.85},
    {"name": "call_center_daily", "generator": gen_call_center_logs, "rows": 10000, "quality": 0.92},
    {"name": "complaint_records", "generator": gen_complaint_records, "rows": 20000, "quality": 0.88},
    {"name": "complaint_records_open", "generator": gen_complaint_records, "rows": 3000, "quality": 0.82},
    {"name": "audit_logs", "generator": gen_audit_logs, "rows": 500000, "quality": 0.98},
    {"name": "audit_logs_security", "generator": gen_audit_logs, "rows": 50000, "quality": 0.95},
    
    # Investment (10)
    {"name": "portfolio_holdings", "generator": gen_portfolio_holdings, "rows": 80000, "quality": 0.92},
    {"name": "portfolio_holdings_active", "generator": gen_portfolio_holdings, "rows": 30000, "quality": 0.95},
    {"name": "trade_history", "generator": gen_trade_history, "rows": 200000, "quality": 0.90},
    {"name": "trade_history_recent", "generator": gen_trade_history, "rows": 25000, "quality": 0.95},
    {"name": "market_data", "generator": gen_market_data, "rows": 100000, "quality": 0.98},
    {"name": "market_data_daily", "generator": gen_market_data, "rows": 5000, "quality": 0.99},
    {"name": "fund_performance", "generator": gen_fund_performance, "rows": 2000, "quality": 0.95},
    {"name": "fund_performance_quarterly", "generator": gen_fund_performance, "rows": 8000, "quality": 0.92},
    {"name": "dividend_payments", "generator": gen_dividend_payments, "rows": 50000, "quality": 0.90},
    {"name": "dividend_payments_ytd", "generator": gen_dividend_payments, "rows": 15000, "quality": 0.95},
]


def generate_all_datasets():
    """Generate all synthetic datasets."""
    manifest = []
    
    print(f"Generating {len(DATASET_CONFIGS)} datasets...")
    print(f"Output directory: {OUTPUT_DIR}")
    print("-" * 50)
    
    for i, config in enumerate(DATASET_CONFIGS, 1):
        name = config["name"]
        generator = config["generator"]
        n_rows = config["rows"]
        quality = config.get("quality", 0.95)
        has_pii = config.get("has_pii", False)
        
        print(f"[{i}/{len(DATASET_CONFIGS)}] Generating {name}... ", end="", flush=True)
        
        try:
            # Generate data
            df = generator(n_rows)
            
            # Add quality issues based on quality level
            null_pct = (1 - quality) * 0.5
            if null_pct > 0:
                # Add nulls to random columns (except ID columns)
                for col in df.columns:
                    if not col.endswith('_id') and df[col].dtype in ['object', 'float64', 'int64']:
                        mask = np.random.random(len(df)) < null_pct
                        df.loc[mask, col] = None
            
            # Save to CSV
            filepath = OUTPUT_DIR / f"{name}.csv"
            df.to_csv(filepath, index=False)
            
            # Add to manifest
            manifest.append({
                "name": name,
                "filename": f"{name}.csv",
                "rows": len(df),
                "columns": len(df.columns),
                "size_bytes": filepath.stat().st_size,
                "has_pii": has_pii,
                "quality_level": quality,
                "column_names": list(df.columns),
            })
            
            print(f"✓ ({len(df):,} rows, {len(df.columns)} cols)")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Save manifest
    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_datasets": len(manifest),
            "datasets": manifest
        }, f, indent=2)
    
    print("-" * 50)
    print(f"✓ Generated {len(manifest)} datasets")
    print(f"✓ Manifest saved to {manifest_path}")
    
    # Summary stats
    total_rows = sum(d["rows"] for d in manifest)
    total_size = sum(d["size_bytes"] for d in manifest)
    pii_count = sum(1 for d in manifest if d["has_pii"])
    
    print(f"\nSummary:")
    print(f"  Total rows: {total_rows:,}")
    print(f"  Total size: {total_size / 1024 / 1024:.1f} MB")
    print(f"  Datasets with PII: {pii_count}")


if __name__ == "__main__":
    generate_all_datasets()
