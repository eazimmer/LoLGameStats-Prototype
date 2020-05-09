import gspread
from oauth2client.service_account import ServiceAccountCredentials

def printGameToSheet(matchdata):
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("test1Eric").sheet1
    match = matchdata.get("players")
    
    for i in match:
        sheet.append_row(list(i.values()))
      
        
