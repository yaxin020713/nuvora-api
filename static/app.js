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

let currentUser = null;

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

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const { response, payload } = await submitJson("/auth/register", {
    username: document.getElementById("register-username").value,
    password: document.getElementById("register-password").value,
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

  const file = document.getElementById("audio-file").files[0];
  if (!file) {
    showResult(audioResult, { error: "請先選擇音檔" });
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

loadAuthState().then((user) => {
  if (user) {
    loadHistory();
  }
});
