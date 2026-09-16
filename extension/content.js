console.log("♡ YouTube to Telegram: listening for your music ♪(´ε｀ )");

const CHECK_EVERY_MS = 2000;
// Only post videos you actually watch, not ones you click past
const MIN_PLAY_SECONDS = 10;
// How long to wait for YouTube to show the new title after switching videos
const TITLE_WAIT_MS = 10000;

let checkInterval = null;
let lastVideoId = null;     // last video we reported
let lastTitle = null;       // its title, used to spot a stale title mid-navigation
let current = null;         // the video we're timing: { videoId, playedSeconds, lastTime, titleWaitMs }

function extensionAlive() {
  // After the extension is reloaded, old content scripts lose access to chrome.* APIs
  try {
    return Boolean(chrome.runtime && chrome.runtime.id);
  } catch (e) {
    return false;
  }
}

function getVideoId() {
  const url = new URL(window.location.href);
  if (url.searchParams.get("v")) {
    return url.searchParams.get("v");
  }
  const shorts = url.pathname.match(/^\/shorts\/([\w-]+)/);
  return shorts ? shorts[1] : null;
}

function getVideoUrl(videoId) {
  if (window.location.pathname.startsWith("/shorts/")) {
    return `https://www.youtube.com/shorts/${videoId}`;
  }
  // Clean link without playlist/timestamp junk (keeps music.youtube.com links on YouTube Music)
  return `${window.location.origin}/watch?v=${videoId}`;
}

function getTitle() {
  // YouTube (and YouTube Music) publish the current track here
  const metadata = navigator.mediaSession && navigator.mediaSession.metadata;
  if (metadata && metadata.title) {
    return metadata.title.trim();
  }

  const titleSelectors = [
    "h1.ytd-watch-metadata yt-formatted-string",
    "#title h1 yt-formatted-string",
    "ytmusic-player-bar .title",
    "h1 yt-formatted-string"
  ];
  for (const selector of titleSelectors) {
    const el = document.querySelector(selector);
    if (el && el.textContent.trim()) {
      return el.textContent.trim();
    }
  }

  // "(3) Song name - YouTube" -> "Song name"
  const pageTitle = document.title.replace(/^\(\d+\)\s*/, "").replace(/\s*-\s*YouTube( Music)?$/, "").trim();
  return pageTitle && pageTitle !== "YouTube" ? pageTitle : null;
}

function checkVideo() {
  if (!extensionAlive()) {
    stopMonitoring();
    return;
  }

  const videoId = getVideoId();
  if (!videoId || videoId === lastVideoId) {
    return;
  }
  if (!current || current.videoId !== videoId) {
    current = { videoId, playedSeconds: 0, lastTime: null, titleWaitMs: 0 };
  }

  const video = document.querySelector("#movie_player video, video");
  if (!video || document.querySelector(".ad-showing")) {
    current.lastTime = null; // don't count ads as watching
    return;
  }

  // Count real playback: pauses add nothing, seeks are ignored
  const step = current.lastTime === null ? 0 : video.currentTime - current.lastTime;
  if (step > 0 && step < (CHECK_EVERY_MS / 1000) * 3) {
    current.playedSeconds += step;
  }
  current.lastTime = video.currentTime;
  if (current.playedSeconds < MIN_PLAY_SECONDS) {
    return;
  }

  // YouTube can keep showing the previous title for a moment after switching videos
  const title = getTitle();
  if ((!title || title === lastTitle) && current.titleWaitMs < TITLE_WAIT_MS) {
    current.titleWaitMs += CHECK_EVERY_MS;
    return;
  }

  lastVideoId = videoId;
  lastTitle = title;
  current = null;

  const videoData = {
    videoId: videoId,
    title: title || "YouTube video",
    url: getVideoUrl(videoId)
  };
  console.log("♡ sharing:", videoData.title);

  try {
    chrome.runtime.sendMessage({ type: "VIDEO_PLAYING", data: videoData }, () => {
      // Reading lastError stops Chrome logging "Receiving end does not exist"
      void chrome.runtime.lastError;
    });
  } catch (e) {
    console.log("(・_・;) extension was reloaded — please refresh this tab");
    stopMonitoring();
  }
}

function startMonitoring() {
  if (checkInterval) {
    return;
  }
  console.log("♡ monitoring started ♪(๑ᴖ◡ᴖ๑)♪");
  checkInterval = setInterval(checkVideo, CHECK_EVERY_MS);
}

function stopMonitoring() {
  if (checkInterval) {
    clearInterval(checkInterval);
    checkInterval = null;
    console.log("♡ monitoring stopped, sleep well (-, - )…zzZ");
  }
  lastVideoId = null;
  lastTitle = null;
  current = null;
}

// The popup's Start/Stop buttons just flip isMonitoring in storage
chrome.storage.local.get(["isMonitoring"], (result) => {
  if (result && result.isMonitoring) {
    startMonitoring();
  }
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.isMonitoring) {
    if (changes.isMonitoring.newValue) {
      startMonitoring();
    } else {
      stopMonitoring();
    }
  }
});
