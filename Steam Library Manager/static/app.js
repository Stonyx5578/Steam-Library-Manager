let games = [];
let filteredGames = [];
let currentIndex = 0;
let skippedGames = new Set();

const filterEl = document.getElementById("filter");
const coverImg = document.getElementById("game-cover");
const nameEl = document.getElementById("game-name");
const hoursEl = document.getElementById("game-hours");
const statusEl = document.getElementById("game-status");
const storeEl = document.getElementById("game-store");

const keepBtn = document.getElementById("keep");
const installBtn = document.getElementById("install");
const removeBtn = document.getElementById("remove");
const resetBtn = document.getElementById("reset-options");

const searchInput = document.getElementById("search-appid");
const checkBtn = document.getElementById("check-appid");
const manualForm = document.getElementById("manual-form");
const manualName = document.getElementById("manual-name");
const manualCover = document.getElementById("manual-cover");
const manualStore = document.getElementById("manual-store");
const manualAddBtn = document.getElementById("manual-add-btn");
const manualInstalled = document.getElementById("manual-installed");

// ===== FILTER & DISPLAY =====
function updateFilterOptions() {
    const allCount = games.filter(g => !skippedGames.has(g.appid)).length;
    const installedCount = games.filter(g => g.installed && !skippedGames.has(g.appid)).length;
    const uninstalledCount = games.filter(g => !g.installed && !skippedGames.has(g.appid)).length;

    filterEl.innerHTML = `
        <option value="all">All (${allCount})</option>
        <option value="installed">Installed (${installedCount})</option>
        <option value="uninstalled">Uninstalled (${uninstalledCount})</option>
    `;
}

function applyFilter() {
    const filter = filterEl.value || "all";
    filteredGames = games.filter(g => {
        if (skippedGames.has(g.appid)) return false;
        if (filter === "installed") return g.installed;
        if (filter === "uninstalled") return !g.installed;
        return true;
    });
    currentIndex = 0;
    showGame();
}

function showGame() {
    if (!filteredGames.length) {
        coverImg.src = "";
        nameEl.textContent = "No games to display";
        hoursEl.textContent = "";
        statusEl.textContent = "";
        storeEl.href = "#";
        installBtn.style.display = "none";
        removeBtn.style.display = "none";
        return;
    }
    const game = filteredGames[currentIndex];
    coverImg.src = game.cover;
    coverImg.onerror = () => coverImg.src = `https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/header.jpg`;
    nameEl.textContent = game.name;
    hoursEl.textContent = `Hours Played: ${game.hours || 0}`;
    if (game.installed) {
        statusEl.textContent = "Installed";
        installBtn.style.display = "none";
        removeBtn.style.display = "inline-block";
    } else {
        statusEl.textContent = "Not Installed";
        installBtn.style.display = "inline-block";
        removeBtn.style.display = "none";
    }
    storeEl.href = game.store;
}

// ===== BUTTON ACTIONS =====
function nextGame() {
    if (!filteredGames.length) return;
    skippedGames.add(filteredGames[currentIndex].appid);
    applyFilter();
}

async function performAction(action) {
    if (!filteredGames.length) return;
    const game = filteredGames[currentIndex];
    try {
        await fetch("/action", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({appid: game.appid, action})
        });
        if (action === "install") game.installed = true;
        if (action === "uninstall") game.installed = false;
        skippedGames.add(game.appid);
        applyFilter();
    } catch (err) { console.error(err); }
}

function resetOptions() {
    skippedGames.clear();
    applyFilter();
}

// ===== MANUAL ADD / STEAM ID =====
checkBtn.addEventListener("click", async () => {
    const appid = searchInput.value.trim();
    if (!appid) return alert("Enter a Steam AppID");
    try {
        const res = await fetch(`/fetch_game/${appid}`);
        const data = await res.json();

        if (data.exists) {
            alert(`Game already in library: ${data.game.name}`);
            manualInstalled.checked = data.game.installed; 
            manualName.value = data.game.name;
            manualCover.value = data.game.cover;
            manualStore.value = data.game.store;
            manualForm.style.display = "block";
        } else if (data.success) {
            manualName.value = data.game.name;
            manualCover.value = data.game.cover;
            manualStore.value = data.game.store;
            manualInstalled.checked = false;
            manualForm.style.display = "block";
        } else {
            alert("Could not fetch game info: " + data.error);
            manualForm.style.display = "block";
            manualInstalled.checked = false;
        }
    } catch (err) {
        console.error(err);
        alert("Error fetching game info");
        manualForm.style.display = "block";
        manualInstalled.checked = false;
    }
});

manualAddBtn.addEventListener("click", async () => {
    const appid = parseInt(searchInput.value.trim());
    const name = manualName.value.trim();
    const cover = manualCover.value.trim();
    const store = manualStore.value.trim();
    const installed = manualInstalled.checked;

    if (!appid || !name || !cover || !store) return alert("Fill all fields");

    try {
        const res = await fetch("/add_game", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({appid, name, cover, store, installed})
        });
        const data = await res.json();
        if (data.success) {
            games.push(data.game);
            manualForm.style.display = "none";
            manualInstalled.checked = false;
            applyFilter();
        } else alert("Failed: " + data.error);
    } catch (err) { console.error(err); }
});

// ===== EVENT LISTENERS =====
keepBtn.addEventListener("click", nextGame);
installBtn.addEventListener("click", () => performAction("install"));
removeBtn.addEventListener("click", () => performAction("uninstall"));
filterEl.addEventListener("change", applyFilter);
resetBtn.addEventListener("click", resetOptions);

// ===== INITIALIZE =====
window.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/games");
        games = await res.json();
        updateFilterOptions();
        applyFilter();
    } catch (err) { console.error(err); }
});
