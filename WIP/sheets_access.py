# https://pygsheets.readthedocs.io/en/stable/index.html
import pygsheets
from sheets_access_secret import *

def get_sheet():
    # authorize right before it's needed!
    gc = pygsheets.authorize(service_file=CREDENTIALS)

    spreadsheet = gc.open_by_key(SHEET_KEY)
    worksheet1 = spreadsheet.sheet1

    return worksheet1

def get_row_record(row, worksheet=None):
    if worksheet == None:
        worksheet = get_sheet()

    header_arr = worksheet.get_row(1, include_tailing_empty=False)
    row_arr = worksheet.get_row(row, include_tailing_empty=False)

    # in case some question was not answered at the end of the survey
    # and the row was cut off early...
    while len(row_arr) < len(header_arr):
        row_arr.append('N/A')

    record = {}
    for i in range(len(header_arr)):
        key = header_arr[i]
        val = row_arr[i]
        record[key] = val
    record['Row'] = row
    return record

def run_sheets_scrape(zip, city, f_type, site_type_map_to_form_types):
    # old debugging
    # print(gc.spreadsheet_titles())
    # return

    # print("starting: f_type is ", f_type)

    worksheet = get_sheet()

    # https://pygsheets.readthedocs.io/en/stable/worksheet.html
    # return [s for s in worksheet1.get_col(RESPONSE_COLUMN) if s != '']

    # https://pygsheets.readthedocs.io/en/stable/worksheet.html#pygsheets.Worksheet.get_all_records
    # makes sure everything is set to be a string with numericise_data as False
    records = worksheet.get_all_records(numericise_data=False)

    print("acquired all records")

    # print(records)
    if DOUBLE_HEADER:
        records = records[1:]
    # print(records)
    new_records = []

    if DOUBLE_HEADER:
        curr_row = 3
    else:
        curr_row = 2

    for record in records:
        # start by adding row to the record
        record['Row'] = curr_row
        curr_row += 1

        # first, check if there is a City match
        if str(record['City']).lower() != str(city).lower():
            continue

        # check if the site type f_type matches any of the form types
        match = False
        record_types = str(record['Type']).lower()
        for match_type in site_type_map_to_form_types[f_type]:
            if match_type.lower() in record_types:
                match = True
                break

        if match == False:
            continue

        # then, check if there is a ZIP match
        # eventually, do a distance check instead of a equality match
        if str(record['ZIP']).lower() != str(zip).lower():
            new_records.append(record)
        else:
            new_records.insert(0, record)

    print("finished checking all records, # results is:", len(new_records))

    return new_records
