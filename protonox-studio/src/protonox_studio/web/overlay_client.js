// Protonox Studio overlay client: status HUD, WebSocket bridge, and HLS-on-demand.
// Lightweight by design; loads hls.js only when required.

const OVERLAY_PATH = '/__protonox/ws';
const HLS_CDN = 'https://cdn.jsdelivr.net/npm/hls.js@1.5.8/dist/hls.min.js';
const state = {
  ws: null,
  status: 'connecting',
  logOpen: false,
  logs: [],
};

function createHud() {
  if (document.getElementById('protonox-overlay-hud')) return;
  const style = document.createElement('style');
  style.textContent = `
    #protonox-overlay-hud { position: fixed; top: 12px; right: 12px; z-index: 2147483646; font-family: 'Inter', system-ui, -apple-system, sans-serif; }
    #protonox-overlay-pill { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px; background: rgba(20,20,20,0.9); color: #f4f4f4; box-shadow: 0 8px 30px rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08); cursor: pointer; }
    #protonox-overlay-dot { width: 10px; height: 10px; border-radius: 50%; background: #f5c400; box-shadow: 0 0 0 4px rgba(245,196,0,0.22); }
    #protonox-overlay-log { margin-top: 8px; max-width: 360px; max-height: 200px; overflow: auto; padding: 10px; border-radius: 12px; background: rgba(18,18,18,0.92); color: #d8d8d8; font-size: 12px; line-height: 1.4; border: 1px solid rgba(255,255,255,0.06); display: none; }
    #protonox-overlay-log pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
    .protonox-log-entry { opacity: 0.92; }
  `;
  document.head.appendChild(style);

  const hud = document.createElement('div');
  hud.id = 'protonox-overlay-hud';

  const pill = document.createElement('div');
  pill.id = 'protonox-overlay-pill';
  const dot = document.createElement('span');
  dot.id = 'protonox-overlay-dot';
  const label = document.createElement('span');
  label.id = 'protonox-overlay-label';
  label.textContent = 'Protonox overlay';
  const hint = document.createElement('span');
  hint.id = 'protonox-overlay-hint';
  hint.style.opacity = '0.7';
  hint.style.fontSize = '12px';
  hint.textContent = '(connecting)';

  pill.append(dot, label, hint);
  pill.addEventListener('click', () => toggleLogs());

  const log = document.createElement('div');
  log.id = 'protonox-overlay-log';
  hud.append(pill, log);
  document.body.appendChild(hud);
}

function setStatus(next, detail) {
  state.status = next;
  const dot = document.getElementById('protonox-overlay-dot');
  const hint = document.getElementById('protonox-overlay-hint');
  if (!dot || !hint) return;
  const colors = { connecting: '#f5c400', ready: '#4ade80', error: '#f87171' };
  dot.style.background = colors[next] || '#f5c400';
  dot.style.boxShadow = `0 0 0 4px ${next === 'ready' ? 'rgba(74,222,128,0.22)' : 'rgba(245,196,0,0.22)'}`;
  hint.textContent = detail ? `${next}: ${detail}` : next;
}

function pushLog(line) {
  state.logs.push(line);
  if (state.logs.length > 50) state.logs.shift();
  const log = document.getElementById('protonox-overlay-log');
  if (!log) return;
  if (state.logOpen) {
    log.innerHTML = state.logs.map((l) => `<div class="protonox-log-entry"><pre>${l}</pre></div>`).join('');
  }
}

function toggleLogs() {
  const log = document.getElementById('protonox-overlay-log');
  if (!log) return;
  state.logOpen = !state.logOpen;
  log.style.display = state.logOpen ? 'block' : 'none';
  if (state.logOpen) log.innerHTML = state.logs.map((l) => `<div class="protonox-log-entry"><pre>${l}</pre></div>`).join('');
}

async function ensureHls() {
  if (window.Hls) return window.Hls;
  if (ensureHls.loading) return ensureHls.loading;
  ensureHls.loading = new Promise((resolve) => {
    const tag = document.createElement('script');
    tag.src = HLS_CDN;
    tag.async = true;
    tag.onload = () => resolve(window.Hls || null);
    tag.onerror = () => resolve(null);
    document.head.appendChild(tag);
  });
  return ensureHls.loading;
}

async function attachHls(video, src) {
  const Hls = await ensureHls();
  if (!Hls) {
    pushLog('hls.js not available');
    video.src = src;
    return;
  }
  if (Hls.isSupported()) {
    const hls = new Hls({ enableWorker: true, lowLatencyMode: true });
    hls.loadSource(src);
    hls.attachMedia(video);
    video.addEventListener('destroy', () => hls.destroy());
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = src;
  } else {
    pushLog('No HLS support in this browser');
    video.src = src;
  }
}

function hydrateVideos(root = document) {
  root.querySelectorAll('video[data-protonox-hls], protonox-video').forEach((node) => {
    const video = node.tagName.toLowerCase() === 'video' ? node : node.querySelector('video');
    if (!video) return;
    const hlsSrc = node.getAttribute('data-protonox-hls') || node.getAttribute('hls');
    const poster = node.getAttribute('poster') || node.getAttribute('data-protonox-poster') || '';
    if (poster) video.poster = poster;
    if (hlsSrc) attachHls(video, hlsSrc);
  });
}

function observeDom() {
  const mo = new MutationObserver((records) => {
    for (const rec of records) {
      rec.addedNodes.forEach((n) => {
        if (n.nodeType === 1) hydrateVideos(n);
      });
    }
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });
}

function connectWs() {
  try {
    const proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
    const ws = new WebSocket(`${proto}${location.host}${OVERLAY_PATH}`);
    state.ws = ws;
    setStatus('connecting');
    ws.onopen = () => {
      setStatus('ready', 'overlay connected');
      ws.send(JSON.stringify({ type: 'hello', overlay: true, url: location.href }));
    };
    ws.onmessage = (ev) => {
      pushLog(ev.data);
      try {
        const msg = JSON.parse(ev.data);
        window.dispatchEvent(new CustomEvent('protonox:message', { detail: msg }));
      } catch (_) {
        window.dispatchEvent(new CustomEvent('protonox:message', { detail: { raw: ev.data } }));
      }
    };
    ws.onerror = (e) => {
      setStatus('error', 'ws error');
      pushLog(`ws error ${e.message || e.type}`);
    };
    ws.onclose = () => {
      setStatus('error', 'ws closed');
      setTimeout(connectWs, 2000);
    };
  } catch (err) {
    setStatus('error', 'ws failed');
    pushLog(String(err));
  }
}

function boot() {
  createHud();
  hydrateVideos();
  observeDom();
  connectWs();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}

window.Protonox = window.Protonox || {};
window.Protonox.overlay = {
  send: (payload) => state.ws && state.ws.readyState === 1 && state.ws.send(JSON.stringify(payload)),
  logs: state.logs,
};
