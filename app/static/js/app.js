// AKUP Evidence API - Frontend

function getApiKey() {
  return localStorage.getItem("akup_api_key");
}

function setApiKey(key) {
  localStorage.setItem("akup_api_key", key);
}

function clearApiKey() {
  localStorage.removeItem("akup_api_key");
}

function requireAuth() {
  if (!getApiKey()) {
    window.location.href = "/static/index.html";
  }
}

async function api(method, path, body = null) {
  const opts = {
    method,
    headers: {
      "X-API-Key": getApiKey(),
      "Content-Type": "application/json",
    },
  };
  if (body) opts.body = JSON.stringify(body);
  const resp = await fetch(path, opts);
  if (resp.status === 401) {
    clearApiKey();
    window.location.href = "/static/index.html";
    return;
  }
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`${resp.status}: ${text}`);
  }
  if (resp.status === 204) return null;
  return resp.json();
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function truncate(str, len = 50) {
  if (!str) return "";
  return str.length > len ? str.slice(0, len - 3) + "..." : str;
}

function showMessage(container, text, type = "success") {
  container.innerHTML = `<p class="msg msg-${type}">${escapeHtml(text)}</p>`;
  setTimeout(() => (container.innerHTML = ""), 4000);
}
