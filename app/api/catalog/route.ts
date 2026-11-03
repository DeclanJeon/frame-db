import {json,listEntries,summary} from '../../../lib/database';
export async function GET(request:Request){try{const p=new URL(request.url).searchParams;return json(p.get('summary')==='1'?await summary():await listEntries(p))}catch(e){console.error('catalog',e);return json({error:'데이터베이스를 준비하지 못했습니다. 잠시 후 다시 시도해 주세요.'},503)}}
