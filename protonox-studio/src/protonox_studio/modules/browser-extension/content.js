// Intenta usar el servidor local si está corriendo para máxima potencia
fetch('http://localhost:4173/__health')
  .then(() => import('http://localhost:4173/studio/inject.js'))
  .catch(() => import('https://cdn.jsdelivr.net/npm/protonox-studio@latest/dist/inject-standalone.js'));

console.log('%cProtonox Studio INYECTADO', 'color:#ff3366;font-size:20px;font-weight:bold');
