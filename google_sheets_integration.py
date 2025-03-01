import os
import json
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Load environment variables

load_dotenv()  # Load environment variables from .env file

SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SCOPES = os.getenv('SCOPES').split(',')  # Split if multiple scopes

def authenticate_google_sheets():
    """Authenticate and return the Google Sheets service."""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def test_connection(service, spreadsheet_id):
    """Test the connection by retrieving the spreadsheet metadata."""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        print("Connection successful!")
        print("Spreadsheet title:", spreadsheet.get('properties', {}).get('title'))
    except Exception as e:
        print("Failed to connect to Google Sheets API:", e)

def get_sheet_id(service, spreadsheet_id, sheet_name):
    """Get the sheet ID for the specified sheet name."""
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in spreadsheet.get('sheets', []):
        if sheet.get('properties', {}).get('title') == sheet_name:
            return sheet.get('properties', {}).get('sheetId')
    raise ValueError(f"Sheet '{sheet_name}' not found.")

def delete_empty_rows(service, spreadsheet_id, sheet_name):
    """Delete all empty rows in the specified sheet."""
    sheet_id = get_sheet_id(service, spreadsheet_id, sheet_name)

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A:A'  # Check the first column for empty rows
    ).execute()

    values = result.get('values', [])
    rows_to_delete = []

    # Identify empty rows
    for i, row in enumerate(values):
        if not any(row):  # Check if the row is completely empty
            rows_to_delete.append(i + 1)  # Store the 1-based index of the empty row

    # Delete empty rows from bottom to top to avoid index shifting
    for row_index in reversed(rows_to_delete):
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'requests': [{
                    'deleteDimension': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': 'ROWS',
                            'startIndex': row_index - 1,
                            'endIndex': row_index
                        }
                    }
                }]
            }
        ).execute()

def find_first_empty_row(service, spreadsheet_id, column_range):
    """Find the first empty row in the specified column range."""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=column_range
    ).execute()

    values = result.get('values', [])

    # Find the first empty row
    for i, row in enumerate(values):
        if not row or not row[0]:  # Check if the cell is empty
            return i + 1  # Return the row index (1-based)

    return len(values) + 1  # If no empty row found, return the next row

def write_data_to_sheet(service, spreadsheet_id, data):
    """Append data to a Google Sheet starting from the first empty row in column A."""
    # Find the first empty row in column A
    first_empty_row = find_first_empty_row(service, spreadsheet_id, 'TABLEAU DÉPENSES!A:A')

    # Prepare the range for appending data
    append_range = f'TABLEAU DÉPENSES!A{first_empty_row}'

    body = {
        'values': data
    }
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=append_range,
        valueInputOption='RAW',
        body=body
    ).execute()

def map_json_depenses_to_sheet(json_data):
    """Map JSON data extracted from depenses to a format suitable for Google Sheets."""
    mapped_data = []
    for item in json_data:
        row = [
            item.get('id'),
            item.get('supplier_name'),
            item.get('date'),
            item.get('total_amount'),
            item.get('pre_tax_amount'),
            # Add more fields as needed
        ]
        mapped_data.append(row)
    return mapped_data

# Example usage
if __name__ == "__main__":
    service = authenticate_google_sheets()
    spreadsheet_id = '1nrh1EArQCTy-5oEEitKRlhQ8n3Y_fmMptALs-TOD5XI'

    # Test the connection
    test_connection(service, spreadsheet_id)

    # Delete empty rows in the specified range
    delete_empty_rows(service, spreadsheet_id, 'TABLEAU DÉPENSES')

    # Load your JSON data
    with open('axonaut_depenses.json') as f:
        json_data = json.load(f)

    # Map and write data to Google Sheets
    data_to_write = map_json_depenses_to_sheet(json_data)
    write_data_to_sheet(service, spreadsheet_id, data_to_write)
