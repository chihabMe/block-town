// Renders the baked frames of an episode with Three.js in headless Chrome and saves them as JPEGs.
// Normally run by render_threejs.sh:
//   TJ_DATA=EPISODE/threejs TJ_FRAMES=EPISODE/frames node SKILL/blockworld/threejs/capture.mjs
// TJ_DATA holds bake.py's output (scene.glb, materials.json, anim.json, anim.bin, tex/).
// TJ_CAPTURE=threads (default): the page snapshots each frame (createImageBitmap) and 3 background threads in the page
//   (web workers with OffscreenCanvas) compress them to JPEG and post the bytes here, while the next frame draws.
//   The browser's own on-thread JPEG encoder was the slowest step (~95 ms a frame); this cuts a frame to ~50 ms.
// TJ_CAPTURE=blob: the page encodes each frame in the background (canvas.toBlob) while it draws the next one,
//   and posts the JPEG bytes straight to this script (no base64 text). TJ_WORKERS=N browsers share the frames (default 1: a second one only gained ~6% on a 14 GB laptop).
// TJ_CAPTURE=canvas encodes in the page with toDataURL (older, ~2x slower). TJ_CAPTURE=screenshot uses a page screenshot.
// Frames are named f_####.jpg from the bake's first frame (anim.json f0), so a partial render drops into place.
// CHROME may point at the browser; otherwise the usual Chrome / Chromium paths are tried.
import http from "node:http";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile, rename } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const KIT = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.resolve(process.env.TJ_DATA || ".");
const OUT = path.resolve(process.env.TJ_FRAMES || path.join(DATA, "frames"));
const QUALITY = Number(process.env.TJ_JPEG || "93");
const SCALE = Math.min(1, Math.max(0.25, Number(process.env.TJ_SCALE || "1")));   // 0.5 = the 540x960 draft
const VW = Math.round(1080 * SCALE), VH = Math.round(1920 * SCALE);
// canvas: the page encodes the WebGL canvas right after drawing, and Node writes the file while the next frame draws.
// screenshot: the older page screenshot (slower, same picture).
const CAPTURE = process.env.TJ_CAPTURE || "threads";
const RELAUNCH = Number(process.env.TJ_RELAUNCH || 1200);   // frames per browser before a restart
const THREADS = Number(process.env.TJ_THREADS || 3);             // compression threads per browser (threads capture)
const WORKERS = Number(process.env.TJ_WORKERS || 1);
for (const [name, value] of Object.entries({ THREADS, WORKERS, RELAUNCH })) {
  if (!Number.isInteger(value) || value < 1) throw new Error(`${name} must be a positive integer`);
}
if (!["threads", "blob", "canvas", "screenshot"].includes(CAPTURE)) throw new Error("invalid TJ_CAPTURE");
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
  return new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      if (req.method === "POST" && req.url.startsWith("/frame/")) {   // a finished JPEG from the page
        const name = req.url.slice(7).replace(/[^0-9]/g, "");
        const parts = [];
        req.on("data", (c) => parts.push(c));
        req.on("end", async () => {
          try {
            const target = path.join(OUT, `f_${name.padStart(4, "0")}.jpg`);
            await writeFile(target + ".tmp", Buffer.concat(parts));
            await rename(target + ".tmp", target);
            res.writeHead(204); res.end();
          } catch (err) {
            console.error("frame write failed:", err.message);
            res.writeHead(500); res.end("frame write failed");
          }
        });
        return;
      }
      const rel = decodeURIComponent(new URL(req.url, "http://127.0.0.1").pathname).replace(/^\/+/, "") || "scene.html";
      const root = rel === "scene.html" || rel.startsWith("node_modules/") || rel.startsWith("fonts/") ? KIT : DATA;
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
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

await mkdir(OUT, { recursive: true });
const wall0 = Date.now();
const server = await serve();

let info = null;

