import os
from data_transformation.transform_04 import Transform04
from data_transformation.transform_16 import Transform16

# Progress bar
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def AutoScrape(data_directory: str):
    """
    :param data_directory: str Path to the directory containing the scraped data
    """
    excel_data_dir = "./summaries"

    print("Scraping data from directory:", data_directory)

    total_files = len(os.listdir(data_directory))
    i = 0

    # Loop through the files in the data directory and process them
    printProgressBar(0, total_files, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for file in os.listdir(data_directory):
        if file.endswith(".xls"):
            file_path = os.path.join(data_directory, file)
            
            # Extract the name of the scraped data file
            data_file_name = os.path.basename(data_directory)
            print(data_file_name)
            
            # Create summary directory if it doesnt exist
            summary_directory = os.path.join(excel_data_dir, data_file_name)
            if not os.path.exists(summary_directory):
                os.makedirs(summary_directory)
                print("Created summary directory:", summary_directory)

            # Construct the path for the summary Excel file, exclude "xls"
            summary_file_name = f"summary_{file[:-3] + 'xlsx'}"
            summary_file_path = os.path.join(excel_data_dir, data_file_name, summary_file_name)
            
            print("Processing file:", file_path)
            print("Summary file path:", summary_file_path)
            
            # Call your Transform04 function here with the appropriate file paths
            if "_ii04" in file:
                Transform04(file_path, summary_file_path)
            elif "_ii16" in file:
                Transform16(file_path, summary_file_path)
            printProgressBar(i+1, total_files, prefix = 'Progress:', suffix = 'Complete', length = 50)
            i += 1

AutoScrape("./web_scraping/scraped_data/scraped_data_2024-05-24_15-23-07")
