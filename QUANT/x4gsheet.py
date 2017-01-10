import gspread
import x4fns
from x4defs import *
from oauth2client.service_account import ServiceAccountCredentials

def open_worksheet(filename, sheet):
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    gc = gspread.authorize(credentials)
    wks = gc.open(filename).worksheet(sheet)
    return wks

def refresh_catalog():
    wks = open_worksheet('MktDashboard', 'Catalog')
    values = wks.get_all_values()
    x4fns.write_csv(EQCatalog, values, 'w')

def update_ranges(thresholds):
    thresholds_unfurl = [x for f in thresholds for x in f]
    width  = len(thresholds[0])
    length = len(thresholds)
    start_row = 3
    start_col = 'A'
    start_cell = start_col + str(start_row)
    end_row = start_row + length - 1
    end_col = chr(ord(start_col) + width - 1)
    end_cell = end_col + str(end_row)
    cell_range = start_cell+':'+end_cell
    wks = open_worksheet('MktDashboard', 'FAnalysis')
    cell_list = wks.range(cell_range) 
    for i, cell in enumerate(cell_list):
        cell.value = thresholds_unfurl[i]
    wks.update_cells(cell_list)

if __name__ == '__main__':
    x = [list(range(10)) for x in range(5)]
    print (x)
    update_ranges(x)