async function launch(w) {
  // (Re)start worker w's browser and load the scene. Returns { browser, page }.
  if (w.page) { try { await w.page.close(); } catch {} }
  if (w.browser) { try { await w.browser.close(); } catch {} }
  w.browser = await puppeteer.launch({
    executablePath: chrome(),
    headless: "new",
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--ignore-gpu-blocklist", "--enable-gpu", "--use-gl=angle",
           `--window-size=${VW},${VH}`, "--hide-scrollbars", "--force-device-scale-factor=1",
           ...(process.env.TJ_SOFTWARE === "1" ? ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] : [])],
  });
  w.page = await w.browser.newPage();
  await w.page.setViewport({ width: VW, height: VH, deviceScaleFactor: 1 });
  w.page.on("pageerror", (err) => console.error("PAGE", err));
  w.page.on("console", (m) => { if (m.type() === "error" && !m.text().includes("404")) console.error("CONSOLE", m.text()); });
  // ?s= sets the draft size; TJ_QUERY=post=0 passes renderer options (scene.html)
  await w.page.goto(`http://127.0.0.1:${server.address().port}/scene.html?s=${SCALE}${process.env.TJ_QUERY ? "&" + process.env.TJ_QUERY : ""}`, { waitUntil: "networkidle0", timeout: 180000 });
  await w.page.waitForFunction("window.__ready === true", { timeout: 180000 });
  if (!info) {
    info = await w.page.evaluate(() => window.__check);
    console.log("CHECK", JSON.stringify(info));
    if (info.missing) console.error(`WARNING: ${info.missing} meshes have no material recipe`);
  }
  w.drawn = 0;
}

