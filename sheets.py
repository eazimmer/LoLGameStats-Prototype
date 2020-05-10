import gspread
from oauth2client.service_account import ServiceAccountCredentials


def sheets_main(matchdata):
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("test1Eric").sheet1
    match = matchdata.get("players")

    # Output match data to spreadsheet
    print_match_data(sheet, match)

    # Call to produce average statistics for all listed players
    create_averages(sheet)


def print_match_data(sheet, match):

    # Output match data to spreadsheet
    for i in match:
        sheet.append_row(list(i.values()), table_range="A2")


def get_all_players(sheet):

    # Pull all data from column and remove duplicates
    players_with_dups = sheet.col_values(1)[1:]
    players_no_dups = list(dict.fromkeys(players_with_dups))

    # Repack into list of lists for submission into columns (required formatting for function call)
    for index in range(len(players_no_dups)):
        players_no_dups[index] = [players_no_dups[index]]
    packaged_players = players_no_dups

    return packaged_players


def average_of_rows(sheet, player_data):

    # Function to calculate the average statistic dictionary to be outputted to spreadsheet
    # Data will come in: {"player" : player, "locations": [row1, row2...]}

    # Final average statistics for this player
    average_stats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    rows_of_data = []

    # Iterate over each row on which data for this player was found
    for row in player_data["locations"]:
        rows_of_data.append(sheet.row_values(row)[4:14])

    # Return single row of data as the average if only one was found
    if len(rows_of_data) == 1:
        rows_of_data[0].insert(0, player_data["player"])
        return rows_of_data[0]

    # Calculate averages if more than one row was found
    else:
        # Iterate over each row of stats
        for row in rows_of_data:
            # Iterate over each item in each row
            for index in range(len(rows_of_data[0])):
                average_stats[index] += float(row[index])

        # Divide sum of each stat by the number of rows of stats (calculate the average)
        for index in range(len(average_stats)):
            average_stats[index] = average_stats[index] / len(rows_of_data)

    # Insert player's name into beginning of the list
    average_stats.insert(0, player_data["player"])

    return average_stats


def create_averages(sheet):

    # Collect packaged players data for updating
    packaged_players = get_all_players(sheet)

    # Acquire parsable players list
    players = readable_players(packaged_players)

    # Create data structure to store averages || list of dictionaries
    rows_for_averaging = []

    # Populate average data structure
    for player in players:

        # Find all rows with this user's name in the match data section
        cells = sheet.findall(player, in_column=1)

        # Data structure to store player and row information
        data = {"player" : player}
        locations = []

        # Grab all row numbers for identified matching rows
        for cell in cells:
            locations.append(cell.row)

        # Update containers
        data["locations"] = locations
        rows_for_averaging.append(data)

    # Final data to be outputted to the spreadsheet
    final_averages = []

    # Calculate average statistics for each player based on their row(s) of data
    for player_data in rows_for_averaging:
        final_averages.append(average_of_rows(sheet, player_data))

    # Output final statistics to the spreadsheet
    sheet.batch_update([{'range' : 'Q2:AA', 'values' : final_averages}])


def readable_players(packaged_players):

    # Helper function to unpack players list into 1D structure
    players = [item for elem in packaged_players for item in elem]
    return players
