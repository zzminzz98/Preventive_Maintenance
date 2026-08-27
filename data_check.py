import os
import pandas as pd
import pandas.api.types as ptypes
from logger_config import setup_logger

logger = setup_logger(__name__)

# Define CMAPSS column names 
col_names = ['unit_number', 'cycle'] + [f'op_setting_{i}' for i in range(1,4)] + [
    f'sensor_{i}' for i in range (1,22)]

DATA_DIR = 'CMAPSSData'

# Validation check function (train/test)
def validate_train_test(filepath):  
    df = pd.read_csv(filepath, sep=r'\s+', header=None, names=col_names)

    # Standardize all columns to lowercase
    df.columns = df.columns.str.lower()

    # Check: dataframe shape
    assert df.shape[1] == len(col_names), f'{filepath}: wrong column count, got {df.shape[1]}'

    # Check: missing data
    assert df.isnull().sum().sum()==0, f'{filepath}: found {df.isnull().sum().sum()} nulls'

    # Check: data format 
    int_cols = ['unit_number', 'cycle']
    numeric_cols = [f'op_setting_{i}' for i in range(1,4)] + [f'sensor_{i}' for i in range(1,22)]

    for col in int_cols:
        assert ptypes.is_integer_dtype(df[col]), f'{filepath}: {col} is not an integer'

    for col in numeric_cols:
        assert ptypes.is_numeric_dtype(df[col]), f'{filepath}: {col} is not a float'

    return df


# Validation check function (rul)
def validation_rul(filepath):
    df_rul = pd.read_csv(filepath, sep=r'\s+', header=None, names=['remaining_cycles'])

    # Standardize column to lowercase
    df_rul.columns = df_rul.columns.str.lower()

    # Check: dataframe shape
    assert df_rul.shape[1] == 1, f'{filepath}: wrong column count, got {df_rul.shape[1]}'

    # Check: missing data
    assert df_rul.isnull().sum().sum() == 0, f'{filepath}: found {df_rul.isnull().sum().sum()} nulls'

    # Check format
    assert ptypes.is_numeric_dtype(df_rul['remaining_cycles']), f'{filepath}: RUL is not numeric'

    # Include unit_number in rul
    df_rul['unit_number'] = df_rul.index + 1

    # Reorder columns 
    df_rul = df_rul[['unit_number', 'remaining_cycles']]

    return df_rul


# Dictionaries to store validated dataframes for later use
train_test_data = {}
rul_data = {}

# Loop through all files (train/test)
prefixes = ['train', 'test']
dataset_id = ['FD001', 'FD002', 'FD003', 'FD004']


for prefix in prefixes:
    for ds_id in dataset_id:
        filename = f'{prefix}_{ds_id}.txt'
        filepath= os.path.join(DATA_DIR, filename)

        if os.path.exists(filepath):
            logger.info(f'Validating and loading: {filename}')

            # Store dataframe in dict
            train_test_data[filename] = validate_train_test(filepath)

        else: 
            logger.warning(f'Skipping {filename} (File not found)')


for ds_id in dataset_id:
    filename = f'RUL_{ds_id}.txt'
    filepath = os.path.join(DATA_DIR, filename)

    if os.path.exists(filepath):
        logger.info(f'Validating and loading: {filename}')

        # Store RUL in dict
        rul_data[filename] = validation_rul(filepath)

    else:
        logger.warning(f'Skipping {filename} (File not found)')

logger.info("Scan is complete! All dataset successfully validated and loaded.")
logger.info("="*100)

# Number of files stored in dictionaries
logger.info(f"Total train/test files loaded: {len(train_test_data)}")
logger.info(f"Total RUL files loaded: {len(rul_data)}")
logger.info("="*100)

# Print Summary: All Loaded Dataframes
#.items(key,values), .key(), .values() 
logger.info("--- Train & Test Dataset Summary ---")
for filename, df in train_test_data.items():
    rows, cols = df.shape
    logger.info(f"{filename} -> Rows: {rows:,}, Columns: {cols}")  # {rows:,} --> commas format

logger.info("="*100)
logger.info("--- RUL Dataset Summary ---")
for filename, df_rul in rul_data.items():
    rows, cols = df_rul.shape
    logger.info(f"{filename} -> Rows: {rows:,}, Columns: {cols}")
logger.info("="*100)

# Make terminal interactable 
# python -i data_check.py
# train_test_data['train_FD001.txt'].head()
# exit >>> exit() /// Ctrl + D