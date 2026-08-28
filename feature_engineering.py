import sqlite3
import pandas as pd
from logger_config import setup_logger

logger = setup_logger(__name__)

DATABASE_NAME = 'cmapss.db'
SOURCE_TABLE = 'train_fd001_w_rul'
TARGET_TABLE = 'train_fd001_features'


def add_rolling_feature(window_size=5):
    try:
        # Connect SQL database 
        logger.info(f"Connect to database: {DATABASE_NAME}")
        conn = sqlite3.connect(DATABASE_NAME)

        # Select and retrieve dataset from SQL 
        logger.info(f"Loading data from {SOURCE_TABLE}")
        df = pd.read_sql(f"SELECT * FROM {SOURCE_TABLE}", conn)

        if df.empty:
            logger.warning("The source table is empty. PLEASE check ingestion in ***calculate_rul.py***")
            return

        logger.info(f"Successfully loaded {"SOURCE_TABLE"} ({len(df):,} rows).")

        # 1. Identify sensor columns
        logger.info("="*100) 
        sensor_cols = [col for col in df.columns if 'sensor' in col]

        # 2. Calculate rolling mean and std
        for col in sensor_cols:
            # Rolling mean
            df[f'{col}_roll_mean'] = (
                df.groupby('unit_number')[col].transform(lambda x: x.rolling(
                    window_size, min_periods=1).mean())
            )

            df[f'{col}_roll_std'] = (
                df.groupby('unit_number')[col].transform(lambda x:x.rolling(
                    window_size, min_periods=1).std()).fillna(0)
            )

        logger.info("Rolling mean and std calculation completed. Sample head preview:\n%s", df[
            ['unit_number','cycle','sensor_2','sensor_2_roll_mean','sensor_2_roll_std']].head().to_string())

        logger.info("="*100)
        logger.info(f"Writting intermediate transformed data to *{TARGET_TABLE}*")
        df.to_sql(TARGET_TABLE, conn, if_exists='replace', index=False)

        logger.info(f"New table ({TARGET_TABLE}) stored in SQLite.")
        logger.info("="*100)

    except Exception as e: 
        logger.error(f"An error occured during the rolling feature pipeline execution: {e}")
    
    finally:
        # Ensure database connection always closes safely
        if conn:
            conn.close()
            logger.info("Database connection closed safely.")
        
    logger.info("="*100)


if __name__ == '__main__':
    add_rolling_feature()




    

