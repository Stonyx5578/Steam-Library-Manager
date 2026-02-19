import requests
from config import STEAM_API_KEY, STEAM_ID

def get_owned_games():
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": STEAM_ID,
        "include_appinfo": True,
        "include_played_free_games": True
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    games = {}
    for g in response.json()["response"]["games"]:
        games[g["appid"]] = {
            "name": g["name"],
            "hours": g["playtime_forever"] // 60,
            "last_played": g.get("rtime_last_played", 0)
        }

    return games