const first = { id: 0 };
const workers = [first];
try {
await launch(first);
const f0 = info.f0 || 0;
const frames = Number(process.env.FRAMES || info.frames);
const loop0 = Date.now();
let render = 0;
let done = 0;

// TJ_ONLY=0,150,300 draws just those frames of the bake (quick look tests); TJ_QUERY=post=0 passes renderer options.
const only = process.env.TJ_ONLY ? new Set(process.env.TJ_ONLY.split(",").map(Number)) : null;
const fpath = (i) => path.join(OUT, `f_${String(f0 + i).padStart(4, "0")}.jpg`);
const todo = [];
for (let i = 0; i < frames; i++) if ((!only || only.has(i)) && !existsSync(fpath(i))) todo.push(i);
console.log(`${todo.length} of ${frames} frames to draw (${frames - todo.length} cached), ${CAPTURE} capture, ${WORKERS} worker(s)`);

// One shared queue of small chunks, so fast workers take more.
const CHUNK = 40;
const queue = [];
for (let k = 0; k < todo.length;) {                       // chunks of consecutive frames
  let e = k + 1;
  while (e < todo.length && e - k < CHUNK && todo[e] === todo[e - 1] + 1) e++;
  queue.push(todo.slice(k, e));
  k = e;
}

async function drawChunk(w, chunk) {
  if (CAPTURE === "threads") {
    render += await w.page.evaluate(async (list, f0, q, nThreads) => {
      const canvas = document.querySelector("canvas");
      if (!window.__pool) {                      // background threads that turn frames into JPEGs and post them
        const src = `onmessage = async (e) => {
          const { bmp, n, q, url } = e.data;
          try {
          const oc = new OffscreenCanvas(bmp.width, bmp.height);
          oc.getContext("2d").drawImage(bmp, 0, 0);
          bmp.close();
          const blob = await oc.convertToBlob({ type: "image/jpeg", quality: q });
          const r = await fetch(url + "/frame/" + n, { method: "POST", body: blob, signal: AbortSignal.timeout(60000) });
          postMessage(r.ok ? n : -1);
          } catch (err) { postMessage(-1); }
        };`;
        const url = URL.createObjectURL(new Blob([src], { type: "text/javascript" }));
        window.__pool = Array.from({ length: nThreads }, () => new Worker(url));
      }
      const pool = window.__pool;
      let pending = 0, failed = 0;
      const waiting = [];
      const wake = () => { const r = waiting.shift(); if (r) r(); };
      let fatal = null;
      for (const wk of pool) {
        wk.onmessage = (e) => { pending--; if (e.data < 0) failed++; wake(); };
        wk.onerror = (e) => { fatal = new Error(e.message || "JPEG worker failed"); wake(); };
        wk.onmessageerror = () => { fatal = new Error("JPEG worker message failed"); wake(); };
      }
      const wait = async () => {
        if (fatal) throw fatal;
        let timer;
        try {
          await Promise.race([new Promise((r) => waiting.push(r)), new Promise((_, reject) => {
            timer = setTimeout(() => reject(new Error("JPEG worker timed out")), 90000);
          })]);
        } finally { clearTimeout(timer); }
        if (fatal) throw fatal;
      };
      let t = 0;
      for (const [j, k] of list.entries()) {
        t += window.renderAt(k);
        const bmp = await createImageBitmap(window.frameCanvas ? window.frameCanvas(k) : canvas);
        while (pending >= pool.length * 2) await wait();
        pending++;
        pool[j % pool.length].postMessage({ bmp, n: f0 + k, q, url: location.origin }, [bmp]);
      }
      while (pending > 0) await wait();
      if (failed) throw new Error(`${failed} frames failed to save`);
      return t;
    }, chunk, f0, QUALITY / 100, THREADS);
    return;
  }
  if (CAPTURE === "blob") {
    // Draw each frame, snapshot it with toBlob (the JPEG encodes on another thread while the next frame draws) and
    // post the bytes. At most 8 frames are in flight.
    const ms = await w.page.evaluate(async (list, q, f0) => {
      const canvas = document.querySelector("canvas");
      const flying = new Set();
      let failure = null;
      let t = 0;
      for (const k of list) {
        t += window.renderAt(k);
        const src = window.frameCanvas ? window.frameCanvas(k) : canvas;
        const p = new Promise((ok, bad) => src.toBlob((b) => {
          if (!b) { bad(new Error("toBlob gave nothing")); return; }
          fetch(`/frame/${f0 + k}`, { method: "POST", body: b, signal: AbortSignal.timeout(60000) })
            .then((r) => r.ok ? ok() : bad(new Error(`frame save HTTP ${r.status}`)), bad);
        }, "image/jpeg", q));
        const tracked = p.catch((err) => { failure = err; }).finally(() => flying.delete(tracked));
        flying.add(tracked);
        if (flying.size >= 8) await Promise.race(flying);
        if (failure) throw failure;
      }
      await Promise.all(flying);
      if (failure) throw failure;
      return t;
    }, chunk, QUALITY / 100, f0);
    render += ms;
  } else {
    for (const i of chunk) {
      if (CAPTURE === "screenshot") {
        render += await w.page.evaluate((k) => window.renderAt(k), i);
        await w.page.screenshot({ path: fpath(i), type: "jpeg", quality: QUALITY });
      } else {
        const [ms, url] = await w.page.evaluate((k, q) => {
          const t = window.renderAt(k);
          return [t, (window.frameCanvas ? window.frameCanvas(k) : document.querySelector("canvas")).toDataURL("image/jpeg", q)];
        }, i, QUALITY / 100);
        render += ms;
        await writeFile(fpath(i), Buffer.from(url.slice(url.indexOf(",") + 1), "base64"));
      }
    }
  }
}

async function worker(w) {
  if (!w.page) await launch(w);
  while (queue.length) {
    let chunk = queue.shift();
    const chunkSize = chunk.length;
    let attempts = 0;
    while (true) {
      if (w.drawn >= RELAUNCH) await launch(w);            // a fresh browser now and then keeps memory flat
      try {
        await drawChunk(w, chunk);
        w.drawn += chunk.length;
        break;
      } catch (err) {
        attempts++;
        console.error(`worker ${w.id}: error on frames ${f0 + chunk[0]}-${f0 + chunk.at(-1)} (attempt ${attempts}):`, err.message);
        if (attempts >= 3) throw err;
        chunk = chunk.filter((i) => !existsSync(fpath(i)));
        await launch(w);
      }
    }
    const before = done;
    done += chunkSize;
    if (Math.floor(done / 300) > Math.floor(before / 300) || !queue.length)
      console.log(`${done} of ${todo.length} frames drawn`);
  }
  if (w.browser) await w.browser.close();
}

for (let k = 1; k < Math.min(WORKERS, Math.max(1, queue.length)); k++) workers.push({ id: k });
await Promise.all(workers.map(worker));
const loop = (Date.now() - loop0) / 1000;
const n = Math.max(1, todo.length);
await writeFile(path.join(DATA, "capture.json"), JSON.stringify({ info, frames, drawn: todo.length, capture: CAPTURE,
  workers: workers.length, loop_s: loop, per_frame_s: loop / n, render_ms: render / n,
  total_s: (Date.now() - wall0) / 1000 }, null, 1));
console.log(`frames ${todo.length} in ${loop.toFixed(1)} s => ${(loop / n).toFixed(3)} s/frame ` +
            `(render ${(render / n).toFixed(1)} ms, ${workers.length} worker(s), ${CAPTURE}); written to ${OUT}`);
} finally {
  await Promise.allSettled(workers.map((w) => w.browser?.close()));
  server.close();
}
