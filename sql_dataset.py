import sqlite3

from logger_config import setup_logger
from data_check import train_test_data, rul_data

logger = setup_logger(__name__)

# Ctrl + / to command

### Path: Not using pandas to dataclean ###
# # create database
# conn = sqlite3.connect("cmapps.db") 
# cursor = conn.cursor()

# # create a unique id for engine 
# cursor.execute("""
# CREATE TABLE engine (
#     unit_number INTEGER PRIMARY KEY
#     dataset_source TEXT
# )
# """)

# cursor.execute("""
# CREATE TABLE reading (
#     reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     unit_number INTEGER,
#     cycle_INTEGER,
#     op_setting_1 REAL,
#     op_setting_2 REAL,
#     op_setting_3 REAL,
#     sensor_1 REAL,
#     sensor_2 REAL,
#     sensor_3 REAL,
#     sensor_4 REAL,
#     sensor_5 REAL,
#     sensor_6 REAL,
#     sensor_7 REAL,
#     sensor_8 REAL,
#     sensor_9 REAL,
#     sensor_10 REAL,
#     sensor_11 REAL,
#     sensor_12 REAL,
#     sensor_13 REAL,
#     sensor_14 REAL,
#     sensor_15 REAL,
#     sensor_16 REAL,
#     sensor_17 REAL,
#     sensor_18 REAL,
#     sensor_19 REAL,
#     sensor_20 REAL,
#     sensor_21 REAL
#
# )

# """)

DATABASE_NAME = 'cmapss.db'

def save_data_to_sqlite():
    # Connects and migrate to SQL
    conn = None

    try:
        logger.info(f"Connect to database: {DATABASE_NAME}")
        conn = sqlite3.connect(DATABASE_NAME)

        logger.info("="*100)
        logger.info("--- Saving Train & Test Dataset to SQLite ---")
        for filename, df in train_test_data.items():
            table_name = filename.replace('.txt', '').lower()
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            logger.info(f"Saved table: {table_name} ({len(df):,} rows)")

        logger.info("="*100)
        logger.info("--- Saving RUL Datasets to SQLite ---")

        for filename, df_rul in rul_data.items():
            table_name = filename.replace('.txt','').lower()
            df_rul.to_sql(table_name, conn , if_exists='replace', index=False)
            logger.info(f"Saved table: {table_name} ({len(df):,} rows)")

        logger.info("="*100)
        logger.info("Database migration complete!")

    except Exception as e: 
        logger.error(f"An error occured during database migration: {e}")
    
    finally:
        # Ensure database connection always closes safely
        if conn:
            conn.close()
            logger.info("Database connection closed safely.")

    logger.info("="*100)



if __name__ == '__main__':
     save_data_to_sqlite()