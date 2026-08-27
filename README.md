# NASA CMAPSS Predictive Maintenance Pipeline

A machine learning pipeline built to predict Remaining Useful Life (RUL) of aircraft turbofan engines using the NASA CMAPSS dataset (FD001).

## Execution Order
To run this pipeline from scratch, execute the Python scripts in the following sequence:

1. **`logger_config.py`** – Reusable module for production-style timestamped logging across all scripts.
2. **`data_check.py`** – Validates raw text data integrity in `CMAPSSData/` before ingestion.
3. **`sql_dataset.py`** – Converts and loads raw data into a local SQLite database (`cmapss.db`).
4. **`calculate_rul.py`** – Computes the target Remaining Useful Life (RUL) for each engine cycle.
5. **`train_model.py`** – Trains the baseline Random Forest model.
6. **`evaluate_model.py`** – Evaluates model performance on the test set and outputs metrics.
