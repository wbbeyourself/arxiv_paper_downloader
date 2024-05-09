import os
import re
import json
import string
import requests
import pandas as pd


# list the dir names of root_dir, sort by time descending
def list_dir(root_dir):
    if not os.path.exists(root_dir):
        return []
    return sorted(os.listdir(root_dir), key=lambda x: os.path.getmtime(os.path.join(root_dir, x)), reverse=True)


# read txt file
def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# read txt file, return line list and remove empty line
def load_txt_lines(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() != ""]


# load json file
def load_json(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# load json line file
def load_jsonl(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = f.readlines()
    return [json.loads(line.strip()) for line in data if line.strip() != '']


# read excel file, optional sheet name
def load_excel(excel_path, sheet_name=None):
    if sheet_name is None:
        return pd.read_excel(excel_path)
    else:
        return pd.read_excel(excel_path, sheet_name=sheet_name)


# read excel file, optional sheet name, return json list
def load_excel_to_json(excel_path, sheet_name=None):
    if sheet_name is None:
        df = pd.read_excel(excel_path, engine='openpyxl')
    else:
        df = pd.read_excel(
            excel_path, sheet_name=sheet_name, engine='openpyxl')
    return df.to_dict('records')


# pandas read csv to json list
def load_csv_to_json(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8')
    return df.to_dict('records')


# save txt file
def save_txt_file(path: str, data: str):
    # is dir not exists, create dir
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    print(f"txt file {path} saved successfully")


# save json list to json file
def save_json_file(path: str, data: list):
    print('len(data): ', len(data))
    # is dir not exists, create dir
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Json file {path} saved successfully")


# save json list to json line file
def save_jsonl_file(path: str, data: list):
    print('len(data): ', len(data))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for js in data:
            f.write(json.dumps(js, ensure_ascii=False) + '\n')
        print(f"save jsonl file to {path}")


# get all files and subdirs files of given dir
def get_all_files(dir_path: str, suffix=None) -> list:
    all_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            abs_path = os.path.join(root, file)
            abs_path = abs_path.replace("\\", "/")
            if suffix is not None:
                if file.endswith(suffix):
                    all_files.append(abs_path)
            else:
                all_files.append(abs_path)
    return all_files


# 添加前导0
def add_leading_zeros(num):
    return str(num).zfill(3)


# json list to excel
def json_list_to_excel(json_list, excel_path):
    df = pd.DataFrame(json_list)
    df.to_excel(excel_path, index=False)
    print(f"Excel file {excel_path} saved successfully")
