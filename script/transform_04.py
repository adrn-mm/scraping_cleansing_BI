# Import libraries
import pandas as pd
import re
from enum import Enum
import os
from datetime import datetime
import warnings
import itertools
import threading
import sys
import time

# Globals:
# Propinsi: str

class ProductType(Enum):
    Giro = "Giro"
    Simpanan = "Simpanan Berjangka"
    Tabungan = "Tabungan"

class ProductAttr(Enum):
    Nominal = "Nominal"
    Jumlah = "Jumlah"

def get_years_months(df: pd.DataFrame, year_row: int, month_row: int):
    VALID_MONTHS = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

    years_months_list = []

    # Extracting the year and month columns
    year_row = df.iloc[year_row]
    year_row_numeric = pd.to_numeric(year_row, errors='coerce')
    year_row_filtered = year_row_numeric.dropna().astype(int).tolist()

    # The first year's column index
    start_x_index = year_row_numeric[year_row_numeric == year_row_filtered[0]].index[0]

    month_row = df.iloc[month_row]
    month_row_filtered = [x for x in month_row.apply(lambda x: x if x in VALID_MONTHS else '' if x in list(map(str, year_row_filtered)) else None).to_list() if x is not None]

    for i in range(len(year_row_filtered)):
        years_months_list.append([year_row_filtered[i], month_row_filtered[i]])

    return years_months_list, start_x_index

def format_data(year: int, month: str, dati_ii: str, details: dict):
    formatted_data = [
        {
            "Tahun": year,
            "Bulan": month if month != year else None,
            "Dati_II": dati_ii,
            ProductType.Giro.value: [
                {
                    ProductAttr.Nominal.value: details[ProductType.Giro][ProductAttr.Nominal],
                    ProductAttr.Jumlah.value: details[ProductType.Giro][ProductAttr.Jumlah]
                }
            ],
            ProductType.Simpanan.value: [
                {
                    ProductAttr.Nominal.value: details[ProductType.Simpanan][ProductAttr.Nominal],
                    ProductAttr.Jumlah.value: details[ProductType.Simpanan][ProductAttr.Jumlah]
                }
            ],
            ProductType.Tabungan.value: [
                {
                    ProductAttr.Nominal.value: details[ProductType.Tabungan][ProductAttr.Nominal],
                    ProductAttr.Jumlah.value: details[ProductType.Tabungan][ProductAttr.Jumlah]
                }
            ],
        }
    ]
    return formatted_data

def get_values(df: pd.DataFrame, ym_list, start_x_index):
    
    ROW_INDEX_INC = 7
    COL_INDEX_INC = 1
    
    data = []

    def get_province(dfp):
        # Define a regular expression pattern to extract the province name
        pattern = r'PROPINSI\s*([\w\s]+)'

        # Search for the pattern in the first column
        for index, value in dfp[0].items():
            match = re.search(pattern, str(value))
            if match:
                # Extract the province name from the matched pattern
                province = match.group(1).strip()
                break
            else:
                continue
        return province

    # Sheet - wide value
    globals()["Propinsi"] = get_province(df)

    # Row 1 = Nominal, Row 2 = Jumlah
    def get_row_index(dfp, product: ProductType, current_row_index):
        row1 = dfp.iloc[current_row_index:current_row_index+7, 2] == product.value
        row1 = row1.astype(int).idxmax()
        row2 = row1 + 1
        return row1, row2

    # Get the index of the first entry
    current_row_index = df.index[df.iloc[:, 0] == "1"].min()

    # Table height
    height = df.shape[0]

    while current_row_index < height:
        dati_ii = df.iloc[current_row_index, 1]
        if pd.isna(dati_ii) or dati_ii == globals()["Propinsi"]:
            current_row_index += ROW_INDEX_INC
            continue

        current_col_index = start_x_index
        for pair in ym_list:
            year = pair[0]
            month = pair[1]
            details = {}
            for product in ProductType:
                row1, row2 = get_row_index(df, product, current_row_index)
                detail = {
                ProductAttr.Nominal: df.iloc[row1, current_col_index],
                ProductAttr.Jumlah: df.iloc[row2, current_col_index]
                }

                details[product] = detail
            

            formatted_data = format_data(year, month, dati_ii, details)

            data.append(formatted_data)

            current_col_index += COL_INDEX_INC  
        current_row_index += ROW_INDEX_INC

    return data

# Function to flatten the JSON structure for multiple years
def flatten_data(data):
    def get_df(inp, record_path):
        df_sub = pd.json_normalize(inp, record_path=[record_path], meta=['Tahun', 'Bulan', 'Dati_II'])
        df_sub['Tipe'] = record_path
        df_sub['Propinsi'] = globals()["Propinsi"]
        return df_sub

    df_all_list = []
    for entry in data:
        df_all_list.extend(get_df(entry, record_path) for record_path in [member.value for member in ProductType])
    
    df_all = pd.concat(df_all_list, ignore_index=True)
    
    return df_all

def Transform04(file_p, excel_file_p):
    # print(f"Transforming: {file_p}")
    # Extract years and months
    tables = pd.read_html(file_p)

    # Only has one table
    df = tables[0]

    # Get the years and months as a list
    year_row = 4
    month_row = 5
    ym_list, start_x_index = get_years_months(df, year_row, month_row)

    # Get the formatted data
    data = get_values(df, ym_list, start_x_index)

    # Flatten the data
    df_all = flatten_data(data)

    # Reorder columns
    df_all = df_all[['Propinsi', 'Dati_II', 'Tahun', 'Bulan', 'Tipe', 'Nominal', 'Jumlah']]

    # Print the DataFrame
    # print(df_all)

    # Save to excel
    df_all.to_csv(excel_file_p, index=False)
    # print(f"Transform Complete. Saved to: {excel_file_p}")

if __name__ == "__main__":
    
    # get the folder with the latest scraped data
    parent_dir = os.path.dirname(os.getcwd())
    scraped_data_dir = os.path.join(parent_dir, 'data')
    dirs = [d for d in os.listdir(scraped_data_dir) if os.path.isdir(os.path.join(scraped_data_dir, d))]
    dirs.sort(key=lambda d: datetime.strptime(re.search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', d).group(), '%Y-%m-%d_%H-%M-%S'))
    latest_dir = dirs[-1]
    # Get all subdirectories in scraped_data_dir
    province_dirs = [d for d in os.listdir(os.path.join(parent_dir, 'data', latest_dir)) if os.path.isdir(os.path.join(parent_dir, 'data', latest_dir, d))]
    
    # Ignore all warnings
    warnings.filterwarnings("ignore")

    # Function to display a spinner with elapsed time
    def spinner(msg, stop_event):
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        start_time = time.time()
        while not stop_event.is_set():
            elapsed_time = time.time() - start_time
            sys.stdout.write('\r' + msg + ' ' + next(spinner) + f' Elapsed time: {elapsed_time:.2f}s')
            sys.stdout.flush()
            time.sleep(0.1)
        elapsed_time = time.time() - start_time
        sys.stdout.write('\r' + msg + ' done! ' + f'Total time: {elapsed_time:.2f}s\n')
    
    # Start spinner
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=("Please wait, start transforming the 04 files...", stop_event))
    spinner_thread.start()
    
    # For each subdirectory, create a corresponding subdirectory in transformed_data_dir
    for province in province_dirs:
        file_path = os.path.join(parent_dir, 'data', latest_dir, province, "./ii04.xls") 
        excel_file_path = os.path.join(parent_dir, 'data', latest_dir, province, "summary_04.csv")
        Transform04(file_path, excel_file_path)
    stop_event.set()
    spinner_thread.join()