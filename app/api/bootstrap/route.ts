import {bootstrap,json} from '../../../lib/database';
export async function GET(request:Request){try{return json(await bootstrap(Number(new URL(request.url).searchParams.get('step')||'0')))}catch(e){console.error('bootstrap',e);return json({error:'초기 데이터를 준비하지 못했습니다. 새로고침해 주세요.'},503)}}
