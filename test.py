import gspread

gc = gspread.service_account(filename="gsheet_credentials.json")
sh = gc.open_by_key('1XQyZJEqIxTm3dk7JGJd5Zprkd_XfQJXOFjwTOGtx2B4')
worksheet = sh.sheet1
worksheet.append_row(["a","b","c"])
#res = worksheet.get_all_records()
#print(res)