# SFTP Automation

This Python script automates the cleaning and formatting of provider charge CSV files. It applies validation rules, fills missing values, standardizes provider naming, and saves clean, renamed outputs, ready for reporting or further ETL processing.

## What It Does

- Processes all `.csv` files from the `CSV_FILES` folder
- Cleans data by:
  - Filling missing provider info from previous rows
  - Injecting provider IDs based on environment variables
  - Dropping rows marked as "LWBS" or "Unknown Provider"
- Parses filenames to extract dates and normalize provider names
- Writes cleaned `.csv` files to a `PROCESSED` folder with consistent naming
- Archives originals into an `OLD_FILES` folder after processing

## Key Features

- Customizable logic for different provider formats (e.g. "Larkin", "St Joe")
- Environment-aware using `.env` for injecting IDs (`PROVIDER`, `ID`)
- Handles both PyInstaller executables and regular Python scripts
- Automatically renames output files using a `Provider MMDDYYYY.csv` format
- Error handling with Windows message dialogs for failed or unsupported files

## Tech Highlights

- Python 3.x
- `pandas`, `csv`, `re`, `shutil`, `ctypes`
- `.env` config via `python-dotenv`
- Designed for internal Windows use with minimal setup

---

## ⚠️ Note
- Internal Use Only!
- This tool is intended solely for authorized staff at Blitz Medical Billing. 
- Do **not** distribute or use this application outside approved environments.

## 🔐 Security & Compliance

This application is designed to process healthcare data (e.g., names, MRNs, dates of service), but no PHI is committed to or stored in this repository.

- No patient data is hardcoded or bundled.
- All uploads happen locally on the user's machine.
- Temporary and output files are not uploaded or retained externally.
- Users are responsible for ensuring HIPAA compliance when operating this tool in a production environment.

This repository contains logic only and is safe for internal, private use.