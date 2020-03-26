# https://pygsheets.readthedocs.io/en/stable/index.html
import pygsheets
from sheets_access_secret import *

def run_sheets_scrape():
    # print(gc.spreadsheet_titles())
    #
    # return

    # authorize right before it's needed!
    gc = pygsheets.authorize(service_file=CREDENTIALS)

    spreadsheet = gc.open_by_key(SHEET_KEY)
    worksheet1 = spreadsheet.sheet1

    # https://pygsheets.readthedocs.io/en/stable/worksheet.html
    return [s for s in worksheet1.get_col(RESPONSE_COLUMN) if s != '']
