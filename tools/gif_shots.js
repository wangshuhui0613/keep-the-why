#!/usr/bin/env node
/* Screenshot every GIF scene. Requires Node + playwright.
 *
 *   NODE_PATH=<path-to-node_modules> node tools/gif_shots.js tools/demo-src/_gif-scenes.html <out-dir>
 *
 * Windows Git Bash 注意：NODE_PATH 要用 Windows 反斜杠路径并用单引号包住
 *（NODE_PATH='C:\path\to\node_modules'）；MSYS 的 /c/... 写法 Node 识别不了，
 *会静默解析失败并报莫名其妙的模块错误。
 */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  const htmlPath = process.argv[2];
  const outDir = process.argv[3];
  if (!htmlPath || !outDir) {
    console.error("usage: node tools/gif_shots.js <html-path> <out-dir>");
    process.exit(1);
  }
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 750 } });
  await page.goto("file:///" + htmlPath.replace(/\\/g, "/"));

  const scenes = ["s1", "s2", "s3", "s4", "s5", "s6"];
  for (const s of scenes) {
    await page.evaluate((id) => { location.hash = "#" + id; }, s);
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(outDir, s + ".png") });
    console.log("shot:", s);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
