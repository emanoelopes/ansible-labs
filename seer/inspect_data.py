import pandas as pd

file_path = '/home/emanoel/ansible-labs/seer/dados.xlsx'
try:
    xl = pd.ExcelFile(file_path)
    print("Sheet names:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet, nrows=5)
        print(f"\n--- Sheet: {sheet} ---")
        print(df.columns.tolist())
        print(df.head())
except Exception as e:
    print(f"Error: {e}")
