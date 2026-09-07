# Credit Card Fraud Detection

An end-to-end machine learning project for credit card fraud detection, combining transaction-level inference, an operational decision policy, persistence, and real-time monitoring.

## Overview

The project addresses the challenge of detecting fraudulent transactions in a highly imbalanced environment while minimizing unnecessary intervention on legitimate transactions.

Each transaction is processed individually through the following pipeline:

```text
Transaction
    ↓
Feature Engineering
    ↓
CatBoost
    ↓
Risk Score
    ↓
Decision Policy
    ↓
Approve / Review / Critical Alert
    ↓
SQLite
    ↓
Monitoring Dashboard
```

The decision policy uses three operational risk levels:

| Risk score | Decision |
|---|---|
| `< 0.20` | Approve |
| `0.20 – 0.90` | Review |
| `>= 0.90` | Critical Alert |

## Dashboard

The Streamlit dashboard provides real-time monitoring of processed transactions, flagged operations, operational metrics, and financial exposure.

It also includes transaction investigation tools and commercial metrics such as processed volume, released volume, critical exposure, financial coverage, and financial friction.

## Running the Project

Clone the repository and install the dependencies:

```bash
git clone https://github.com/<your-user>/ccard_fraud_ml.git
cd ccard_fraud_ml

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Start the system:

```bash
python main.py
```

The command starts both the transaction processing worker and the Streamlit dashboard.

Stop the application with:

```text
Ctrl+C
```

## Stack

Python, CatBoost, Pandas, NumPy, scikit-learn, SQLite, Streamlit and Plotly.
