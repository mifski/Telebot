// The bot stamps its own address in here when it sends you the extension ♡
// (left as localhost when you build the zip yourself for local testing)
const DEFAULT_SERVER_URL = "__SERVER_URL__";
let lastVideoId = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "VIDEO_PLAYING") {
    handleVideoUpdate(message.data);
    sendResponse({ received: true });
    return false;
  }
  if (message.type === "SEND_TEST") {
    postVideo({
      title: "♡ hihi! a little test post from your extension ♡",
      url: "https://www.youtube.com/watch?v=jfKfPfyJRdk"
    }, true).then(sendResponse);
    return true; // keep the channel open for the async response
  }
  if (message.type === "CHECK_CONNECTION") {
    callServer("/api/me", {}).then(sendResponse);
    return true;
  }
  if (message.type === "GET_DEFAULT_SERVER") {
    sendResponse({ serverUrl: DEFAULT_SERVER_URL });
    return false;
  }
  return false;
});

// Let the same video be posted again after monitoring is restarted
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.isMonitoring && !changes.isMonitoring.newValue) {
    lastVideoId = null;
  }
});

async function handleVideoUpdate(videoData) {
  // Two YouTube tabs can report the same video
  if (videoData.videoId === lastVideoId) {
    return;
  }
  lastVideoId = videoData.videoId;
  console.log("♪ now carrying:", videoData.title);
  await postVideo(videoData, false);
}

// POST to the bot server with this browser's connection code
async function callServer(path, body) {
  const config = await chrome.storage.local.get(["code", "serverUrl"]);
  if (!config.code) {
    return { success: false, error: "no code yet! send /connect to the bot and paste it here ( ˘ ³˘)♡" };
  }

  const serverUrl = (config.serverUrl || DEFAULT_SERVER_URL).replace(/\/+$/, "");
  try {
    const response = await fetch(`${serverUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: config.code, ...body })
    });
    return await response.json().catch(() => ({
      success: false,
      error: `the bot server answered with HTTP ${response.status} (⌒_⌒;)`
    }));
  } catch (error) {
    const isLocal = /localhost|127\.0\.0\.1/.test(serverUrl);
    return {
      success: false,
      error: isLocal
        ? `can't reach the bot at ${serverUrl} — is "python telebot.py" running? (´•ω•̥\`)`
        : `can't reach the bot at ${serverUrl} — check the URL under Advanced, or the server may be waking up (´•ω•̥\`)`
    };
  }
}

async function postVideo(videoData, isTest) {
  const result = await callServer("/api/send-video", {
    title: videoData.title,
    url: videoData.url,
    test: isTest
  });

  const lastResult = {
    success: Boolean(result.success),
    skipped: Boolean(result.skipped),
    error: result.error || "",
    title: videoData.title,
    time: Date.now()
  };
  await chrome.storage.local.set({ lastResult });

  if (lastResult.success) {
    console.log(lastResult.skipped ? "↩ already shared:" : "♡ sent to Telegram:", videoData.title);
  } else {
    console.error("(>_<) couldn't send:", lastResult.error);
  }
  return lastResult;
}
