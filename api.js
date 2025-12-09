// api.js
// CHANGE THIS to your Kali IP
const KALI_IP = "192.168.56.104";
const BASE_URL = `http://${KALI_IP}:5000`;

// Console helper (works if page has #consoleBox)
function logConsole(msg) {
  const c = document.getElementById("consoleBox");
  if (!c) return;
  c.innerHTML += "<br> > " + msg;
  c.scrollTop = c.scrollHeight;
}

// Backend API wrappers
async function apiTestNmap(target) {
  const resp = await fetch(`${BASE_URL}/api/test-nmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target })
  });
  if (!resp.ok) throw new Error(`Nmap error ${resp.status}: ${await resp.text()}`);
  return resp.json();
}

async function apiHttpLoadTest(url, requests) {
  const resp = await fetch(`${BASE_URL}/api/http-load-test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, requests })
  });
  if (!resp.ok) throw new Error(`HTTP load error ${resp.status}: ${await resp.text()}`);
  return resp.json();
}

async function apiCapacityTest(url, steps) {
  const resp = await fetch(`${BASE_URL}/api/capacity-test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, steps })
  });
  if (!resp.ok) throw new Error(`Capacity error ${resp.status}: ${await resp.text()}`);
  return resp.json();
}

// Local history storage
function saveHistory(entry) {
  const key = "trafficHistory";
  const raw = localStorage.getItem(key);
  const arr = raw ? JSON.parse(raw) : [];
  arr.push(entry);
  localStorage.setItem(key, JSON.stringify(arr));
}

function loadHistory() {
  const key = "trafficHistory";
  const raw = localStorage.getItem(key);
  return raw ? JSON.parse(raw) : [];
}
