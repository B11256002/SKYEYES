const labels = {
  on: "\u958b\u555f",
  off: "\u95dc\u9589",
  normal: "\u6b63\u5e38",
  error: "\u7570\u5e38",
  offline: "\u96e2\u7dda",
  noAlarm: "\u7121\u8b66\u5831",
  backendLost: "\u5f8c\u7aef\u9023\u7dda\u4e2d\u65b7",
  noAlarmHistory: "\u5c1a\u7121\u8b66\u5831\u7d00\u9304",
  alarmLoadFailed: "\u8b66\u5831\u7d00\u9304\u8b80\u53d6\u5931\u6557",
  sourceApplyFailed: "\u5f71\u50cf\u4f86\u6e90\u5207\u63db\u5931\u6557",
  sourceSwitching: "\u5f71\u50cf\u4f86\u6e90\u5207\u63db\u4e2d",
  current: "\u76ee\u524d",
  video: "\u6e2c\u8a66\u5f71\u7247",
  webcam: "Webcam",
  custom: "\u81ea\u8a02\u4f86\u6e90",
};

const ids = {
  fps: document.getElementById("fps"),
  detections: document.getElementById("detections"),
  inside: document.getElementById("inside"),
  tracks: document.getElementById("tracks"),
  landmarks: document.getElementById("landmarks"),
  esp32: document.getElementById("esp32"),
  stabilizer: document.getElementById("stabilizer"),
  backend: document.getElementById("backend"),
  latestAlarm: document.getElementById("latest-alarm"),
  alarmList: document.getElementById("alarm-list"),
  sourceMode: document.getElementById("source-mode"),
  sourceValue: document.getElementById("source-value"),
  sourceApply: document.getElementById("source-apply"),
  sourceStatus: document.getElementById("source-status"),
  settingYolo: document.getElementById("setting-yolo"),
  settingFrameWidth: document.getElementById("setting-frame-width"),
  settingInterval: document.getElementById("setting-interval"),
  settingRuntimeFps: document.getElementById("setting-runtime-fps"),
  settingWebFps: document.getElementById("setting-web-fps"),
  settingJpeg: document.getElementById("setting-jpeg"),
  controlTabs: document.querySelectorAll(".control-tab"),
  controlPanels: document.querySelectorAll(".control-panel"),
};

let lastSourceSignature = "";

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`${url} ${response.status}`);
  }

  return response.json();
}

async function sendJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `${url} ${response.status}`);
  }

  return data;
}

function getSourceLabel(source) {
  if (!source) {
    return labels.video;
  }

  if (source.mode === "video") {
    return labels.video;
  }

  if (source.mode === "webcam") {
    return `${labels.webcam} ${source.value || "0"}`;
  }

  if (source.mode === "custom") {
    return `${labels.custom}: ${source.value}`;
  }

  return source.label || source.mode;
}

function refreshSourceInputState() {
  const mode = ids.sourceMode.value;

  ids.sourceValue.disabled = mode === "video";

  if (mode === "video") {
    ids.sourceValue.placeholder = "";
  } else if (mode === "webcam") {
    ids.sourceValue.placeholder = "0";
  } else {
    ids.sourceValue.placeholder = "C:\\path\\video.mp4 / http://...";
  }
}

function updateSourceControls(source) {
  if (!source) {
    return;
  }

  const signature = `${source.mode}:${source.value}`;
  ids.sourceStatus.textContent = `${labels.current}: ${getSourceLabel(source)}`;

  if (signature === lastSourceSignature) {
    return;
  }

  lastSourceSignature = signature;

  if (document.activeElement !== ids.sourceMode) {
    ids.sourceMode.value = source.mode;
  }

  if (document.activeElement !== ids.sourceValue) {
    ids.sourceValue.value = source.mode === "video" ? "" : source.value;
  }

  refreshSourceInputState();
}

async function updateStatus() {
  try {
    const status = await fetchJson("/api/status");

    ids.fps.textContent = status.fps.toFixed(2);
    ids.detections.textContent = status.detections_count;
    ids.inside.textContent = status.inside_boundary_count;
    ids.tracks.textContent = status.active_tracks_count;
    ids.landmarks.textContent = status.landmarks_count;
    ids.esp32.textContent = status.esp32_mode;
    ids.stabilizer.textContent = status.stabilization_enabled ? labels.on : labels.off;
    ids.backend.textContent = status.error ? labels.error : labels.normal;
    updateSourceControls(status.source);

    ids.latestAlarm.textContent = status.error || status.latest_alarm || labels.noAlarm;
    ids.latestAlarm.classList.toggle("idle", ids.latestAlarm.textContent === labels.noAlarm);
  } catch (error) {
    ids.backend.textContent = labels.offline;
    ids.latestAlarm.textContent = labels.backendLost;
    ids.latestAlarm.classList.remove("idle");
  }
}

async function applySource() {
  const mode = ids.sourceMode.value;
  const value = mode === "video" ? "" : ids.sourceValue.value.trim();

  ids.sourceApply.disabled = true;
  ids.sourceStatus.textContent = labels.sourceSwitching;

  try {
    const source = await sendJson("/api/source", { mode, value });
    updateSourceControls(source);
    const video = document.getElementById("video");
    video.src = `/video_feed?ts=${Date.now()}`;
  } catch (error) {
    ids.sourceStatus.textContent = `${labels.sourceApplyFailed}: ${error.message}`;
  } finally {
    ids.sourceApply.disabled = false;
  }
}

async function updateAlarms() {
  try {
    const alarms = await fetchJson("/api/alarms");

    ids.alarmList.innerHTML = "";

    if (alarms.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = labels.noAlarmHistory;
      ids.alarmList.appendChild(empty);
      return;
    }

    for (const alarm of alarms) {
      const item = document.createElement("li");
      const time = document.createElement("time");
      const message = document.createElement("span");

      time.textContent = alarm.time;
      message.textContent = alarm.message;
      item.append(time, message);
      ids.alarmList.appendChild(item);
    }
  } catch (error) {
    ids.alarmList.innerHTML = `<li>${labels.alarmLoadFailed}</li>`;
  }
}

async function updateSettings() {
  const settings = await fetchJson("/api/settings");
  const precision = settings.yolo_half ? "FP16" : "FP32";

  ids.settingYolo.textContent = `${settings.yolo_device} / ${settings.yolo_image_size} / ${precision}`;
  ids.settingFrameWidth.textContent = settings.frame_width;
  ids.settingInterval.textContent = settings.vision_process_interval;
  ids.settingRuntimeFps.textContent = settings.runtime_target_fps;
  ids.settingWebFps.textContent = settings.web_stream_fps;
  ids.settingJpeg.textContent = settings.web_jpeg_quality;
}

function activateControlPanel(panelId) {
  for (const tab of ids.controlTabs) {
    tab.classList.toggle("active", tab.dataset.panel === panelId);
  }

  for (const panel of ids.controlPanels) {
    panel.classList.toggle("active", panel.id === panelId);
  }
}

async function refresh() {
  await Promise.all([updateStatus(), updateAlarms()]);
}

updateSettings();
refresh();
refreshSourceInputState();
ids.sourceMode.addEventListener("change", refreshSourceInputState);
ids.sourceApply.addEventListener("click", applySource);
for (const tab of ids.controlTabs) {
  tab.addEventListener("click", () => activateControlPanel(tab.dataset.panel));
}
setInterval(refresh, 700);
