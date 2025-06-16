import os
import sys
import shutil
import pandas as pd
import re
import csv
from decimal import Decimal, InvalidOperation
import ctypes 
from dotenv import load_dotenv

load_dotenv()
ID = os.getenv('ID')
PROVIDER = os.getenv('PROVIDER')

if getattr(sys, 'frozen', False):
    # Running as a PyInstaller executable
    base_dir = os.path.dirname(sys.executable)
else:
    # Running as a regular .py script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Change to folder with csv files
csv_folder = os.path.join(base_dir, 'CSV_FILES')
output_folder = os.path.join(base_dir, 'PROCESSED')
os.makedirs(output_folder, exist_ok=True)
old_file_folder = os.path.join(base_dir, 'OLD_FILES')
os.makedirs(old_file_folder, exist_ok=True)


# Process each file
def process(df, filename):
    # Normalize headers (remove leading/trailing whitespace)
    df.columns = df.columns.str.strip()
    
    # Find index positions
    try:
        bp_index = df.columns.get_loc("billing_provider")
        bpid_index = df.columns.get_loc("billing_provider_id")
        sec1_index = bpid_index + 1
        sec2_index = bpid_index + 2
        
    except KeyError as e:
        raise Exception(f"Required column not found: {e}")

    rows_to_delete = []

    for index, row in df.iterrows():
        

        billing_provider = row.iloc[bp_index]
        billing_provider_id = row.iloc[bpid_index]

        # Deletes row if LWBS or Unknown Provider
        if billing_provider in ["LWBS", "Unknown Provider"]:
            rows_to_delete.append(index)
            continue
        if billing_provider == PROVIDER and pd.isna(billing_provider_id):
            df.iat[index, bpid_index] = ID

        prev_row = df.iloc[index - 1]

        if pd.isna(billing_provider) and pd.isna(billing_provider_id): 
            # Copy values from previous row
            df.iat[index, bp_index] = prev_row.iloc[bp_index]
            df.iat[index, bpid_index] = prev_row.iloc[bpid_index]

            # Check if secondary provider exists in previous row
            if not pd.isna(prev_row.iloc[sec1_index]) and not pd.isna(prev_row.iloc[sec2_index]):
                df.iat[index, sec1_index] = prev_row.iloc[sec1_index]
                df.iat[index, sec2_index] = prev_row.iloc[sec2_index]

    df.drop(index=rows_to_delete, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


for filename in os.listdir(csv_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(csv_folder, filename)
        try:
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False, na_values=[''])
            processed_df = process(df, filename)

            # Save to output folder
            name, ext = os.path.splitext(filename)

            match = re.search(r'_(\d{8})$', name)
            if not match:
                raise ValueError(f"Could not find date in filename: {filename}")
            date_unformatted = match.group(1)
            date_str = date_unformatted[4:6] + date_unformatted[6:8] + date_unformatted[0:4]

            provider_part = name[:match.start()].lower()

            # Naming the processed files 
            if "larkin" in provider_part:
                provider_clean = "Larkin"
            elif "joseph" in provider_part:
                provider_clean = "Elite St Joe"
            elif "port arthur" in provider_part:
                provider_clean = "Elite Port Arthur"
            else:
                # Fallback to dynamic cleanup if unknown provider
                provider_clean = provider_part
                provider_clean = re.sub(r'charges tester', '', provider_clean, flags=re.IGNORECASE)
                provider_clean = re.sub(r"[^\w\s]", '', provider_clean)
                provider_clean = re.sub(r"\s+", ' ', provider_clean).strip()
                provider_clean = provider_clean.title()

            processed_filename = f"{provider_clean} {date_str}.csv"
            output_path = os.path.join(output_folder, processed_filename)

            processed_df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)

            # Move original file to OLDFILE folder
            moved_path = os.path.join(old_file_folder, filename)
            shutil.move(file_path, moved_path)

        except Exception as e:
            error_message = f"Failed to process {filename}:\n{str(e)}"
            ctypes.windll.user32.MessageBoxW(0, error_message, "Error", 0x10)

    else:
        # Non-CSV file: show warning dialog
        error_message = f"Unsupported file type found: {filename}\n\n* Must be csv files only! *"
        ctypes.windll.user32.MessageBoxW(0, error_message, "Unsupported File", 0x30)