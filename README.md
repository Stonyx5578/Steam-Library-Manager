# Steam Library Manager

A Python/Flask application that helps you manage your Steam library with ease. It automatically detects installed and uninstalled games, displays cover art, provides Steam Store links, and allows you to install or uninstall games directly from the interface. The app also includes filtering options, a skip‑list system, and the ability to manually add games using a Steam AppID.

> **Note:** This Project was made using AI during development.

---

## Features

- Detects installed and uninstalled Steam games.
- Displays game cover art, hours played, and store links.
- Install or uninstall games directly from the web interface.
- Filter by installed, uninstalled, or all games.
- Skip games and reset the skip list at any time.
- Manually add games by Steam AppID with automatic metadata retrieval.
- Clean, dark‑themed Flask UI.
- First‑run GUI for entering:
  - Steam API Key  
  - SteamID64  
  - Steam library folder  
- Automatically opens your browser when the app starts.

---

## Screenshots

_Add screenshots here to showcase the UI._

---

## Prerequisites

### 1. Python 3.11+  
Verify installation:

```bash
python --version
```

### 2. Required Python Packages

```bash
python -m pip install --upgrade pip
python -m pip install flask requests
```

### 3. Tkinter (Included with Python on Windows)

Test Tkinter:

```bash
python -m tkinter
```

A small window should appear.

### 4. Optional: Build an EXE  
Install PyInstaller:

```bash
python -m pip install pyinstaller
```

---

## Folder Structure

```
Steam Tinder/
├─ app.py
├─ config.py  (auto-generated on first run)
├─ templates/
│  └─ index.html
├─ static/
│  ├─ app.js
│  └─ style.css
```

---

## First Run

1. Start the app:

   ```bash
   python app.py
   ```

   (Or run the compiled EXE.)

2. On first launch, a GUI will prompt you for:
   - **Steam API Key**  
     Get one at: https://steamcommunity.com/dev/apikey  
   - **SteamID64**  
     Look it up at: https://steamid.io/lookup/  
   - **Steam Library Folder**  
     (The folder containing `steamapps`)

3. After saving, the Flask server starts and your browser opens automatically.

---

## Running the App

Once the server is running, you can:

- Browse your Steam games
- Filter by installed/uninstalled/all
- Install or uninstall games
- Add games manually by AppID
- Reset your skipped games list

---

## Building an EXE (Optional)

Standard build:

```bash
python -m PyInstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
```

Hide the terminal window:

```bash
python -m PyInstaller --onefile --windowed --add-data "templates;templates" --add-data "static;static" app.py
```

---

## License

This project is licensed under the **MIT License**.  
You may use, modify, and distribute the code freely.

External libraries (Flask, Requests, PyInstaller, Tkinter) retain their own respective licenses.

---

## Notes

- Your Steam API Key and SteamID64 are stored in `config.py`.  
  **Do not share this file publicly.**
- An internet connection is required for Steam API calls and cover art retrieval.
- This project was made using AI
