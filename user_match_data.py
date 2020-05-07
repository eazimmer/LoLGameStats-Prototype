# Imports
from riotwatcher import LolWatcher, ApiError
import json

# Global Variables
api_key = "RGAPI-39b4dca4-5490-4e15-a5f7-d7467e921d3f"
watcher = LolWatcher(api_key)
region = "na1"


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
                    print(output) # Output result to console

                    # Output result to a file
                    # with open('out.txt', 'w') as outfile:
                    # json.dump(output, outfile, indent=4)


def main():
    user = input("Please enter a summoner name: ") # Get target summoner's username


    try:
        account_id = watcher.summoner.by_name(region, user)["accountId"]  # Get account_id of target user via their summoner name

    except ApiError as err:
        if err.response.status_code == 404:
            print('Summoner with that name not found.')
    else:
        get_match_data(account_id, user)

main()


