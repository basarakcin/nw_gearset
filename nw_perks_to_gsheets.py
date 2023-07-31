import gspread
from google.oauth2.service_account import Credentials

#
# pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
#

def write_to_sheet(username, info):
    # use creds to create a client to interact with the Google Drive API
    scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('path_to_your_service_account_file.json', scopes=scopes)
    client = gspread.authorize(creds)
    
    # Find a workbook by name and open the first sheet
    try:
        sheet = client.open(username).sheet1
    except gspread.SpreadsheetNotFound:
        # if the sheet doesn't exist, create a new one
        sh = client.create(username)  # returns Spreadsheet instance
        sheet = sh.sheet1

    # iterate over items and write data to the sheet
    for image_file_name, item_info in info.items():
        perks = item_info['perks']
        # Append the perks, each in a different cell
        sheet.append_row(perks)
