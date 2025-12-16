import { readFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

// Protonox Studio Vite plugin (dev-only scaffold)
export function protonoxStudioPlugin(opts = {}) {
  const overlayPath = opts.overlayPath || "/__protonox/studio-client.js";
  const log = (...args) => console.log("[protonox]", ...args);
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const overlaySource = readFileSync(path.resolve(__dirname, "../src/protonox_studio/web/overlay_client.js"), "utf-8");

  return {
    name: "protonox-studio",
    apply: "serve",
    configureServer(server) {
      // Healthcheck
      server.middlewares.use("/__protonox/health", (_req, res) => {
        res.end("ok");
      });

      // Overlay client (dev-only, tiny stub)
      server.middlewares.use(overlayPath, (_req, res) => {
        res.setHeader("Content-Type", "application/javascript");
        res.end(overlaySource);
      });

      // Assets import stub
      server.middlewares.use("/__protonox/assets/import", async (req, res) => {
        log("asset import stub hit");
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ status: "ok", message: "asset import stub" }));
      });

      // WebSocket bridge (broadcast connect/disconnect)
      server.httpServer.on("upgrade", (req, socket, head) => {
        if (!req.url.startsWith("/__protonox/ws")) return;
        server.ws.handleUpgrade(req, socket, head, (ws) => {
          server.ws.emit("connection", ws, req);
        });
      });

      server.ws.on("connection", (ws) => {
        log("ws client connected");
        ws.send(JSON.stringify({ type: "hello", overlay: true }));
        ws.on("message", (data) => {
          log("ws msg", data.toString());
          // Echo to all clients for now
          server.ws.clients.forEach((client) => client.send(data.toString()))
        });
      });
    },
    transformIndexHtml(html) {
      if (html.includes(overlayPath)) return html;
      return html.replace("</body>", `<script type="module" src="${overlayPath}"></script></body>`);
    },
  };
}

export default protonoxStudioPlugin;
