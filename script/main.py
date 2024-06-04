import subprocess
import os
import platform
import time
from datetime import datetime

def activate_venv():
    if platform.system() == "Windows":
        activate_venv = os.path.join('.venv', 'Scripts', 'activate')
        python_executable = os.path.join('.venv', 'Scripts', 'python')
    else:
        activate_venv = os.path.join('.venv', 'bin', 'activate')
        python_executable = os.path.join('.venv', 'bin', 'python')

    return python_executable

def run_script(python_executable, script_name):
    try:
        subprocess.run([python_executable, script_name], check=True)
        print(f"Successfully ran {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        return False
    return True

def main():
    # Record the start time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    start_time = time.time()
    
    python_executable = activate_venv()

    # Run web_scraping.py with retry on failure
    while True:
        if run_script(python_executable, 'web_scraping_test.py'):
            break
        print("Retrying web_scraping.py...")
        time.sleep(5)  # Optional: wait for 5 seconds before retrying

    # Run the next scripts
    run_script(python_executable, 'transform_04.py')
    run_script(python_executable, 'transform_16.py')
    
    # Record the end time
    end_time = time.time()

    # Calculate the duration
    duration = (end_time - start_time)/60

    # Convert the existing timestamp to the desired format
    timestamp = datetime.strptime(timestamp, '%Y-%m-%d_%H-%M-%S')
    formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    # Write the log
    with open('log.txt', 'a') as f:
        f.write(f"Scraping on {formatted_timestamp} with duration {duration} minutes.\n")

if __name__ == "__main__":
    main()