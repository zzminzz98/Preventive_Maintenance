# NASA CMAPSS Predictive Maintenance Pipeline

An end-to-end machine learning pipeline for predicting Remaining Useful Life (RUL) of turbofan engines using the NASA C-MAPSS (FD001) dataset. This project integrates SQLite3 database normalization, Python ETL workflows, feature engineering, and Random Forest regression.

---

## Project Overview
Predictive maintenance helps forecast equipment failures before they happen, minimizing unexpected downtime. This project processes multi-sensor time-series telemetry data to predict how many operational cycles an engine has left before failure.

## Pipeline Architecture
To run this pipeline from scratch, execute the Python scripts in the following sequence:

1. **`logger_config.py`** – Reusable module for production-style timestamped logging across all scripts.
2. **`data_check.py`** – Validates raw text data integrity in `CMAPSSData/` before ingestion.
3. **`sql_dataset.py`** – Converts and loads raw data into a local SQLite database (`cmapss.db`).
4. **`calculate_rul.py`** – Computes the target Remaining Useful Life (RUL) for each engine cycle.
5. **`feature_engineering.py`** - Explores temporal feature extraction using rolling windows (mean and standard deviation) across 21 sensor streams.
6. **`train_model.py`** – Trains the baseline Random Forest model.
7. **`evaluate_model.py`** – Evaluates model performance on the test set and outputs metrics.
8. **`model_eval_results.py`** - Record of model's metric results. 


## Results & Experimentation 
| Model Configuration | Test RMSE (cycles) | Test MAE (cycles) | Test $R^2$ Score |
| :--- | :--- | :--- | :--- |
| **Clipping-Only Baseline** | **18.11** | **13.20** | **0.8100** |
| **Clipping + Rolling Windows (5-cycle)** | 19.18 | 14.00 | 0.7870 |

* **Key Takeaway**: The clipping-only baseline generalized better on the test set. While rolling windows capture short-term momentum, they also introduced minor feat.

---

## Feature Importance & Analytical Insights

Extracting feature importances from the trained Random Forest model revealed a striking dominance of temporal trends: **`sensor_4_roll_mean` alone accounts for over 61% of the model's total decision-making power**, followed by sensors 9, 11, and 14. 

* **The Dominance of Exhaust Temperature Trends**: In the C-MAPSS dataset, Sensor 4 measures core engine exhaust temperature, which exhibits a strong, continuous upward drift as degradation accumulates. The Random Forest naturally prioritizes features that display these smooth, monotonic trajectories.
* **The Training vs. Generalization Paradox**: Although rolling means captured over 90% of the top feature importances during training, the *clipping-only baseline* ultimately generalized better on unseen test data (RMSE 18.11 vs. 19.18). While rolling features provide rich historical momentum, they also introduce dimensionality overhead and localized noise that can slightly impair final-cycle test predictions on unseen engines.

---

## Tech Stack
* **Language**: Python
* **Data Manipulation**: Pandas, NumPy
* **Database**: SQLite3
* **Machine Learning**: Scikit-Learn (Random Forest Regressor)
* **Logging**: Custom Python logging configuration