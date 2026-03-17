const registerForm = document.getElementById("register-form");
const loginForm = document.getElementById("login-form");
const logoutButton = document.getElementById("logout-button");
const authMessage = document.getElementById("auth-message");
const authResult = document.getElementById("auth-result");

const textForm = document.getElementById("text-form");
const audioForm = document.getElementById("audio-form");
const textResult = document.getElementById("text-result");
const audioResult = document.getElementById("audio-result");
const historyList = document.getElementById("history-list");
const audioFileInput = document.getElementById("audio-file");
const audioPreview = document.getElementById("audio-preview");
const recordStartButton = document.getElementById("record-start");
const recordStopButton = document.getElementById("record-stop");
const recordingStatus = document.getElementById("recording-status");
const registerInviteCodeInput = document.getElementById("register-invite-code");

let currentUser = null;
let mediaRecorder = null;
let recordedChunks = [];
let recordedBlob = null;
let inviteOnlyMode = false;

function showResult(target, payload) {
  target.textContent = JSON.stringify(payload, null, 2);
}

function setAuthState(user) {
  currentUser = user;
  const authenticated = Boolean(user);

  authMessage.textContent = authenticated
    ? `目前登入中：${user.username}`
    : "尚未登入。";

  logoutButton.disabled = !authenticated;

  [textForm, audioForm].forEach((form) => {
    Array.from(form.elements).forEach((element) => {
      element.disabled = !authenticated;
    });
  });

  if (!authenticated) {
    historyList.innerHTML = '<div class="empty-state">登入後才能查看你的健康紀錄。</div>';
  }

  if (!authenticated) {
    recordingStatus.textContent = "請先登入後再錄音。";
  } else if (!recordedBlob) {
    recordingStatus.textContent = "尚未開始錄音。";
  }
}

function setBetaAccessState(inviteOnly) {
  inviteOnlyMode = inviteOnly;
  if (inviteOnly) {
    registerInviteCodeInput.required = true;
    registerInviteCodeInput.placeholder = "封測中，註冊需要有效邀請碼";
  } else {
    registerInviteCodeInput.required = false;
    registerInviteCodeInput.placeholder = "目前可留空";
  }
}

function renderHistory(items) {
  if (!items.length) {
    historyList.innerHTML = '<div class="empty-state">目前還沒有你的健康資料。</div>';
    return;
  }

  historyList.innerHTML = items.map((item) => `
    <article class="history-item">
      <h3>${item.user_id} · #${item.id}</h3>
      <p>心率：${item.heart_rate ?? "未提供"}</p>
      <p>喝水量：${item.water_intake ?? "未提供"}</p>
      <p>睡眠時數：${item.sleep_hours ?? "未提供"}</p>
    </article>
  `).join("");
}

async function loadAuthState() {
  const response = await fetch("/auth/me");
  const payload = await response.json();
  setAuthState(payload.user);
  return payload.user;
}

async function loadBetaAccessState() {
  const response = await fetch("/beta/access");
  const payload = await response.json();
  setBetaAccessState(Boolean(payload.invite_only));
}

async function loadHistory() {
  if (!currentUser) {
    return;
  }

  const response = await fetch("/health-data");
  const payload = await response.json();
  renderHistory(payload.items || []);
}

async function submitJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const payload = await response.json();
  return { response, payload };
}

function resetRecordingPreview() {
  recordedBlob = null;
  audioPreview.removeAttribute("src");
  audioPreview.load();
}

function setRecorderButtons(isRecording) {
  recordStartButton.disabled = !currentUser || isRecording;
  recordStopButton.disabled = !currentUser || !isRecording;
}

function getRecordedFile() {
  if (!recordedBlob) {
    return null;
  }

  const extension = recordedBlob.type.includes("mp4") ? "m4a" : "webm";
  return new File([recordedBlob], `nuvora-recording.${extension}`, {
    type: recordedBlob.type || "audio/webm",
  });
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    showResult(audioResult, { error: "目前瀏覽器不支援直接錄音，請改用上傳音檔。" });
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const preferredMimeType = MediaRecorder.isTypeSupported("audio/webm")
      ? "audio/webm"
      : "";

    recordedChunks = [];
    mediaRecorder = preferredMimeType
      ? new MediaRecorder(stream, { mimeType: preferredMimeType })
      : new MediaRecorder(stream);

    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    });

    mediaRecorder.addEventListener("stop", () => {
      recordedBlob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || "audio/webm" });
      audioPreview.src = URL.createObjectURL(recordedBlob);
      recordingStatus.textContent = "錄音完成，可以直接送出或重新錄一次。";
      setRecorderButtons(false);
      stream.getTracks().forEach((track) => track.stop());
    });

    mediaRecorder.start();
    resetRecordingPreview();
    recordingStatus.textContent = "錄音中...";
    setRecorderButtons(true);
  } catch (error) {
    showResult(audioResult, { error: "無法啟用麥克風，請確認瀏覽器權限已開啟。" });
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
}

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const { response, payload } = await submitJson("/auth/register", {
    username: document.getElementById("register-username").value,
    password: document.getElementById("register-password").value,
    invite_code: registerInviteCodeInput.value,
  });

  showResult(authResult, payload);
  if (response.ok) {
    setAuthState(payload.user);
    await loadHistory();
  }
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const { response, payload } = await submitJson("/auth/login", {
    username: document.getElementById("login-username").value,
    password: document.getElementById("login-password").value,
  });

  showResult(authResult, payload);
  if (response.ok) {
    setAuthState(payload.user);
    await loadHistory();
  }
});

logoutButton.addEventListener("click", async () => {
  const { payload } = await submitJson("/auth/logout", {});
  showResult(authResult, payload);
  resetRecordingPreview();
  setRecorderButtons(false);
  setAuthState(null);
});

textForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const { response, payload } = await submitJson("/parse-text", {
    text: document.getElementById("text-input").value,
    save: document.getElementById("text-save").checked,
  });

  showResult(textResult, payload);
  if (response.ok) {
    await loadHistory();
  }
});

audioForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = audioFileInput.files[0] || getRecordedFile();
  if (!file) {
    showResult(audioResult, { error: "請先錄音或選擇音檔" });
    return;
  }

  const formData = new FormData();
  formData.append("audio", file);
  formData.append("save", document.getElementById("audio-save").checked);

  const response = await fetch("/whisper", {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  showResult(audioResult, payload);
  if (response.ok) {
    await loadHistory();
  }
});

recordStartButton.addEventListener("click", startRecording);
recordStopButton.addEventListener("click", stopRecording);

audioFileInput.addEventListener("change", () => {
  if (audioFileInput.files[0]) {
    recordedBlob = null;
    audioPreview.src = URL.createObjectURL(audioFileInput.files[0]);
    recordingStatus.textContent = "已選擇音檔，可以直接送出。";
  }
});

Promise.all([loadBetaAccessState(), loadAuthState()]).then(([, user]) => {
  setRecorderButtons(false);
  if (user) {
    loadHistory();
  }
});
