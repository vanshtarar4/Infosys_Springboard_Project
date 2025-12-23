# Predictive Transaction Intelligence for BFSI

## Project Overview
This project implements predictive transaction intelligence for the Banking, Financial Services, and Insurance (BFSI) sector, focusing on fraud detection and risk assessment.

## Milestone 1 Objectives
1. **Data Acquisition & Exploration**
   - Gather and understand transaction datasets
   - Perform exploratory data analysis (EDA)
   - Identify key patterns and anomalies

2. **Data Preprocessing**
   - Handle missing values and outliers
   - Feature engineering for transaction data
   - Data normalization and scaling

3. **Initial Model Development**
   - Baseline model creation
   - Feature selection and importance analysis
   - Model evaluation metrics setup

## Project Structure
```
project_root/
├── data/              # Data storage
├── notebooks/         # Jupyter notebooks for analysis
├── src/              # Source code
├── docs/             # Documentation and reports
├── configs/          # Configuration files
└── tests/            # Unit tests
```

## Milestone 2 Objectives - Predictive Modeling

### Overview
Develop and deploy machine learning models for fraud detection using the preprocessed transaction data from Milestone 1.

### Goals
1. **Model Training**
   - Train Random Forest classifier on processed data
   - Handle class imbalance with appropriate techniques
   - Perform hyperparameter tuning
   - Cross-validate model performance

2. **Model Evaluation**
   - Evaluate on test set with comprehensive metrics
   - Generate ROC curves and precision-recall curves
   - Analyze feature importance
   - Validate model robustness

3. **Model Deployment**
   - Save trained model artifacts
   - Create prediction API endpoint
   - Integrate with existing Flask backend
   - Enable real-time fraud scoring

### Modeling Workflow
```
data/processed/train.csv → Model Training → models/fraud_model.joblib
                                           ↓
data/processed/test.csv  → Model Evaluation → Metrics & Plots
                                           ↓
                           API Integration → /api/predict endpoint
```

### Key Deliverables
- ✅ Training pipeline (`src/modeling/train_model.py`)
- ✅ Evaluation pipeline (`src/modeling/evaluate_model.py`)
- ✅ Feature utilities (`src/modeling/feature_utils.py`)
- 🔄 Trained model artifacts (`models/`)
- 🔄 Prediction API endpoint
- 🔄 Model performance report

## Development Branches
- **main**: Stable production-ready code
- **backend**: Backend development and API implementation
- **frontend**: Frontend UI/UX development

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Check out the appropriate branch for your work
3. Review the EDA summary in `docs/EDA_summary.md`

## Running the API Server
Start the Flask API server on port 8001:
```bash
# Using Python module
python -m src.api.app --port 8001

# Or using Flask CLI
set FLASK_APP=src/api/app.py
flask run --port 8001

# With debug mode
python -m src.api.app --port 8001 --debug
```

API will be available at: `http://localhost:8001`

### API Endpoints
- `GET /api/transactions?limit=100` - Paginated transaction data
- `GET /api/transactions/sample` - Sample preview data
- `GET /api/metrics` - Transaction statistics
- `GET /api/download/processed` - Download full CSV
- `GET /api/health` - Health check
