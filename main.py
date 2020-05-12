# Imports
from riotwatcher import LolWatcher, ApiError
import json
import sheets

# Global Variables
api_key = "RGAPI-3ace2577-8184-460e-8171-7f4f4b113003"
watcher = LolWatcher(api_key)
region = "na1"


def get_stats(match_data, player_data, champlist):
    # Tracked information:

    # Player
        # Team (100, 200) || ["teamId"] -> 100 == Blue, 200 == Red
        # Win or Loss || ["stats"]["win"] -> true or false
        # Champion || ["championId"]
        # Kills || ["stats"]["kills"]
        # Deaths || ["stats"]["deaths"]
        # Assists || ["stats"]["assists"]
        # KDA || ((Kills + Assists) / Deaths)
        # Creep Score || (["stats"]["totalMinionsKilled"] + ["stats"]["neutralMinionsKilled"])
        # Creep Score per minute (Creep Score / Game length in minutes) || (Creep Score / int(fullmatchdata["gameDuration"] / 60))
        # Gold || ["stats"]["goldEarned"]
        # Gold per minute (Gold / Game length in minutes) || (Gold / int(fullmatchdata["gameDuration"] / 60))
        # Kill Participation || ((Kills + Assists) / Sum Team Kills)
        # Team Gold Percentage || (Gold / Sum Team Gold)

    # Convert JSON string back into JSON object
    match_data, player_data = json.loads(match_data), json.loads(player_data)

    # Data to be referenced
    statistics = {"players" : []} # Store all game statistics
    name_to_participant_id = {} # Mapping of player names to participant ids
    participant_id_to_name = {} # Mapping of participant ids to player names

    # Team-wide sum values to be used for calculations later
    blue_team_kills = 0
    blue_team_gold = 0
    red_team_kills = 0
    red_team_gold = 0

    # Enter the name each player into the data set
    for player in match_data["participantIdentities"]:
        statistics["players"].append({"player" : player["player"]["summonerName"]})
        name_to_participant_id[player["player"]["summonerName"]] = player["participantId"] # Map player name to participant id
        participant_id_to_name[str(player["participantId"])] = player["player"]["summonerName"] # Map participant ids to player names

    # Cycle through each player entering their respective data
    for participant in range(len(match_data["participants"])):

        # Team Color
        if match_data["participants"][participant]["teamId"] == 100:
            statistics["players"][participant]["side"] = "blue"
        elif match_data["participants"][participant]["teamId"] == 200:
            statistics["players"][participant]["side"] = "red"

        # Win or Loss
        if match_data["participants"][participant]["stats"]["win"] == True:
            statistics["players"][participant]["win"] = True
        elif match_data["participants"][participant]["stats"]["win"] == False:
            statistics["players"][participant]["win"] = False

        # Champion
        statistics["players"][participant]["champion"] = get_champ_from_id(champlist, match_data["participants"][participant]["championId"])

        # Combat Stats
        statistics["players"][participant]["kills"] = match_data["participants"][participant]["stats"]["kills"]

        # Increment team kill counts based on which team the player represents
        if statistics["players"][participant]["side"] == "blue":
            blue_team_kills += match_data["participants"][participant]["stats"]["kills"]
        else:
            red_team_kills += match_data["participants"][participant]["stats"]["kills"]

        statistics["players"][participant]["deaths"] = match_data["participants"][participant]["stats"]["deaths"]
        statistics["players"][participant]["assists"] = match_data["participants"][participant]["stats"]["assists"]

        # KDA = (Kills + Assists) / Deaths
        statistics["players"][participant]["kda"] = round((statistics["players"][participant]["kills"] + statistics["players"][participant]["assists"]) / statistics["players"][participant]["deaths"], 2)

        # Farming Statistics
        statistics["players"][participant]["creepscore"] = (match_data["participants"][participant]["stats"]["totalMinionsKilled"] + match_data["participants"][participant]["stats"]["neutralMinionsKilled"])
        statistics["players"][participant]["creepspermin"] = round(statistics["players"][participant]["creepscore"] / int(match_data["gameDuration"] / 60), 1)

        # Gold Statistics
        statistics["players"][participant]["gold"] = match_data["participants"][participant]["stats"]["goldEarned"]

        # Increment team gold counts based on which team the player represents
        if statistics["players"][participant]["side"] == "blue":
            blue_team_gold += match_data["participants"][participant]["stats"]["goldEarned"]
        else:
            red_team_gold += match_data["participants"][participant]["stats"]["goldEarned"]

        statistics["players"][participant]["goldpermin"] = round(statistics["players"][participant]["gold"] / int(match_data["gameDuration"] / 60), 1)

    # Cycle back through to append team-wide data
    for participant in range(len(match_data["participants"])):

        # Kill Participation based on team || (Kills + Assists) / Team Kills
        if statistics["players"][participant]["side"] == "blue":
            statistics["players"][participant]["killparticipationpercent"] = round((statistics["players"][participant]["kills"] + statistics["players"][participant]["assists"]) / blue_team_kills, 2)
        else:
            statistics["players"][participant]["killparticipationpercent"] = round((statistics["players"][participant]["kills"] + statistics["players"][participant]["assists"]) / red_team_kills, 2)

        # Team Gold Percentage based on team || Gold / Team Gold
        if statistics["players"][participant]["side"] == "blue":
            statistics["players"][participant]["teamgoldpercent"] = round(statistics["players"][participant]["gold"] / blue_team_gold, 2)
        else:
            statistics["players"][participant]["teamgoldpercent"] = round(statistics["players"][participant]["gold"] / red_team_gold, 2)

    return statistics


def get_match_data(account_id, user):

    # Acquire match data
    matchlist = watcher.match.matchlist_by_account(region, account_id) # Get their match history via account_id
    match_id = matchlist["matches"][0]["gameId"] # Grab this user's most recent match_id
    match_data = watcher.match.by_id(region, match_id) # Get match data from this match

    # Filter down data from returned JSON file, towards search of a specific player
    participants = match_data["participants"]
    participantIDs = match_data["participantIdentities"]

    # Get individual user data for a match
    for participant in participantIDs:  # Find Logic's participant ID
        if participant["player"]["summonerName"] == user:
            pid = int(participant["participantId"])
            for participant in participants:    # Select Logic's data
                if participant["participantId"] == pid:
                    output = json.dumps(participant, indent=4)
                    return json.dumps(match_data), json.dumps(output)


def get_champ_from_id(champlist, id):

    # Acquire champion data
    champions = champlist.keys()

    # Identify the right champion and print its name
    for champ in champions:
        if champlist[champ]["key"] == str(id):
            return champ


def main():
    user = input("Please enter a (CASE SENSITIVE) summoner name: ") # Get target summoner's username

    try:
        account = watcher.summoner.by_name(region, user)  # Get account_id of target user via their summoner name
    except ApiError as err:
        if err.response.status_code == 404:
            print('Summoner with that name not found.')
    else:
        print("Exporting data, please wait:")
        account_id = account["accountId"]
        user = account["name"]
        match_data, player_data = get_match_data(account_id, user) # Get match data
        version = watcher.data_dragon.versions_for_region(region)["v"]  # Get game version
        champlist = watcher.data_dragon.champions(version)["data"]  # Get champion data

        statistics = get_stats(match_data, player_data, champlist) # Produce statistics from the game

        # Call sheets API to output data
        sheets.sheets_main(statistics)
        print("Process complete.")


main()
