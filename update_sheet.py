from __future__ import print_function
import pickle
import os.path
import string
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# The name of the spreadsheet if created
SPREADSHEET_DEFAULT_TITLE = 'mal_stats'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Path to Google Spreadsheet resources
GS_PATH = 'GS_resources/'
TOKEN_PATH = GS_PATH + 'token.pickle'
CREDENTIALS_PATH = GS_PATH + 'credentials.json'
SPREADSHEET_ID_PATH = GS_PATH + 'spreadsheet_id'

# Default values for columns and rows
COLUMN_DATE = 'A'
COLUMN_STATS_BEGIN = 'B'
COLUMN_ANIME_NAMES_BEGIN = 'B'
ROW_ANIME_NAMES = 1
ROW_STATS_BEGIN = 2

NUMBER_ROWS_DATE = 2

def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)

def create_spreadsheet(service, sheet_name):
    spreadsheet = {
        'properties': {
            'title': SPREADSHEET_DEFAULT_TITLE
        },
        'sheets': [
            {
                "properties": {
                    'title': sheet_name
                }
            }
        ]
    }

    # Create the spreadsheet
    spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()

    # Create the file containing the id of the spreadsheet for future uses
    with open(SPREADSHEET_ID_PATH, 'w') as file:
        file.write(spreadsheet.get('spreadsheetId'))

def get_spreadsheet_id(service, sheet_name):
    if not os.path.exists(SPREADSHEET_ID_PATH):
        create_spreadsheet(service, sheet_name)
    with open(SPREADSHEET_ID_PATH, 'r') as file:
        # The strip is added in case of the presence of a newline in the file
        id = file.read().strip()
    return id

def create_sheet(service, spreadsheet_id, sheet_name):
    body = {
        "requests": [{
            "addSheet": {
                "properties": {
                    "title": sheet_name
                }
            }
        }]
    }
    result = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

def is_new_season(service, spreadsheet_id, sheet_name):
    result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    is_new = True
    for sheet in result['sheets']:
        if sheet_name == sheet['properties']['title']:
            is_new = False
    return is_new

def num_to_col_letters(num):
    letters = ''
    while num:
        mod = (num - 1) % 26
        letters += chr(mod + 65)
        num = (num - 1) // 26
    return ''.join(reversed(letters))

def col_letters_to_num(col):
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num

def update_anime_names(service, spreadsheet_id, sheet_name, data):
    # Create a list with the anime names from the mal request
    mr_anime_names = [ i[0] for i in data ]
    # Create a list with the anime names from the google sheet
    range = '%s!%s%s:%s' %(sheet_name, COLUMN_ANIME_NAMES_BEGIN, ROW_ANIME_NAMES, ROW_ANIME_NAMES)
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range).execute()
    if result.get('values'):
        gs_anime_names = result.get('values')[0]
    else:
        gs_anime_names = []

    # Sort the anime in the mal request to be the same than in the google sheet
    sorted_data = []
    for anime_name in gs_anime_names:
        # Anime name in mal request and google sheet
        if anime_name in mr_anime_names:
            sorted_data.append(data[mr_anime_names.index(anime_name)])
        # Anime name only in google sheet
        else:
            empty_tuple = ('', '', '', '', data[0][4])
            sorted_data.append(empty_tuple)
    # Anime name only in mal request
    if len(sorted_data) != len(mr_anime_names):
        # To add the new anime names in the google sheet
        new_anime_names = []
        for anime_name in mr_anime_names:
            if anime_name not in gs_anime_names:
                sorted_data.append(data[mr_anime_names.index(anime_name)])
                new_anime_names.append(anime_name)

        # Add the new anime names in the google sheet
        # 2 because we begin at B
        col_begin = num_to_col_letters(len(gs_anime_names)+2)
        col_end = num_to_col_letters(len(gs_anime_names)+1+len(new_anime_names))
        range = '%s!%s%s:%s%s' %(sheet_name, col_begin, ROW_ANIME_NAMES, col_end, ROW_ANIME_NAMES)
        value_input_option = 'RAW'
        body = {
            'values': [
                new_anime_names
            ]
        }
        result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range, valueInputOption=value_input_option, body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))

    # Return the data sorted for the coming update of data
    return sorted_data

def update_anime_stats(service, spreadsheet_id, sheet_name, sorted_data):
    # Get the list of dates already done
    range = '%s!%s%s:%s' %(sheet_name, COLUMN_DATE, ROW_STATS_BEGIN, COLUMN_DATE)
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range).execute()
    dates = result.get('values', [])
    # We flatten the dates list
    flat_dates = [date for sub_dates in dates for date in sub_dates]
    current_date = sorted_data[0][4].split(', ')[1].split(' ')[0]

    # We get the row where the stats must be put
    row_index = 0
    if current_date in flat_dates:
        row_index = NUMBER_ROWS_DATE * (flat_dates.index(current_date) + 1)
    if not row_index:
        row_index = NUMBER_ROWS_DATE * (len(flat_dates) + 1)

    # Update the date in the google sheet
    range = '%s!%s%s:%s%s' %(sheet_name, COLUMN_DATE, row_index, COLUMN_DATE, row_index)
    value_input_option = 'USER_ENTERED'
    body = {
        'values': [
            [current_date]
        ]
    }
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range, valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

    # Merge the date cell with the one below
    result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in result['sheets']:
        if sheet_name == sheet['properties']['title']:
            sheet_id = sheet['properties']['sheetId']
    body = {
        "requests": [
            {
                "mergeCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row_index - 1,
                        "endRowIndex": row_index + 1,
                        "startColumnIndex": col_letters_to_num(COLUMN_DATE) - 1,
                        "endColumnIndex": col_letters_to_num(COLUMN_DATE)
                    },
                    "mergeType": 'MERGE_ALL'
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row_index - 1,
                        "endRowIndex": row_index + 1,
                        "startColumnIndex": col_letters_to_num(COLUMN_DATE) - 1,
                        "endColumnIndex": col_letters_to_num(COLUMN_DATE)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment, verticalAlignment)"
                }
            }
        ]
    }
    result = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    # Update the scores and members
    members = [ i[1] for i in sorted_data ]
    scores = [ i[2] for i in sorted_data ]
    col_end = num_to_col_letters(len(sorted_data)+2)
    range = '%s!%s%s:%s%s' %(sheet_name, COLUMN_STATS_BEGIN, row_index, col_end, row_index + 1)
    value_input_option = 'RAW'
    body = {
        'values': [
            members,
            scores
        ]
    }
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range, valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

def update_sheet(year, season, data):
    service = get_service()
    sheet_name = "%s_%s" %(year, season)
    spreadsheet_id = get_spreadsheet_id(service, sheet_name)
    if is_new_season(service, spreadsheet_id, sheet_name):
        create_sheet(service, spreadsheet_id, sheet_name)

    sorted_data = update_anime_names(service, spreadsheet_id, sheet_name, data)
    update_anime_stats(service, spreadsheet_id, sheet_name, sorted_data)
