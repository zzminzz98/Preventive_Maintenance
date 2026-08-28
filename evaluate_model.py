import sqlite3
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
from logger_config import setup_logger

logger = setup_logger(__name__)

DATABASE_NAME = 'cmapss.db'
TEST_TABLE = 'test_fd001'
RUL_TABLE = 'rul_fd001'
MODEL_FILENAME = 'random_forest_baseline.pkl'


def evaluate_model(window_size=5):
    try:
        logger.info(f"Connect to database: {DATABASE_NAME}")
        conn = sqlite3.connect(DATABASE_NAME)

        # 1.Select and retrieve dataset from SQL 
        logger.info(f"Loading test data from *{TEST_TABLE}* and true RUL from *{RUL_TABLE}*")
        df_test = pd.read_sql(f"Select * FROM {TEST_TABLE}", conn)
        df_true_rul = pd.read_sql(f"SELECT * FROM {RUL_TABLE}", conn)

        # 2. Calculate rolling mean and std
        logger.info("="*100)
        sensor_cols = [col for col in df_test.columns if 'sensor' in col]

        for col in sensor_cols:
            # Rolling mean
            df_test[f'{col}_roll_mean'] = (
                df_test.groupby('unit_number')[col].transform(lambda x: x.rolling(
                    window_size, min_periods=1).mean())
            )

            # Rolling std
            df_test[f'{col}_roll_std'] = (
                df_test.groupby('unit_number')[col].transform(lambda x:x.rolling(
                    window_size, min_periods=1).std()).fillna(0)
            )

        logger.info(f"Rolling mean and std calculation completed for {TEST_TABLE}")

        # 3.Transform dataset for evaluation
        logger.info("Extract last recorded cycle for each test engine unit with rolling features are computed")
        # Retrive unit_number's max cycle op setting and sensors
        idx_last_cycles = df_test.groupby('unit_number')['cycle'].idxmax() # max value's index
        # use index to get row data (iloc for rows)
        df_test_last = df_test.loc[idx_last_cycles].reset_index(drop=True)

        logger.info(f"Completed transforming {TEST_TABLE}. Sample head preview:\n%s", df_test_last[
            ['unit_number','cycle','sensor_2','sensor_2_roll_mean','sensor_2_roll_std']].head().to_string())

        # Merge true RUL values with df_test_last
        df_eval = pd.merge(df_test_last, df_true_rul, how='inner', on='unit_number')

        # 4. Define features X_test and true target y_true
        logger.info("="*100)
        drop_cols = ['unit_number', 'cycle', 'remaining_cycles']
        feature_cols = [col for col in df_eval.columns if col not in drop_cols]

        X_test = df_eval[feature_cols]
        y_true = df_eval['remaining_cycles']

        logger.info("Define variables to test model")
        logger.info("Total feature used: %d", len(feature_cols))
        logger.info("Feature columns: %s", feature_cols)
        logger.info("Target column: ['remaining_cycles']")
        logger.info("Target 'remaining_cycles' sample preview (first 5 rows):\n%s", y_true.head().to_string())

        # 5. Load training model artifact
        logger.info("="*100)
        logger.info(f"Load model artifact from {MODEL_FILENAME}")
        model = joblib.load(MODEL_FILENAME)

        # 6. Make predictions
        logger.info("="*100)
        logger.info("Generate predictions for test engines")
        y_pred = model.predict(X_test)

        # 7. Calculate evaluation metrics
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # 8. Result log
        logger.info("="*100)
        logger.info("MODEL EVALUATION RESULTS (FD001 Test Set)")
        logger.info(f"Root Mean Squared Error (RMSE): {rmse:.4f} cycles")
        logger.info(f"Mean Absolute Error (MAE): {mae:.4f} cycles")
        logger.info(f"Coefficient Score (R2): {r2:.4f}")
        logger.info("="*100)

        # 9. Show comparison preview
        comparison_df = pd.DataFrame({
             'unit_number': df_eval['unit_number'],
             'true_rul': y_true,
             'predicted_rul': y_pred.round(1),
             'error': (y_pred - y_true).round(1)
        })

        logger.info("Sample prediction comparison (First 5 engine):\n%s", comparison_df.head().to_string())
        logger.info("="*100)


    except Exception as e:
        logger.error(f"Training pipeline failed due to an error: {e}")
            
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed safely.")


if __name__ == '__main__':
     evaluate_model()

    