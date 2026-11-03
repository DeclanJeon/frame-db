/** Upload in agbrowse's local Chrome with its installed native file chooser. */
import { createRequire } from 'node:module';
import { readFile } from 'node:fs/promises';
import { dirname, basename } from 'node:path';
import { listPublicFolder } from './drive-public.mjs';

const root = new URL('../../', import.meta.url);
const packageJSON = process.env.AGBROWSE_PACKAGE_JSON;
if (!packageJSON) throw new Error('Set AGBROWSE_PACKAGE_JSON to the installed agbrowse package.json');
const { chromium } = createRequire(packageJSON)('playwright-core');
const plan = JSON.parse(await readFile(new URL('data/drive-upload-plan.json', root), 'utf8'));
const files = process.env.DRIVE_UPLOAD_METADATA === '1'
  ? ['drive-upload-plan.json', 'drive-assets.json', 'drive-transfer-audit.json', 'drive-media-index.json']
    .map(name => ({ relative_path: `00_manifests/${name}`, local_path: `data/${name}` }))
  : plan.files;
const state = JSON.parse(await readFile(new URL('data/drive-upload-state.json', root), 'utf8'));
const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const context = browser.contexts()[0];
const page = await context.newPage();
const selected = process.env.DRIVE_UPLOAD_LEAF;
const leaves = selected ? [selected] : [...new Set(files.map(file => dirname(file.relative_path)))];
const maximum = Number(process.env.DRIVE_UPLOAD_MAX_FILES || Infinity);

try {
  const knownFolders = new Set(Object.values(state.folders));
  for (const existing of context.pages()) {
    const location = new URL(existing.url());
    const folderID = location.pathname.match(/^\/drive\/folders\/([\w-]+)$/)?.[1];
    if (location.hostname !== 'drive.google.com' || !knownFolders.has(folderID)) continue;
    if (await existing.getByRole('dialog', { name: /업로드\s*중/ }).count()) {
      await existing.bringToFront();
      console.log(`AWAITING_EXISTING_UPLOAD ${folderID}`);
      await existing.getByRole('dialog', { name: /^항목\s*\d+개\s*업로드\s*완료$/ })
        .waitFor({ state: 'visible', timeout: 1800000 });
      console.log(`EXISTING_UPLOAD_FINISHED ${folderID}`);
    }
  }
  for (const path of leaves) {
    const folderID = state.folders[path];
    if (!folderID) throw new Error(`Unknown classified Drive folder: ${path}`);
    const expected = files.filter(file => dirname(file.relative_path) === path);
    const before = await listPublicFolder(folderID);
    for (const file of expected) {
      if (before.children.filter(child => child.kind === 'file' && child.name === basename(file.relative_path)).length > 1) {
        throw new Error(`Duplicate Drive filename: ${file.relative_path}`);
      }
    }
    const present = new Set(before.children.filter(child => child.kind === 'file').map(child => child.name));
    const missing = expected.filter(file => !present.has(basename(file.relative_path))).slice(0, maximum);
    if (!missing.length) {
      console.log(`LEAF_PRESENT ${path} ${expected.length}`);
      continue;
    }
    await page.bringToFront();
    await page.goto(`https://drive.google.com/drive/folders/${folderID}`, { waitUntil: 'load' });
    await page.getByRole('button', { name: basename(path), exact: true })
      .waitFor({ state: 'visible', timeout: 30000 });
    const main = page.getByRole('main');
    if (present.size === 0) {
      await main.getByText('파일을 여기에 드래그 앤 드롭하거나', { exact: false })
        .waitFor({ state: 'visible', timeout: 30000 });
    } else {
      await main.getByRole('gridcell')
        .first().waitFor({ state: 'visible', timeout: 30000 });
    }
    const oldQueue = page.getByRole('dialog', { name: /^항목\s*\d+개\s*업로드\s*완료$/ });
    if (await oldQueue.count()) await oldQueue.getByRole('button', { name: '닫기', exact: true }).click();
    await page.getByRole('button', { name: '신규', exact: true }).click();
    await page.getByRole('menuitem', { name: /^파일 업로드/ }).waitFor({ state: 'visible' });
    const chooserReady = page.waitForEvent('filechooser', { timeout: 30000 });
    await page.getByRole('menuitem', { name: /^파일 업로드/ }).click();
    const chooser = await chooserReady;
    const completed = page.getByRole('dialog', {
      name: new RegExp(`^항목\\s*${missing.length}개\\s*업로드\\s*완료$`),
    }).waitFor({ state: 'visible', timeout: 1800000 });
    await chooser.element().evaluate(input => input.setAttribute('data-frame-drive-upload', 'true'));
    const cdp = await context.newCDPSession(page);
    const { root: document } = await cdp.send('DOM.getDocument', { depth: 1 });
    const { nodeId } = await cdp.send('DOM.querySelector', {
      nodeId: document.nodeId, selector: 'input[data-frame-drive-upload="true"]',
    });
    if (!nodeId) throw new Error('The native Drive file chooser input was not found');
    await cdp.send('DOM.setFileInputFiles', {
      nodeId, files: missing.map(file => new URL(file.local_path, root).pathname),
    });
    await cdp.detach();
    console.log(`DELIVERED ${path} ${missing.length}`);
    await completed;
    const after = await listPublicFolder(folderID);
    for (const file of missing) {
      const matches = after.children.filter(child => child.kind === 'file' && child.name === basename(file.relative_path));
      if (matches.length !== 1) {
        throw new Error(`Upload is not confirmed in the exact public destination: ${file.relative_path} (${matches.length})`);
      }
    }
    console.log(`LEAF_COMPLETE ${path} ${missing.length} uploaded; ${after.children.filter(child => child.kind === 'file').length} present`);
  }
  await page.close();
  console.log('AGBROWSE_UPLOAD_COMPLETE');
  process.exit(0);
} catch (error) {
  console.error(error);
  console.error('The work tab remains open for inspection; no sharing confirmation is clicked automatically.');
  process.exit(1);
}
