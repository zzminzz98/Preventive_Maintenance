# Calculate RUL from SQL database 
import sqlite3
import pandas as pd 
from logger_config import setup_logger

logger = setup_logger(__name__)

DATABASE_NAME = 'cmapss.db'
SOURCE_TABLE = 'train_fd001'
TARGET_TABLE = 'train_fd001_w_rul'

def calculate_rul_pipeline():
    try:
        # 1.Connect SQL database
        logger.info(f"Connect to database: {DATABASE_NAME}")
        conn = sqlite3.connect(DATABASE_NAME)

        # 2.Select and retrieve dataset from SQL
        # * select all columns 
        logger.info(f"Loading data from *{SOURCE_TABLE}*")
        df = pd.read_sql(f"SELECT * FROM {SOURCE_TABLE}",conn)

        if df.empty:
            logger.warning("The source table is empty. Please check ingestion in ***sql_dataset.py***.")
            return

        logger.info(f"Successfully loaded {len(df):,} rows.")

        # 3.Calculate RUL 
        logger.info("="*100)
        logger.info(f"Calculating RUL")

        # Find max cycle for each engine unit
        # reset_index prevent unit_number to be row index 
        max_cycles = df.groupby("unit_number")['cycle'].max().reset_index()
        max_cycles.rename(columns={'cycle': 'max_cycle'}, inplace=True)

        # Merge max cycle into main dataframe
        df = pd.merge(df, max_cycles, on='unit_number', how='left')

        # Calculate rul: Max cycle - Current cycle
        df['rul'] = df['max_cycle'] - df['cycle']

        # Drop max_cycle column to keep schema clean
        df.drop(columns=['max_cycle'], inplace=True)

        # .to_string() for pandas DataFrames
        logger.info("RUL calculation complete. Sample head preview:\n%s", df[['unit_number','cycle','rul']].head().to_string())

        # Write new processed table
        logger.info("="*100)
        logger.info(f"Writing transformed data to *{TARGET_TABLE}*")
        df.to_sql(TARGET_TABLE, conn, if_exists='replace', index=False)

        logger.info("Pipeline completed successfully! New table stored in SQLite.")
        logger.info("="*100)

    except Exception as e: 
        logger.error(f"An error occured during the RUL pipeline execution: {e}")

    finally:
        # Ensure database connection always closes safely
        if conn:
            conn.close()
            logger.info("Database connection closed safely.")
    
    logger.info("="*100)



if __name__ == '__main__':
    calculate_rul_pipeline()

