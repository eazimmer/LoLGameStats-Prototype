# Imports
from riotwatcher import LolWatcher, ApiError

# Global Variables
api_key = "RGAPI-39b4dca4-5490-4e15-a5f7-d7467e921d3f"
watcher = LolWatcher(api_key)
region = "na1"


# Collect champion_id
champion_id = input("Please enter a champion id: ")


# Acquire match data
version = watcher.data_dragon.versions_for_region(region)["v"]
champlist = watcher.data_dragon.champions(version)["data"]
champions = champlist.keys()


# Identify the right champion and print its name
for champ in champions:
    if champlist[champ]["key"] == champion_id:
        print(champ)
