import time
import gspread
import os
import csv
from flask import current_app

global_sheet = None
cache = {
    'data': None,
    'timestamp': 0
}
CACHE_DURATION = 30
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
from models.state import DecryptionStatus

SERVICE_ACCOUNT_FILE = None

def get_service_account_file():
    global SERVICE_ACCOUNT_FILE
    if os.path.exists('credentials.json'):
        SERVICE_ACCOUNT_FILE =  'credentials.json'
    elif os.path.exists('gauth-credentials.json'):
        DecryptionStatus.set_decryption_status(True)
        SERVICE_ACCOUNT_FILE = 'gauth-credentials.json'
    else:
        print("Error: No credentials file found")
        exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/spreadsheets'
]

def initialize_google_sheets(sheet_name):
    client = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sheet = client.open(sheet_name).sheet1
    return sheet

def fetch_data_from_sheets():
    global global_sheet
    if global_sheet is None:
        global_sheet = initialize_google_sheets('vehicle-detection') 
    
    rows = global_sheet.get_all_records()  
    return rows

def write_to_csv(data):
    temp_csv_path = os.path.join(current_app.root_path, 'temp', 'data.csv')
    
    os.makedirs(os.path.dirname(temp_csv_path), exist_ok=True)
    
    with open(temp_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    return temp_csv_path  

def clear_google_sheets_data(sheet_name, worksheet_name):
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sheet = gc.open(sheet_name)
    worksheet = sheet.worksheet(worksheet_name)
    worksheet.clear()

def get_cached_data():
    global cache, global_sheet
    current_time = time.time()
    if cache['data'] is None or current_time - cache['timestamp'] > CACHE_DURATION:
        if global_sheet is None:
            global_sheet = initialize_google_sheets('vehicle-detection')
        cache['data'] = global_sheet.get_all_records(head=1)
        cache['timestamp'] = current_time
    return cache['data']