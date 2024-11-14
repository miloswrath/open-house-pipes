import requests
from datetime import datetime, timedelta
import zipfile
import os
import numpy as np
import pandas as pd
import json
import shutil
import subprocess

# jap_5ThOJ14yf7z1EPEUpAoZYMWoETZcmJk305719

def parse_cmd():
    #parse command line for TEASE var
    import argparse
    parser = argparse.ArgumentParser(description='API File to Pull Subject Data from Jatos')
    parser.add_argument('-t', type=str, help='TEASE')
    parser.add_argument('-a', type=str, help="toke")
    return parser.parse_args()



def get_met(tease):

    

    proxies = {
    'http': f'http:zjgilliam:{tease}@proxy.divms.uiowa.edu:8888',
    'https': f'http://zjgilliam:{tease}@proxy.divms.uiowa.edu:8888',
    }



    url = 'https://jatos.psychology.uiowa.edu/jatos/api/v1/results/metadata'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer jap_5ThOJ14yf7z1EPEUpAoZYMWoETZcmJk305719',
        'Content-Type': 'application/json',
    }
    data = {
        'studyIds': [999]
    }

    response = requests.post(url, headers=headers, json=data, proxies=proxies)

    # If you want to print the response
    print(response.status_code)
    print(response.json())
    response_json = response.json()

    response = response_json

    # Get the current timestamp
    current_time = datetime.now().timestamp() * 1000  # Convert to milliseconds
    one_minute_ago = current_time - (60 * 60 * 24 * 7 * 1000)
    # Initialize an empty list to store study result IDs
    study_result_ids = []

    # Iterate through the data to check conditions and collect study result IDs
    for study in response['data']:
        for study_result in study['studyResults']:
            if study_result['studyState'] == 'FINISHED' and study_result['endDate'] >= one_minute_ago:
                study_result_ids.append(study_result['id'])
                break  # No need to check other component results for this study result

    # Print the list of study result IDs
    print(study_result_ids)

    if len(study_result_ids) == 0:
        print("No study results found.")
        exit()
    
    return study_result_ids

