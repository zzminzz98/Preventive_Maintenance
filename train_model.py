import sqlite3
import pandas as pd
import joblib
from logger_config import setup_logger
from sklearn.ensemble import RandomForestRegressor

logger = setup_logger(__name__)

# Connect and load SQL database
DATABASE_NAME = 'cmapss.db'
TABLE_NAME = 'train_fd001_w_rul'
MODEL_FILENAME = 'random_forest_baseline.pkl'

def train_baseline_model():
    try: 
        # Connect SQL database
        logger.info(f"Connect to database: {DATABASE_NAME}")
        conn = sqlite3.connect(DATABASE_NAME)

        # Select and retrieve dataset from SQL 
        logger.info(f"Loading data from *{TABLE_NAME}*")
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)

        if df.empty:
            logger.warning("The database table is empty! Exiting pipeline.\nPLEASE check ***calculate_rul***.py.")
            return

        logger.info(f"Successfully loaded {len(df):,} rows from {TABLE_NAME}.")


        # 1. Define features X and target y 
        # only op_settings and sensors are considered
        logger.info("="*100)
        drop_cols = ['unit_number','cycle','rul']
        feature_cols = [col for col in df.columns if col not in drop_cols]

        X = df[feature_cols]
        y = df['rul']

        logger.info("Define variables to train model")
        logger.info("Total feature used: %d", len(feature_cols))
        logger.info("Feature columns: %s", feature_cols)
        logger.info("Target column: ['rul']")
        logger.info("Target 'rul' sample preview (first 5 rows):\n%s", y.head().to_string())

        # 2. Train model
        logger.info("="*100)
        logger.info("Training Random Forest Regressor")
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X,y)
        logger.info("Model training completed successfully!")

        # 3. Save model artifact
        logger.info("="*100)
        logger.info(f"Saving model artifact to {MODEL_FILENAME}")
        # Load trained model easily 
        joblib.dump(model, MODEL_FILENAME) 
        logger.info("Model saved successfully!")

    except Exception as e:
        logger.error(f"Training pipeline failed due to an error: {e}")
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed safely.")

    logger.info("="*100)



if __name__ == '__main__':
    train_baseline_model()
