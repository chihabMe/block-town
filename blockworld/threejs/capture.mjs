// Renders the baked frames of an episode with Three.js in headless Chrome and saves them as JPEGs.
// Normally run by render_threejs.sh:
//   TJ_DATA=EPISODE/threejs TJ_FRAMES=EPISODE/frames node SKILL/blockworld/threejs/capture.mjs
// TJ_DATA holds bake.py's output (scene.glb, materials.json, anim.json, anim.bin, tex/).
// Frames are named f_####.jpg from the bake's first frame (anim.json f0), so a partial render drops into place.
// CHROME may point at the browser; otherwise the usual Chrome / Chromium paths are tried.
import http from "node:http";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const KIT = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.resolve(process.env.TJ_DATA || ".");
const OUT = path.resolve(process.env.TJ_FRAMES || path.join(DATA, "frames"));
const QUALITY = Number(process.env.TJ_JPEG || "93");
const SCALE = Math.min(1, Math.max(0.25, Number(process.env.TJ_SCALE || "1")));   // 0.5 = the 540x960 draft
const VW = Math.round(1080 * SCALE), VH = Math.round(1920 * SCALE);
const types = { ".html": "text/html", ".js": "text/javascript", ".png": "image/png", ".jpg": "image/jpeg",
                ".json": "application/json", ".glb": "model/gltf-binary", ".bin": "application/octet-stream" };

function chrome() {
  const tries = [process.env.CHROME, "/usr/bin/google-chrome-stable", "/usr/bin/google-chrome", "/usr/bin/chromium",
    "/usr/bin/chromium-browser", "/snap/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "C:/Program Files/Google/Chrome/Application/chrome.exe"];
  const hit = tries.find((p) => p && existsSync(p));
  if (!hit) throw new Error("no Chrome or Chromium found: set CHROME=/path/to/chrome");
  return hit;
}

function serve() {
  // scene.html and node_modules come from the kit; everything else from the bake folder.
  return new Promise((resolve) => {
    const server = http.createServer(async (req, res) => {
      const rel = decodeURIComponent(new URL(req.url, "http://127.0.0.1").pathname).replace(/^\/+/, "") || "scene.html";
      const root = rel === "scene.html" || rel.startsWith("node_modules/") ? KIT : DATA;
      if (rel.startsWith("node_modules/")) {                 // node_modules may be a link (a git worktree shares it)
        try {
          const data = await readFile(path.join(KIT, rel));
          res.writeHead(200, { "Content-Type": types[path.extname(rel)] || "application/octet-stream" });
          res.end(data);
        } catch { res.writeHead(404); res.end("missing"); }
        return;
      }
      const file = path.resolve(root, rel);
      if (!file.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
      try {
        const data = await readFile(file);
        res.writeHead(200, { "Content-Type": types[path.extname(file)] || "application/octet-stream" });
        res.end(data);
      } catch {
        res.writeHead(404); res.end("missing");
      }
    });
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

await mkdir(OUT, { recursive: true });
const wall0 = Date.now();
const server = await serve();

let browser = null;
let page = null;
let info = null;

async function launchBrowser() {
  if (page) {
    try { await page.close(); } catch {}
    page = null;
  }
  if (browser) {
    try { await browser.close(); } catch {}
    browser = null;
  }
  browser = await puppeteer.launch({
    executablePath: chrome(),
    headless: "new",
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--ignore-gpu-blocklist", "--enable-gpu", "--use-gl=angle",
           `--window-size=${VW},${VH}`, "--hide-scrollbars", "--force-device-scale-factor=1"],
  });
  page = await browser.newPage();
  await page.setViewport({ width: VW, height: VH, deviceScaleFactor: 1 });
  page.on("pageerror", (err) => console.error("PAGE", err));
  page.on("console", (m) => { if (m.type() === "error" && !m.text().includes("404")) console.error("CONSOLE", m.text()); });
  // ?s= sets the draft size; TJ_QUERY=post=0 passes renderer options (scene.html)
  await page.goto(`http://127.0.0.1:${server.address().port}/scene.html?s=${SCALE}${process.env.TJ_QUERY ? "&" + process.env.TJ_QUERY : ""}`, { waitUntil: "networkidle0", timeout: 180000 });
  await page.waitForFunction("window.__ready === true", { timeout: 180000 });
  if (!info) {
    info = await page.evaluate(() => window.__check);
    console.log("CHECK", JSON.stringify(info));
    if (info.missing) console.error(`WARNING: ${info.missing} meshes have no material recipe`);
  }
}

await launchBrowser();

const f0 = info.f0 || 0;
const frames = Number(process.env.FRAMES || info.frames);
const loop0 = Date.now();
let render = 0;
let drawnInBatch = 0;

// TJ_ONLY=0,150,300 draws just those frames of the bake (quick look tests); TJ_QUERY=post=0 passes renderer options.
const only = process.env.TJ_ONLY ? new Set(process.env.TJ_ONLY.split(",").map(Number)) : null;
for (let i = 0; i < frames; i++) {
  if (only && !only.has(i)) continue;
  const framePath = path.join(OUT, `f_${String(f0 + i).padStart(4, "0")}.jpg`);
  if (existsSync(framePath)) {
    if (i % 300 === 0) console.log(`frame ${f0 + i} (${i + 1} of ${frames}) [cached]`);
    continue;
  }
  if (drawnInBatch >= 250) {
    await launchBrowser();
    drawnInBatch = 0;
  }
  let attempts = 0;
  while (attempts < 3) {
    try {
      render += await page.evaluate((k) => window.renderAt(k), i);
      await page.screenshot({ path: framePath, type: "jpeg", quality: QUALITY });
      drawnInBatch++;
      break;
    } catch (err) {
      attempts++;
      console.error(`Error rendering frame ${f0 + i} (attempt ${attempts}):`, err.message);
      await launchBrowser();
      drawnInBatch = 0;
      if (attempts >= 3) throw err;
    }
  }
  if (i % 300 === 0 || i === frames - 1) console.log(`frame ${f0 + i} (${i + 1} of ${frames})`);
}
const loop = (Date.now() - loop0) / 1000;
await writeFile(path.join(DATA, "capture.json"), JSON.stringify({ info, frames, loop_s: loop,
  per_frame_s: loop / frames, render_ms: render / frames, total_s: (Date.now() - wall0) / 1000 }, null, 1));
console.log(`frames ${frames} in ${loop.toFixed(1)} s => ${(loop / frames).toFixed(3)} s/frame ` +
            `(render ${(render / frames).toFixed(1)} ms); written to ${OUT}`);
if (browser) await browser.close();
server.close();
