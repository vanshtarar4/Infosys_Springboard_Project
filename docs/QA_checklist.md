# QA Checklist - Milestone 1

## Overview
Quality assurance checklist for validating Milestone 1 deliverables of the Predictive Transaction Intelligence system.

---

## 🔄 Automated Tests

### Data Integrity Tests
Run: `pytest tests/test_data_integrity.py -v`

- ✅ All transaction IDs are non-null
- ✅ All transaction IDs are unique
- ✅ All transaction amounts > 0
- ✅ `is_fraud` contains only 0 or 1
- ✅ `kyc_verified` is binary (0/1)
- ✅ Channel values are standardized
- ✅ Account ages are non-negative
- ✅ High-value flags are correct
- ✅ Timestamps are valid datetime
- ✅ No missing required columns
- ✅ Fraud rate is reasonable (0-50%)

### Data Cleaning Tests
Run: `pytest tests/test_cleaning.py -v`

- ✅ No null transaction IDs in processed data
- ✅ No null transaction amounts
- ✅ All amounts are positive
- ✅ KYC verified is binary
- ✅ Channels are standardized
- ✅ Timestamps are parseable
- ✅ High-value flags match amounts
- ✅ Required columns exist
- ✅ No duplicate transaction IDs

### API Tests
Run: `pytest tests/test_api.py -v`

- ✅ Health check returns 200
- ✅ Metrics endpoint returns required keys
- ✅ Metrics values are numeric
- ✅ Metrics values are non-null
- ✅ Fraud rate calculation is correct
- ✅ Transactions endpoint returns data
- ✅ Pagination works correctly

### Train/Test Split Tests
Run: `pytest tests/test_data_integrity.py::TestTrainTestSplit -v`

- ✅ No transaction ID overlap
- ✅ Class balance is maintained

---

## 📁 Manual File Checks

### Data Files

**Raw Data**
- [ ] File exists: `data/raw/transactions.csv`
- [ ] File has 5000 rows
- [ ] Contains all 8 required columns

**Processed Data**
- [ ] File exists: `data/processed/transactions_processed.csv`
- [ ] Preview file exists: `data/processed/transactions_preview.csv` (500 rows)
- [ ] No null values in critical columns
- [ ] Engineered features present (16 total columns)

**Train/Test Split**
- [ ] File exists: `data/processed/train.csv`
- [ ] File exists: `data/processed/test.csv`
- [ ] Train set is ~80% of total
- [ ] Test set is ~20% of total
- [ ] Split metadata exists: `configs/split_info.json`

**Database**
- [ ] File exists: `data/transactions.db`
- [ ] Contains `transactions` table
- [ ] Row count matches processed CSV

### EDA Visualizations

**Required Figures** (in `docs/figs/`)
- [ ] `fig1_fraud_count.png` - Fraud distribution bar chart
- [ ] `fig2_box_amount.png` - Amount boxplots (linear & log)
- [ ] `fig3_heatmap_time.png` - Time activity heatmap
- [ ] `fig4_channel_fraud.png` - Channel fraud rates
- [ ] `fig5_segment_risk.png` - Account age risk segments
- [ ] `fig6_kyc_impact.png` - KYC effectiveness

**Visual Quality Check**
- [ ] All images are high resolution (300 DPI)
- [ ] Labels are readable
- [ ] Axes are properly labeled
- [ ] Legends are clear
- [ ] Colors are distinguishable

### Documentation

**Core Documentation**
- [ ] File exists: `README.md`
- [ ] Contains project overview
- [ ] Contains Milestone 1 objectives
- [ ] Contains API running instructions
- [ ] Contains development branch info

**EDA Summary**
- [ ] File exists: `docs/EDA_summary.md`
- [ ] Contains all 6 figure descriptions
- [ ] Includes statistical insights
- [ ] Lists key findings
- [ ] Provides recommendations

**Notebooks**
- [ ] File exists: `notebooks/eda_milestone1.ipynb`
- [ ] Notebook is executable
- [ ] HTML export exists: `notebooks/eda_milestone1.html`

**Configuration**
- [ ] File exists: `configs/data_profile.json`
- [ ] Contains schema information
- [ ] File exists: `configs/split_info.json`
- [ ] Contains split statistics

---

## 🌐 API Endpoint Checks

### Backend API Health
Start backend: `python -m src.api.app --port 8001`

**Endpoint: GET /api/health**
```bash
curl http://localhost:8001/api/health
```
- [ ] Returns 200 status code
- [ ] Returns `{"success": true, "status": "healthy"}`

**Endpoint: GET /api/metrics**
```bash
curl http://localhost:8001/api/metrics
```
- [ ] Returns 200 status code
- [ ] Contains `total_transactions`
- [ ] Contains `fraud_count`
- [ ] Contains `fraud_rate`
- [ ] Contains `avg_amount`
- [ ] Contains `avg_amount_fraud`
- [ ] All values are numeric and positive

**Endpoint: GET /api/transactions**
```bash
curl "http://localhost:8001/api/transactions?limit=10"
```
- [ ] Returns 200 status code
- [ ] Returns array of transactions
- [ ] Contains pagination info
- [ ] Limit parameter works
- [ ] Offset parameter works

**Endpoint: GET /api/transactions/sample**
```bash
curl http://localhost:8001/api/transactions/sample
```
- [ ] Returns 200 status code
- [ ] Returns 500 sample records

**Endpoint: GET /api/download/processed**
```bash
curl -O http://localhost:8001/api/download/processed
```
- [ ] Returns CSV file
- [ ] File downloads successfully
- [ ] Content-Type is text/csv

---

## 💻 Frontend Application Checks

