const textForm = document.getElementById("text-form");
const audioForm = document.getElementById("audio-form");
const filterForm = document.getElementById("filter-form");
const textResult = document.getElementById("text-result");
const audioResult = document.getElementById("audio-result");
const historyList = document.getElementById("history-list");
const historyUserIdInput = document.getElementById("history-user-id");

function showResult(target, payload) {
  target.textContent = JSON.stringify(payload, null, 2);
}

function renderHistory(items) {
  if (!items.length) {
    historyList.innerHTML = '<div class="empty-state">目前還沒有符合條件的健康資料。</div>';
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

async function loadHistory(userId = "") {
  const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
  const response = await fetch(`/health-data${query}`);
  const payload = await response.json();
  renderHistory(payload.items || []);
}

textForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const response = await fetch("/parse-text", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: document.getElementById("text-user-id").value,
      text: document.getElementById("text-input").value,
      save: document.getElementById("text-save").checked,
    }),
  });

  const payload = await response.json();
  showResult(textResult, payload);
  if (response.ok) {
    await loadHistory(historyUserIdInput.value);
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
  formData.append("user_id", document.getElementById("audio-user-id").value);
  formData.append("save", document.getElementById("audio-save").checked);

  const response = await fetch("/whisper", {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  showResult(audioResult, payload);
  if (response.ok) {
    await loadHistory(historyUserIdInput.value);
  }
});

filterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadHistory(historyUserIdInput.value);
});

loadHistory();
