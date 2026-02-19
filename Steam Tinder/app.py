import os
import requests
from flask import Flask, render_template, jsonify, request
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import importlib
import threading

CONFIG_FILE = "config.py"

# ====== FIRST-RUN CONFIG =====
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        f.write('STEAM_API_KEY = ""\nSTEAM_ID = ""\nSTEAM_LIBRARY_PATHS = []\n')

import config

def write_config(api_key, steam_id, library_path):
    with open(CONFIG_FILE, "w") as f:
        f.write(f'STEAM_API_KEY = "{api_key}"\n')
        f.write(f'STEAM_ID = "{steam_id}"\n')
        f.write(f'STEAM_LIBRARY_PATHS = ["{library_path}"]\n')

# Show GUI only if any config value is empty
if not config.STEAM_API_KEY or not config.STEAM_ID or not config.STEAM_LIBRARY_PATHS:
    root = tk.Tk()
    root.title("Steam Library Manager - First Run")
    root.geometry("450x300")
    root.resizable(False, False)

    tk.Label(root, text="Welcome! Please enter your Steam info", font=("Arial", 14)).pack(pady=10)

    # Steam API Key
    tk.Label(root, text="Steam API Key:").pack()
    api_entry = tk.Entry(root, width=50)
    api_entry.pack(pady=2)
    tk.Label(root, text="Get your API key here:").pack()
    api_link = tk.Label(root, text="https://steamcommunity.com/dev/apikey", fg="blue", cursor="hand2")
    api_link.pack()
    api_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://steamcommunity.com/dev/apikey"))

    # SteamID64
    tk.Label(root, text="SteamID64 (numeric Steam ID):").pack(pady=(10,0))
    id_entry = tk.Entry(root, width=50)
    id_entry.pack(pady=2)
    tk.Label(root, text="Find your SteamID64 here:").pack()
    id_link = tk.Label(root, text="https://steamid.io/lookup/", fg="blue", cursor="hand2")
    id_link.pack()
    id_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://steamid.io/lookup/"))

    # Steam Library Folder
    tk.Label(root, text="Steam Library Folder (steamapps):").pack(pady=(10,0))
    folder_path = tk.StringVar()
    folder_entry = tk.Entry(root, textvariable=folder_path, width=50)
    folder_entry.pack(pady=2)
    tk.Button(root, text="Browse...", command=lambda: folder_path.set(filedialog.askdirectory(title="Select Steam Library Folder"))).pack()

    def save_and_close():
        api_key = api_entry.get().strip()
        steam_id = id_entry.get().strip()
        library = folder_path.get().strip()
        if not api_key or not steam_id or not library:
            messagebox.showerror("Error", "All fields are required!")
            return
        write_config(api_key, steam_id, library)
        importlib.reload(config)
        messagebox.showinfo("Saved", "Configuration saved! The app will now start.")
        root.destroy()  # close GUI

    tk.Button(root, text="Save & Start", command=save_and_close, bg="#ff6600", fg="#fff").pack(pady=15)
    root.mainloop()

# ===== LOAD CONFIG =====
STEAM_API_KEY = config.STEAM_API_KEY
STEAM_ID = config.STEAM_ID
STEAM_LIBRARY_PATHS = config.STEAM_LIBRARY_PATHS

# ===== FLASK APP =====
app = Flask(__name__)
manual_games = []

# ===== HELPER FUNCTIONS =====
def get_owned_games():
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={STEAM_API_KEY}&steamid={STEAM_ID}&include_appinfo=1&include_played_free_games=1&format=json"
    )
    try:
        response = requests.get(url)
        data = response.json()
    except:
        return []
    games = []
    for g in data["response"].get("games", []):
        games.append({
            "appid": g["appid"],
            "name": g.get("name", "Unknown"),
            "hours": round(g.get("playtime_forever", 0)/60, 1),
            "installed": False,
            "cover": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{g['appid']}/header.jpg",
            "store": f"https://store.steampowered.com/app/{g['appid']}"
        })
    return games

def check_installed_games(games):
    installed_appids = set()
    for path in STEAM_LIBRARY_PATHS:
        if not os.path.exists(path):
            continue
        for f in os.listdir(path):
            if f.startswith("appmanifest") and f.endswith(".acf"):
                try:
                    with open(os.path.join(path, f), "r", encoding="utf-8") as file:
                        for line in file:
                            if '"appid"' in line:
                                appid = int(line.split()[1].strip('"'))
                                installed_appids.add(appid)
                except:
                    continue
    for game in games:
        if game["appid"] in installed_appids:
            game["installed"] = True
    return games

# ===== ROUTES =====
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/games")
def get_games():
    games = get_owned_games()
    games = check_installed_games(games)
    return jsonify(games + manual_games)

@app.route("/action", methods=["POST"])
def action():
    data = request.json
    appid = data.get("appid")
    action_type = data.get("action")
    try:
        if action_type == "install":
            os.startfile(f"steam://install/{appid}")
        elif action_type == "uninstall":
            os.startfile(f"steam://uninstall/{appid}")
    except Exception as e:
        print(f"Failed to {action_type} {appid}: {e}")

    # Update manual games if present
    for game in manual_games:
        if game["appid"] == appid:
            game["installed"] = action_type == "install"
    return jsonify({"success": True, "appid": appid, "action": action_type})

@app.route("/fetch_game/<int:appid>")
def fetch_game(appid):
    games = get_owned_games()
    games = check_installed_games(games)
    all_games = games + manual_games
    for g in all_games:
        if g["appid"] == appid:
            return jsonify({"exists": True, "game": g})
    try:
        res = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en", timeout=5).json()
        if not res[str(appid)]["success"]:
            return jsonify({"success": False, "error": "Game not found"}), 404
        data = res[str(appid)]["data"]
        game = {
            "appid": appid,
            "name": data.get("name", f"AppID {appid}"),
            "hours": 0,
            "installed": False,
            "cover": data.get("header_image", f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"),
            "store": f"https://store.steampowered.com/app/{appid}"
        }
        return jsonify({"success": True, "game": game})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/add_game", methods=["POST"])
def add_game():
    data = request.json
    required_keys = ["appid", "name", "cover", "store", "installed"]
    if not all(k in data for k in required_keys):
        return jsonify({"success": False, "error": "Missing keys"}), 400
    game = {
        "appid": data["appid"],
        "name": data["name"],
        "hours": data.get("hours", 0),
        "installed": data.get("installed", False),
        "cover": data["cover"],
        "store": data["store"]
    }
    manual_games.append(game)
    return jsonify({"success": True, "game": game})

# ===== RUN FLASK =====
if __name__ == "__main__":
    # Open browser automatically
    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")

    threading.Timer(1.0, open_browser).start()  # wait 1 sec for server to start
    app.run(debug=True)
