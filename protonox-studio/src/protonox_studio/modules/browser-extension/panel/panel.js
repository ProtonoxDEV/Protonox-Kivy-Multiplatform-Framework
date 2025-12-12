export async function activate() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return;
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      fetch('http://localhost:4173/__health')
        .then(() => import('http://localhost:4173/studio/inject.js'))
        .catch(() => import('https://cdn.jsdelivr.net/npm/protonox-studio@latest/dist/inject-standalone.js'));
    },
  });
}

window.activate = activate;
