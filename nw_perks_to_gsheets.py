import gspread
import time
from google.oauth2.service_account import Credentials

def authorize_gspread():
    scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('src/credentials/service_account.json', scopes=scopes)
    client = gspread.authorize(creds)
    return client

def open_spreadsheet(client, spreadsheet_name):
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)
    return spreadsheet

def open_worksheet(spreadsheet, worksheet_name):
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="20")
    return worksheet

def find_build_name_or_empty_row(worksheet, build_name):
    col_values = worksheet.col_values(1)
    try:
        return str(col_values.index(build_name) + 1) # index is 0-based, row number is 1-based
    except ValueError:
        return str(len(col_values) + 1)

def write_build_name(worksheet, build_name, row):
    if row - 1 == len(worksheet.col_values(1)):
        worksheet.update_acell(f'A{row}', build_name)

def write_perks(worksheet, item_info, start_row, is_weapon):
    perks = item_info['perks']
    if is_weapon:
        for i, perk in enumerate(perks, start=1):
            worksheet.update_acell(f"{chr(ord('D') + i - 1)}{start_row}", perk)
    else:
        for i, perk in enumerate(perks):
            worksheet.update_acell(f"{chr(ord('A') + i)}{start_row}", perk)

def write_to_sheet(username, build_name, info):
    client = authorize_gspread()
    spreadsheet = open_spreadsheet(client, 'New World Gears')
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
    worksheet = open_worksheet(spreadsheet, username)

    start_row = find_build_name_or_empty_row(worksheet, build_name)
    write_build_name(worksheet, build_name, int(start_row))

    weapon_row = int(start_row) + 1
    non_weapon_row = int(start_row) + 1
    for item_info in info.values():
        stats = item_info['stats']
        is_weapon = sum(stats.values()) > 26
        if is_weapon:
            write_perks(worksheet, item_info, str(weapon_row), is_weapon)
            weapon_row += 1
        else:
            write_perks(worksheet, item_info, str(non_weapon_row), is_weapon)
            non_weapon_row += 1
    return worksheet
def resize_colums(worksheet):
    worksheet.columns_auto_resize(0, 7)
