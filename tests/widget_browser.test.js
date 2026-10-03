const assert = require('node:assert/strict');
const path = require('node:path');
const { chromium } = require('/Users/goodok/.hermes/hermes-agent/node_modules/playwright');

const widget = `file://${path.resolve(__dirname, '../assets/index.html')}`;

async function openWidget({ callTool, displayMode, sendFollowUpMessage, portable = false } = {}) {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  });
  const page = await browser.newPage();
  await page.exposeFunction('__testCallTool', callTool || (async () => ({ items: [] })));
  await page.exposeFunction('__testDisplayMode', displayMode || (async () => ({})));
  await page.exposeFunction('__testSendFollowUp', sendFollowUpMessage || (async () => ({})));
  await page.addInitScript(() => {
    if (window === window.top) window.openai = {
      callTool: async (name, args) => window.__testCallTool(name, args),
      sendFollowUpMessage: async payload => window.__testSendFollowUp(payload),
      requestDisplayMode: async mode => window.__testDisplayMode(mode),
    };
  });
  if (portable) {
    await page.goto(widget);
    await page.exposeFunction('__hostCall', callTool || (async () => ({ items: [] })));
    await page.exposeFunction('__hostDisplayMode', displayMode || (async () => ({})));
    await page.evaluate(() => {
      window.addEventListener('message', async event => {
        const message = event.data;
        if (!message?.jsonrpc || message.id === undefined) return;
        if (message.method === 'ui/initialize') event.source.postMessage({ jsonrpc: '2.0', id: message.id, result: {} }, '*');
        if (message.method === 'tools/call') event.source.postMessage({ jsonrpc: '2.0', id: message.id, result: await window.__hostCall(message.params.name, message.params.arguments) }, '*');
        if (message.method === 'ui/request-display-mode') {
          try { await window.__hostDisplayMode(message.params.mode); event.source.postMessage({ jsonrpc: '2.0', id: message.id, result: {} }, '*'); }
          catch (error) { event.source.postMessage({ jsonrpc: '2.0', id: message.id, error: { message: error.message } }, '*'); }
        }
      });
    });
    await page.evaluate(src => { const iframe = document.createElement('iframe'); iframe.id = 'widget'; iframe.src = src; document.body.append(iframe); }, widget);
  } else await page.goto(widget);
  return { browser, page };
}

async function result(page, generation) {
  await page.evaluate(generation => {
    window.dispatchEvent(new MessageEvent('message', {
      source: window,
      data: { method: 'ui/notifications/tool-result', params: { structuredContent: generation } },
    }));
  }, generation);
}

async function testFilterResetAndLoadMore() {
  const calls = [];
  const { browser, page } = await openWidget({
    callTool: async (name, args) => {
      calls.push({ name, args });
      if (args.cursor === 'cursor-2') return { items: [{ id: 'two', type: 'image', url: 'https://cdn.example/two' }] };
      if (args.type === 'video') return { items: [{ id: 'video', type: 'video', url: 'https://cdn.example/video' }], next_cursor: null };
      return { items: [{ id: 'one', type: 'image', url: 'https://cdn.example/one' }], next_cursor: 'cursor-2' };
    },
  });
  try {
    await page.click('#workspace');
    await page.locator('#load-more').click();
    assert.deepEqual(calls.slice(0, 2).map(c => c.args), [
      { size: 24 },
      { size: 24, cursor: 'cursor-2' },
    ]);
    await page.locator('[data-filter="video"]').click();
    assert.deepEqual(calls[2].args, { size: 24, type: 'video' });
    assert.equal(await page.locator('#gallery .gallery-card').count(), 1);
  } finally { await browser.close(); }
}

async function testUseInChatPayloadHasNoSignedUrl() {
  const messages = [];
  const signedUrl = 'https://cdn.example/signed-result?X-Amz-Signature=secret';
  const { browser, page } = await openWidget({
    sendFollowUpMessage: async payload => messages.push(payload),
  });
  try {
    await result(page, { id: 'generation-42', type: 'image', url: signedUrl, resource_uri: 'ui://provod/generation-42' });
    await page.click('#use-chat');
    assert.equal(messages.length, 1);
    const serialized = JSON.stringify(messages[0]);
    assert.equal(serialized.includes(signedUrl), false);
    assert.match(messages[0].prompt, /generation-42/);
  } finally { await browser.close(); }
}

async function testVideoWithoutExtensionAndUnsafeUrl() {
  const { browser, page } = await openWidget();
  try {
    await result(page, { id: 'video-1', type: 'video', url: 'https://cdn.example/video-1' });
    assert.equal(await page.locator('#result-media video').count(), 1);
    await result(page, { id: 'unsafe', type: 'image', url: 'javascript:alert(1)' });
    assert.equal(await page.locator('#result-media').locator('img,video').count(), 1);
    assert.match(await page.locator('#notice').textContent(), /no safe preview URL/i);
  } finally { await browser.close(); }
}

async function testEmptyErrorAndFullscreenRejection() {
  const errors = [];
  const { browser, page } = await openWidget({
    displayMode: async () => { throw new Error('fullscreen denied'); },
    callTool: async () => ({ items: [], next_cursor: null }),
    portable: true,
  });
  try {
    await page.waitForTimeout(250);
    const frame = page.frames().find(candidate => candidate !== page.mainFrame() && candidate.url().startsWith('file://'));
    assert(frame, 'widget iframe did not load');
    await frame.locator('#workspace').click();
    await frame.locator('#gallery').waitFor({ state: 'visible' });
    await frame.locator('#gallery').getByText('No creations in this view yet').waitFor();
    assert.match(await frame.locator('#notice').textContent(), /Fullscreen is unavailable/i);
    assert.match(await frame.locator('#gallery').textContent(), /No creations in this view yet/i);
    void errors;
  } finally { await browser.close(); }
}

async function testHistoryErrorState() {
  const { browser, page } = await openWidget({ callTool: async () => { throw new Error('history unavailable'); } });
  try {
    await page.click('#workspace');
    await page.locator('#gallery').getByText('Could not load creations').waitFor();
    assert.match(await page.locator('#gallery').textContent(), /Could not load creations/i);
  } finally { await browser.close(); }
}

(async () => {
  const tests = [
    ['filter reset/cursor and load more', testFilterResetAndLoadMore],
    ['Use in chat omits signed URL', testUseInChatPayloadHasNoSignedUrl],
    ['video without extension and unsafe URL', testVideoWithoutExtensionAndUnsafeUrl],
    ['empty/error/fullscreen rejection', testEmptyErrorAndFullscreenRejection],
    ['history error state', testHistoryErrorState],
  ];
  for (const [name, test] of tests) {
    await test();
    console.log(`ok - ${name}`);
  }
  console.log(`passed ${tests.length} browser tests`);
})().catch(error => { console.error(error); process.exitCode = 1; });
