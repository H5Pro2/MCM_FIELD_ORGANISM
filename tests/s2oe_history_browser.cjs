const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {pathToFileURL} = require('url');
const {chromium} = require(process.env.MCM_PLAYWRIGHT);
(async () => {
  const directory = process.argv[2];
  const expected = JSON.parse(fs.readFileSync(path.join(directory, 'expected.json'), 'utf8'));
  const browser = await chromium.launch({headless:true, channel:'msedge'});
  try {
    const page = await browser.newPage();
    const errors = [], requests = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {if (/^https?:/.test(request.url())) requests.push(request.url());});
    await page.goto(pathToFileURL(path.join(directory, 'view.html')).href);
    for (const viewport of [{width:1280,height:900},{width:390,height:844}]) {
      await page.setViewportSize(viewport);
      for (let i=0; i<expected.length; i++) {
        await page.selectOption('#history-event', String(i+1));
        assert((await page.locator('#history-event option:checked').textContent()).includes(expected[i].event));
        assert((await page.locator('#context').textContent()).includes(expected[i].context));
        assert((await page.locator('#history-provenance').textContent()).includes(expected[i].state));
        assert((await page.locator('#phase').textContent()).includes('Historischer'));
        if (i%2===1) {
          assert((await page.locator('#history-candidates').textContent()).includes('Generation ab Ereignis '+expected[i].birth));
          assert((await page.locator('#history-basis').textContent()).includes('0: 0.25'));
          assert((await page.locator('#history-basis').textContent()).includes('2: 0.75'));
        }
      }
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    assert.equal(await page.locator('video').count(), 0);
    assert.equal(await page.locator('#start').count(), 0);
    assert.deepEqual(errors, []);
    assert.deepEqual(requests, []);
    console.log('BROWSER_OK desktop/mobile; independent fixture expectations; no network/media/start');
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});
