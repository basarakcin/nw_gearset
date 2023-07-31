import gspread
from google.oauth2.service_account import Credentials

#
# pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
#
def write_to_sheet(username, info):
    # use creds to create a client to interact with the Google Drive API
    scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('src/credentials/service_account.json', scopes=scopes)
    client = gspread.authorize(creds)
    
    # Find a workbook by name and open the first sheet
    try:
        spreadsheet = client.open('New World Gears')  # change here
    except gspread.SpreadsheetNotFound:
        # if the sheet doesn't exist, create a new one
        spreadsheet = client.create('New World Gears')  # change here
        spreadsheet.share('akcinbasar@gmail.com', perm_type='user', role='writer')  # share the spreadsheet

    # Print the spreadsheet URL
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")

    # Check if a sheet with the username exists
    try:
        sheet = spreadsheet.worksheet(username)
    except gspread.WorksheetNotFound:
        # If the sheet doesn't exist, create a new one with the username as the title
        sheet = spreadsheet.add_worksheet(title=username, rows="100", cols="20")

    # iterate over items and write data to the sheet
    for image_file_name, item_info in info.items():
        perks = item_info['perks']
        # Append the perks, each in a different cell
        sheet.append_row(perks)

