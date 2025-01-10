import time
import datetime
import gspread
import os
import csv
import io
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

def write_csv_to_string(data):
    current_time = datetime.datetime.now()
    full_time_string = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    
    # Generate CSV content in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    csv_content = output.getvalue()
    output.close()
    
    return csv_content, f'data_{full_time_string}.csv'

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

class DataStorage:
    # Class-level attribute to store data
    temp_storage = None

    @classmethod
    def store_data_temporarily(cls, data):
        # Store the data temporarily in the class attribute
        cls.temp_storage = data

    @classmethod
    def get_stored_data(cls):
        # Retrieve the temporarily stored data from the class attribute
        return cls.temp_storage
    
    @classmethod
    def clear_stored_data(cls):
        # Clear the temporarily stored data
        cls.temp_storage = None