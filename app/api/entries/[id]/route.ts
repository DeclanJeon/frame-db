import {detail,json} from '../../../../lib/database';
export async function GET(_:Request,{params}:{params:Promise<{id:string}>}){try{const d=await detail((await params).id);return d?json(d):json({error:'자료가 없습니다.'},404)}catch(e){console.error(e);return json({error:'상세 자료를 불러오지 못했습니다.'},503)}}
