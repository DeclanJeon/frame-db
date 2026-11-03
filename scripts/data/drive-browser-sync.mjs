/** Upload through the user's signed-in browser; never inspect credentials. */
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, basename } from 'node:path';
import { listPublicFolder } from './drive-public.mjs';

const root = new URL('../../', import.meta.url);
const plan = JSON.parse(await readFile(new URL('data/drive-upload-plan.json', root), 'utf8'));
const stateURL = new URL('data/drive-upload-state.json', root);
const state = JSON.parse(await readFile(stateURL, 'utf8'));
const skillRoot = process.env.OMO_BROWSER_SKILL_ROOT;
if (!skillRoot) throw new Error('Set OMO_BROWSER_SKILL_ROOT to the installed browser skill directory');
const { loadOmowright } = await import(`${skillRoot}/scripts/omowright.mjs`);
const { omowright } = await loadOmowright();
const session = await omowright.connectBrowserSkill({ name: 'FRAME DB classified Drive upload', focused: false });
const saveState = () => writeFile(stateURL, JSON.stringify(state, null, 2) + '\n');

async function evaluate(expression, timeoutMs = 30000) {
  const result = await session.evaluate(expression, { awaitPromise: true, timeoutMs });
  if (!result.ok) throw new Error(JSON.stringify(result.error));
  return result.value;
}

async function waitDOM(predicate, timeoutMs = 30000) {
  return evaluate(`new Promise((resolve,reject)=>{
    const observer=new MutationObserver(check);
    const timer=setTimeout(()=>{observer.disconnect();reject(new Error('DOM condition timed out'));},${timeoutMs - 1000});
    function check(){const value=(${predicate});if(value){observer.disconnect();clearTimeout(timer);resolve(value);}}
    observer.observe(document.documentElement,{childList:true,subtree:true,attributes:true,characterData:true});
    check();
  })`, timeoutMs);
}

async function openFolder(id) {
  await session.navigate(`https://drive.google.com/drive/folders/${id}`, { waitUntil: 'load' });
  await waitDOM(`document.querySelector('button[aria-label="신규"][aria-disabled="false"]')!==null`);
}

async function openMenuItem(prefix, marker) {
  // Read the live element before choosing it; Drive's AX snapshot can omit menus.
  const current = await evaluate(`({newButton:!!document.querySelector('button[aria-label="신규"][aria-disabled="false"]'),menuOpen:document.querySelector('button[aria-label="신규"][aria-disabled="false"]')?.getAttribute('aria-expanded')==='true'})`);
  if (!current.newButton) throw new Error('Drive New button is unavailable');
  if (!current.menuOpen) await session.click('button[aria-label="신규"][aria-disabled="false"]');
  await waitDOM(`(()=>{const item=[...document.querySelectorAll('[role=menuitem]')].find(x=>x.getBoundingClientRect().width>0&&getComputedStyle(x).visibility!=='hidden'&&x.innerText.startsWith(${JSON.stringify(prefix)}));if(!item)return false;item.setAttribute('data-frame-action',${JSON.stringify(marker)});return {text:item.innerText};})()`);
}

async function createFolder(parentID, name) {
  await openFolder(parentID);
  await openMenuItem('새 폴더', 'new-folder');
  await session.click('[data-frame-action="new-folder"]');
  await waitDOM(`!!document.querySelector('[role=dialog] input')`);
  const dialog = await evaluate(`[...document.querySelectorAll('[role=dialog]')].map(x=>x.innerText)`);
  if (!dialog.some(text => text.includes('새 폴더'))) throw new Error('Unexpected create-folder dialog');
  await session.fill('[role=dialog] input', name);
  await session.press('Enter', { target: '[role=dialog] input' });
  return waitDOM(`(()=>{const row=[...document.querySelectorAll('[data-id]')].find(x=>x.innerText.split('\\n')[0]===${JSON.stringify(name)});return row?.getAttribute('data-id')||false;})()`);
}

try {
  const rootFolder = await listPublicFolder(state.root_folder_id);
  if (rootFolder.title !== 'FRAME_DB') throw new Error(`Unexpected target folder: ${rootFolder.title}`);
  const leafPaths = [...new Set(plan.files.map(file => dirname(file.relative_path)))];
  const folderPaths = new Set(['00_manifests']);
  for (const leaf of leafPaths) {
    let path = leaf;
    while (path !== '.') {
      folderPaths.add(path);
      path = dirname(path);
    }
  }
  const sortedPaths = [...folderPaths].sort((a, b) => a.split('/').length - b.split('/').length || a.localeCompare(b));
  for (const path of sortedPaths) {
    if (state.folders[path]) continue;
    const parent = dirname(path) === '.' ? '' : dirname(path);
    const parentID = state.folders[parent];
    const listing = await listPublicFolder(parentID);
    const matches = listing.children.filter(child => child.kind === 'folder' && child.name === basename(path));
    if (matches.length > 1) throw new Error(`Duplicate Drive folder: ${path}`);
    state.folders[path] = matches[0]?.id || await createFolder(parentID, basename(path));
    await saveState();
    console.log(`FOLDER ${path} ${state.folders[path]}`);
  }
  console.log(`FOLDERS_READY ${Object.keys(state.folders).length}`);
  if (process.argv.includes('--upload')) {
    const selectedPath = process.env.DRIVE_UPLOAD_LEAF;
    const leaves = selectedPath ? [selectedPath] : leafPaths;
    for (const path of leaves) {
      const folderID = state.folders[path];
      if (!folderID) throw new Error(`Unknown classified folder: ${path}`);
      const expected = plan.files.filter(file => dirname(file.relative_path) === path);
      const before = await listPublicFolder(folderID);
      const present = new Map(before.children.filter(child => child.kind === 'file').map(child => [child.name, child.id]));
      const missing = expected.filter(file => !present.has(basename(file.relative_path)));
      await openFolder(folderID);
      for (let offset = 0; offset < missing.length; offset += 20) {
        const chunk = missing.slice(offset, offset + 20);
        await openMenuItem('파일 업로드', 'file-upload');
        const process = Bun.spawn([
          'bsk', 'upload', '--json', '--session', session.sessionId,
          '--selector', '[data-frame-action="file-upload"]', '--timeout', '10m',
          ...chunk.flatMap(file => ['--file', new URL(file.local_path, root).pathname]),
        ], { stdout: 'pipe', stderr: 'pipe' });
        const [output, errors, status] = await Promise.all([
          new Response(process.stdout).text(), new Response(process.stderr).text(), process.exited,
        ]);
        if (status !== 0) throw new Error(`Upload delivery failed (${status}): ${output}\n${errors}`);
        console.log(`DELIVERED ${path} ${offset + chunk.length}/${missing.length} ${output.trim()}`);
        // The next batch must not navigate away from active uploads.
        await waitDOM(`(()=>{const text=document.body.innerText;return !/업로드 중|Uploading/i.test(text)&&/업로드 완료|업로드됨|Upload complete|uploaded/i.test(text);})()`, 600000);
        console.log(`BATCH_COMPLETE ${path} ${offset + chunk.length}/${missing.length}`);
      }
      const after = await listPublicFolder(folderID);
      const names = after.children.filter(child => child.kind === 'file').map(child => child.name);
      for (const file of expected) {
        if (names.filter(name => name === basename(file.relative_path)).length !== 1) {
          throw new Error(`Missing or duplicate uploaded file: ${file.relative_path}`);
        }
      }
      console.log(`LEAF_COMPLETE ${path} ${expected.length}`);
    }
  }
} finally {
  await session.stop();
}