def get_data(study_result_ids, tease):


    

    proxies = {
    'http': f'http://zjgilliam:{tease}@proxy.divms.uiowa.edu:8888',
    'https': f'http://zjgilliam:{tease}@proxy.divms.uiowa.edu:8888',
    }

    headers = {
        'accept': 'application/octet-stream',
        'Authorization': 'Bearer jap_5ThOJ14yf7z1EPEUpAoZYMWoETZcmJk305719',
        'Content-Type': 'application/json',
    }
    # Get the data for each study result
    datas = {
        'studyIds': [999],
        'studyResultIds': study_result_ids
    }

    url = 'https://jatos.psychology.uiowa.edu/jatos/api/v1/results/data'
    response = requests.post(url, headers=headers, json=datas, proxies=proxies)
    # Debugging information
    print(f"Status Code: {response.status_code}")


    # Save the unzip file and save .txt file to the current directory
    if response.status_code == 200:
        jrzip_file = 'response.jrzip'
        with open(jrzip_file, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded file: {jrzip_file}")

        # Verify if the file is a valid zip file
        if zipfile.is_zipfile(jrzip_file):
            print("The file is a valid zip file.")

            # Create a new zip file with only the desired files
            filtered_jrzip_file = 'filtered_response.jrzip'
            with zipfile.ZipFile(jrzip_file, 'r') as zip_ref:
                with zipfile.ZipFile(filtered_jrzip_file, 'w') as filtered_zip_ref:
                    for zip_info in zip_ref.infolist():
                        # Check if the filename contains any of the study_result_ids
                        if any(str(study_result_id) in zip_info.filename for study_result_id in study_result_ids):
                            filtered_zip_ref.writestr(zip_info, zip_ref.read(zip_info.filename))
            print(f"Filtered zip file created: {filtered_jrzip_file}")

            # Extract the filtered zip file
            with zipfile.ZipFile(filtered_jrzip_file, 'r') as zip_ref:
                zip_ref.extractall('./data/raw')
            print(f"Unzipped file: {filtered_jrzip_file}")

            # Optionally, remove the original and filtered zip files after extraction
            os.remove(jrzip_file)
            os.remove(filtered_jrzip_file)

            # Walk through the directory and find all .txt files, save paths to a list
            txt_files = []
            for root, dirs, files in os.walk("./data/raw"):
                for file in files:
                    if file.endswith(".txt"):
                        txt_files.append(os.path.join(root, file))
            print(f"Found {len(txt_files)} .txt files.")
            #move the text file to the data folder

        else:
            print("The file is not a valid zip file.")
    else:
        print("Failed to retrieve or save the file.")
        print(f"Response Text: {response.text}")

    return txt_files

def get_next_run_dir(sub):
    base_dir = f'./data/{sub}/processed'
    i = 1
    while os.path.exists(os.path.join(base_dir, f'run-{i}')):
        i += 1
    return os.path.join(base_dir, f'run-{i}')

def convert_beh():
    txt_files = []
    for root, dirs, files in os.walk('./data/*/raw'):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    print(f"Found text files: {txt_files}")
            
    dic = {}
    for idx, b in enumerate(txt_files, start=1):
        tweets = []
        with open(b, 'r') as file:
            for line in file:
                tweets.append(json.loads(line))
        dic[idx] = pd.json_normalize(tweets, 'data')

    print("Data dictionaries created.")

    all_paths = []
    for i in dic:
        df = dic[i]
        for sub in np.unique(df['subject_id']):
            print(f"Processing subject: {sub}")
            # Filter data for this subject
            sub_df = df[df['subject_id'] == sub]

            # Get next run directory
            run_dir = get_next_run_dir(sub)
            os.makedirs(run_dir, exist_ok=True)

            # Build the CSV file path
            csv_filename = f"{sub}_{sub_df['task'].iloc[0]}_{sub_df['task_vers'].iloc[0]}.csv"
            csv_path = os.path.join(run_dir, csv_filename)

            # Save CSV
            sub_df.to_csv(csv_path, index=False)
            print(f"Saved {csv_path}")

            all_paths.append(csv_path)

    return all_paths

def move_txt(txt_files):
    dic = {}
    for file_path in txt_files:
        tweets = []
        with open(file_path, 'r') as file:
            # Read text file and append each line as a JSON object to tweets
            for line in file:
                tweets.append(json.loads(line))
        dic[file_path] = pd.json_normalize(tweets, 'data')

    for file_path, df in dic.items():
        for sub in np.unique(df['multichar_response']):
            print(sub)
            target_dir = f'./data/{sub}/raw'
            os.makedirs(target_dir, exist_ok=True)
            # Save the DataFrame to a text file in the target directory
            output_file = os.path.join(target_dir, os.path.basename(file_path))
            with open(output_file, 'w') as f:
                f.write(df.to_string(index=False))
            print(f"Saved {output_file} to {target_dir}")
        os.remove(file_path)
        print(f"Removed {file_path}")

    # Move the directory removal outside the loop
    for root, dirs, files in os.walk('./data/raw'):
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    # Optionally, remove the raw directory itself
    os.rmdir('./data/raw')

    return None



def push(toke):
    #use the folder name as task
    task = os.path.basename(os.getcwd())

    subprocess.run(['git', 'config', 'user.email', 'miloswrath@users.noreply.github.com'])
    subprocess.run(['git', 'remote', 'set-url', 'origin', f'https://miloswrath:{toke}@github.com/HBClab/{task}'])
    subprocess.run(['git', 'config', 'user.name', 'miloswrath'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'Automated Commit -> New Data'])
    subprocess.run(['git', 'push', 'origin', 'main'])

def main():
    args = parse_cmd()
    tease = args.t
    toke = args.a
    study_result_ids = get_met(tease)
    get_data(study_result_ids, tease)
    convert_beh()
    txt_files = []
    for root, dirs, files in os.walk('./data/raw'):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    move_txt(txt_files)
    push(toke)





if __name__ == "__main__":
    main()
    
