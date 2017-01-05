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

def update_thresholds(thresholds):
    wks = open_worksheet('MktDashboard', 'GFin')
    cell_list = wks.range('C2:D84') 
    for i, cell in enumerate(cell_list):
        cell.value = thresholds[i]
    wks.update_cells(cell_list)

if __name__ == '__main__':

    update_thresholds(range(166))