### Frontend Setup
Navigate to: `cd frontend && npm install && npm run dev`

**Homepage (Dashboard) - http://localhost:3000**
- [ ] Page loads without errors
- [ ] All 6 metric cards display
- [ ] Values are loaded from API
- [ ] Loading state shows before data loads
- [ ] Download CSV button works
- [ ] Quick action links work
- [ ] Navigation menu functional

**Transactions Page - http://localhost:3000/transactions**
- [ ] Page loads without errors
- [ ] Transaction table displays
- [ ] Data is fetched from API
- [ ] Pagination controls visible
- [ ] Pagination works (Next/Previous)
- [ ] Fraud badges display correctly
- [ ] KYC status shows correctly
- [ ] Channel chips are colored

**Analytics Page - http://localhost:3000/analytics**
- [ ] Page loads without errors
- [ ] All 6 charts display (if images copied)
- [ ] Chart descriptions are visible
- [ ] Responsive layout works
- [ ] Images load without 404 errors

**Upload Page - http://localhost:3000/upload**
- [ ] Page loads without errors
- [ ] File drop zone is visible
- [ ] File selection dialog works
- [ ] Upload button is present
- [ ] Format requirements displayed

### Responsive Design
- [ ] Dashboard works on mobile (< 768px)
- [ ] Transactions table scrolls horizontally on mobile
- [ ] Analytics charts stack vertically on mobile
- [ ] Navigation collapses appropriately
- [ ] All text is readable

---

## 🔧 Code Quality

### Python Code
- [ ] All Python files have docstrings
- [ ] Functions have type hints where applicable
- [ ] Code follows PEP 8 style guide
- [ ] No unused imports
- [ ] No print statements in production code

**Run Linter:**
```bash
flake8 src tests --max-line-length=127
```

### Git Repository
- [ ] `.gitignore` exists and is comprehensive
- [ ] No sensitive data (API keys, passwords) in repo
- [ ] All branches exist: `main`, `backend`, `frontend`
- [ ] Commit messages are descriptive
- [ ] No large binary files in git history

---

## 📊 Data Quality Metrics

### Expected Statistics
Based on 5000 transaction dataset:

- **Total Transactions**: 5000 (after cleaning: ~4900-5000)
- **Fraud Rate**: 4-9%
- **Channels**: Web, Mobile, POS, ATM, Other
- **KYC Coverage**: > 50% verified
- **High-Value Transactions**: 5-10%

### Data Validation Commands

**Check row counts:**
```bash
python -c "import pandas as pd; print('Processed:', len(pd.read_csv('data/processed/transactions_processed.csv'))); print('Train:', len(pd.read_csv('data/processed/train.csv'))); print('Test:', len(pd.read_csv('data/processed/test.csv')))"
```

**Check fraud distribution:**
```bash
python -c "import pandas as pd; df = pd.read_csv('data/processed/transactions_processed.csv'); print(df['is_fraud'].value_counts(normalize=True) * 100)"
```

**Verify no nulls:**
```bash
python -c "import pandas as pd; df = pd.read_csv('data/processed/transactions_processed.csv'); print('Nulls:', df.isnull().sum().sum())"
```

---

## ✅ Final Checklist

### Milestone 1 Deliverables

**Data Pipeline** ✓
- [x] Raw data ingestion (5000 transactions)
- [x] Data cleaning and preprocessing
- [x] Feature engineering (8 new features)
- [x] Train/test split with stratification
- [x] SQLite database ingestion

**Exploratory Data Analysis** ✓
- [x] Jupyter notebook with analysis
- [x] 6 publication-quality visualizations
- [x] EDA summary document
- [x] Statistical insights and recommendations

**Backend API** ✓
- [x] Flask application
- [x] 5 RESTful endpoints
- [x] CORS enabled
- [x] Error handling
- [x] API documentation

**Frontend Application** ✓
- [x] Next.js with TypeScript
- [x] Dashboard with metrics
- [x] Transactions table with pagination
- [x] Analytics page with charts
- [x] Upload page (placeholder)
- [x] Responsive design

**Testing & QA** ✓
- [x] Data integrity tests
- [x] API endpoint tests
- [x] GitHub Actions CI workflow
- [x] QA checklist documentation

**Documentation** ✓
- [x] Project README
- [x] EDA summary
- [x] API documentation
- [x] Frontend documentation
- [x] QA checklist

---

## 🚀 Running All Tests

**Run complete test suite:**
```bash
# Data tests
pytest tests/test_data_integrity.py -v

# Cleaning tests
pytest tests/test_cleaning.py -v

# API tests
pytest tests/test_api.py -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected Results:**
- All tests should PASS ✅
- Coverage should be > 70%
- No critical errors or warnings

---

## 📝 Sign-Off

**Tested By**: _________________  
**Date**: _________________  
**Build Version**: _________________  
**Status**: ⬜ PASS  ⬜ FAIL  ⬜ PASS WITH NOTES

**Notes**:
_____________________________________________
_____________________________________________
_____________________________________________

---

## 🔍 Troubleshooting Common Issues

**Issue: Tests fail with "file not found"**
- Solution: Run tests from project root directory
- Verify data files exist in correct locations

**Issue: API connection refused**
- Solution: Ensure Flask backend is running on port 8001
- Check firewall settings

**Issue: Frontend charts not displaying**
- Solution: Copy PNG files to `frontend/public/assets/charts/`
- Verify file names match exactly (case-sensitive)

**Issue: Import errors in tests**
- Solution: Install all requirements: `pip install -r requirements.txt`
- Verify Python version is 3.9+

---

**Last Updated**: December 23, 2024  
**Version**: 1.0  
**Milestone**: 1
