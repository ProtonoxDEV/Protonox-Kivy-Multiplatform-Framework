// Minimal ProtonoxVideo web component stub with HLS/MP4 fallback.
class ProtonoxVideo extends HTMLElement {
  connectedCallback() {
    const src = this.getAttribute('src') || '';
    const poster = this.getAttribute('poster') || '';
    const hls = this.getAttribute('hls') || '';
    const wrapper = document.createElement('div');
    wrapper.style.display = 'block';
    const video = document.createElement('video');
    video.controls = true;
    if (poster) video.poster = poster;
    if (hls) {
      // naive check; real impl should load hls.js when needed
      video.src = hls;
    } else if (src) {
      video.src = src;
    }
    wrapper.appendChild(video);
    this.replaceChildren(wrapper);
  }
}

if (!customElements.get('protonox-video')) {
  customElements.define('protonox-video', ProtonoxVideo);
}
