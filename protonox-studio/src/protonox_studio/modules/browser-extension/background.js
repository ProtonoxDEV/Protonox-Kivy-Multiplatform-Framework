chrome.runtime.onInstalled.addListener(() => {
  console.log('Protonox Studio extension instalada.');
});

chrome.action.onClicked.addListener((tab) => {
  chrome.tabs.sendMessage(tab.id, { type: 'PROTONOX_TOGGLE' });
});
