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
};

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`${url} ${response.status}`);
  }

  return response.json();
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

    ids.latestAlarm.textContent = status.error || status.latest_alarm || labels.noAlarm;
    ids.latestAlarm.classList.toggle("idle", ids.latestAlarm.textContent === labels.noAlarm);
  } catch (error) {
    ids.backend.textContent = labels.offline;
    ids.latestAlarm.textContent = labels.backendLost;
    ids.latestAlarm.classList.remove("idle");
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

async function refresh() {
  await Promise.all([updateStatus(), updateAlarms()]);
}

refresh();
setInterval(refresh, 700);
