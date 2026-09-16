const $ = (id) => document.getElementById(id);

// little rotating encouragements ♡
const IDLE_NOTES = [
  "press start and go play something ♪",
  "your channel is waiting (｡•ᴗ•｡)",
  "ready whenever you are ♡"
];

document.addEventListener("DOMContentLoaded", async () => {
  // Load saved config
  const config = await chrome.storage.local.get(["code", "serverUrl", "isMonitoring", "lastResult"]);

  $("code").value = config.code || "";
  $("serverUrl").value = config.serverUrl || "";

  // Show the address the bot baked in, so "empty" never looks broken
  chrome.runtime.sendMessage({ type: "GET_DEFAULT_SERVER" }, (reply) => {
    void chrome.runtime.lastError;
    if (reply && reply.serverUrl) {
      $("serverUrl").placeholder = reply.serverUrl;
    }
  });

  updateStatus(Boolean(config.isMonitoring));
  showResult(config.lastResult);
  if (config.code) {
    checkConnection();
  }

  $("saveConfig").addEventListener("click", async () => {
    if (await saveConfig()) {
      showMessage("saved! ♡", "ok");
      await checkConnection();
    }
  });

  $("testBtn").addEventListener("click", async () => {
    if (!(await saveConfig())) {
      return;
    }
    showMessage("sending a little hello… ♪", "info");
    const result = await chrome.runtime.sendMessage({ type: "SEND_TEST" });
    showResult(result);
  });

  // Start monitoring - content scripts on YouTube tabs react to isMonitoring changing
  $("startBtn").addEventListener("click", async () => {
    if (!(await saveConfig())) {
      return;
    }
    await chrome.storage.local.set({ isMonitoring: true });
    updateStatus(true);
    showMessage("listening! ♬ videos post after 10s of playtime. (tabs opened before this need a refresh)", "ok");
  });

  // Stop monitoring
  $("stopBtn").addEventListener("click", async () => {
    await chrome.storage.local.set({ isMonitoring: false });
    updateStatus(false);
    showMessage("okay, taking a break (-, - )…zzZ", "info");
  });

  // Show posts as they happen while the popup is open
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes.lastResult) {
      showResult(changes.lastResult.newValue);
    }
  });
});

async function saveConfig() {
  const code = $("code").value.trim();
  const serverUrl = $("serverUrl").value.trim();

  if (!code) {
    showMessage("paste your code first! send /connect to the bot ( ˘ ³˘)♡", "error");
    return false;
  }
  if (serverUrl && !/^https?:\/\//.test(serverUrl)) {
    showMessage("the server URL should start with http:// or https:// (･_･;)", "error");
    return false;
  }

  await chrome.storage.local.set({ code, serverUrl });
  // Settings from older versions of the extension
  await chrome.storage.local.remove(["channelId", "userId"]);
  return true;
}

// Ask the server who this code belongs to and where posts go
async function checkConnection() {
  const el = $("connection");
  el.textContent = "peeking… ( ˘ ᵕ ˘ )";
  el.className = "";

  const result = await chrome.runtime.sendMessage({ type: "CHECK_CONNECTION" });
  if (!result.success) {
    el.textContent = `(>_<) ${result.error}`;
    el.className = "warn";
  } else if (!result.channel) {
    el.textContent = "(・・?) connected! but no channel yet — add the bot to your channel as an admin with \"Post Messages\"";
    el.className = "warn";
  } else if (result.paused) {
    el.textContent = `⏸ ${result.channel} is on pause — send /resume to the bot ♡`;
    el.className = "warn";
  } else {
    el.textContent = `♡ posting to ${result.channel} as "${result.format}"`;
    el.className = "ok";
  }
}

function showResult(result) {
  if (!result) {
    return;
  }
  const when = result.time ? ` · ${new Date(result.time).toLocaleTimeString()}` : "";
  if (result.skipped) {
    showMessage(`↩ already shared that one: ${result.title}${when}`, "info");
  } else if (result.success) {
    showMessage(`♡ posted: ${result.title}${when}`, "ok");
  } else {
    showMessage(`(>_<) ${result.error}${when}`, "error");
  }
}

function showMessage(text, kind) {
  const el = $("message");
  el.textContent = text;
  el.className = kind;
  el.hidden = false;
}

function updateStatus(isActive) {
  const statusEl = $("status");
  if (isActive) {
    statusEl.textContent = "♪ listening along with you";
    statusEl.className = "active pulse";
  } else {
    const note = IDLE_NOTES[Math.floor(Math.random() * IDLE_NOTES.length)];
    statusEl.textContent = `⏸ napping — ${note}`;
    statusEl.className = "inactive";
  }
}
