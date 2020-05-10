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

    # Call to produce average statistics for all listed players
    create_averages(sheet)


def get_all_players(sheet):

    # Pull all data from column and remove duplicates
    players_with_dups = sheet.col_values(1)[1:]
    players_no_dups = list(dict.fromkeys(players_with_dups))

    # Repack into list of lists for submission into columns (required formatting for function call)
    for index in range(len(players_no_dups)):
        players_no_dups[index] = [players_no_dups[index]]
    packaged_players = players_no_dups

    return packaged_players


def create_averages(sheet):

    # Work in Progress
    sheet.update("Q2:Q", get_all_players(sheet))


def print_all_players(packaged_players):

    # Helper function for developer to view players easily
    players = [item for elem in packaged_players for item in elem]
    print(players)


