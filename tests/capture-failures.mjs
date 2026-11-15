// Exercise browser-side capture failures without starting Blender or Chrome.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import test from 'node:test';
const source = await readFile(new URL('../blockworld/threejs/capture.mjs', import.meta.url), 'utf8');
const draw = source.slice(source.indexOf('async function drawChunk'), source.indexOf('async function worker'));
function context(mode, workerFailure = false) {
  const canvas = { toBlob: (callback) => callback({}) };
  const ctx = vm.createContext({ CAPTURE: mode, QUALITY: 93, THREADS: 1, f0: 0, render: 0,
    document: { querySelector: () => canvas }, location: { origin: 'http://test' },
    window: { renderAt: () => 1 }, Blob, URL, AbortSignal, setTimeout, clearTimeout,
    createImageBitmap: async () => ({}), fetch: async () => ({ ok: false, status: 500 }),
    Worker: class { postMessage() { queueMicrotask(() => workerFailure
      ? this.onerror({ message: 'worker crashed' }) : this.onmessage({ data: -1 })); } },
  });
  vm.runInContext(draw + '\nglobalThis.draw = drawChunk;', ctx);
  return ctx;
}
test('threaded capture rejects failed frame saves', async () => {
  const ctx = context('threads');
  await assert.rejects(ctx.draw({ page: { evaluate: (fn, ...args) => fn(...args) } }, [0, 1, 2]), /failed to save/);
});
test('thread crash releases pending wait', async () => {
  const ctx = context('threads', true);
  await assert.rejects(ctx.draw({ page: { evaluate: (fn, ...args) => fn(...args) } }, [0, 1, 2]), /worker crashed/);
});
test('blob capture rejects HTTP errors', async () => {
  const ctx = context('blob');
  await assert.rejects(ctx.draw({ page: { evaluate: (fn, ...args) => fn(...args) } }, [0, 1, 2]), /HTTP 500/);
});
