import pandas as pd

def return_sheets():
    excel_file = r"./data/Datasheet PSE 2026.xlsx"
    sheets = pd.read_excel(excel_file, sheet_name=None)

    for sheet_name, df in sheets.items():
        csv_name = f"./data/{sheet_name}.csv"
        df.to_csv(csv_name, index=False)

return_sheets()