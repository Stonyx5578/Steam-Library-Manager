import os

def parse_acf(path):
    data = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if '"' in line:
                p = line.strip().split('"')
                if len(p) >= 4:
                    data[p[1]] = p[3]
    return data

def get_installed_games(steam_path):
    steamapps = os.path.join(steam_path, "steamapps")
    installed = set()

    if not os.path.exists(steamapps):
        return installed

    for f in os.listdir(steamapps):
        if f.startswith("appmanifest_"):
            data = parse_acf(os.path.join(steamapps, f))
            installed.add(int(data["appid"]))

    return installed
