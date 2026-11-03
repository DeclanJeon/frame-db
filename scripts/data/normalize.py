"""Normalize saved public metadata. No image downloads or synthetic record multiplication."""
from pathlib import Path
import json,re,hashlib,collections,sys
import content_pack
from content_pack import NEW_CATEGORIES, TEMPLATES, apply
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2];data=root/'data';old=json.loads((data/'catalog.json').read_text());refs=json.loads((data/'references.json').read_text())
drive_inputs=None
if '--drive' in sys.argv:
 drive_inputs=(json.loads((data/'drive-assets.json').read_text()),json.loads((data/'drive-transfer-audit.json').read_text()))
source_snapshot=json.loads((data/'gallery-sources.json').read_text())
source_ids={(s['source'],r['id']) for s in source_snapshot['sources'] for r in s['records']}
assert source_ids=={(r['source'],r['id']) for r in refs}
assert len(source_ids)==len(refs)
rows=[
('pose','포즈·자세','인물','서기, 앉기, 눕기, 이동과 자세'),('costume','의상·코디','인물','계절, 스타일, 소재와 핏'),('hair','헤어스타일','인물','길이, 커트, 가르마와 스타일링'),('makeup','메이크업·그루밍','인물','피부, 눈, 입술, 눈썹과 수염'),('expression','표정·시선','인물','감정, 강도와 얼굴의 미세 반응'),('gesture','손동작·제스처','인물','손의 방향, 제스처와 접촉'),('anatomy','얼굴·체형·실루엣','인물','외형, 비율과 정체성 앵커'),('fashion-items','패션 아이템','인물','신발, 가방, 안경과 액세서리'),('props','소품·제품 상호작용','행동','소품의 형태와 사용하는 방식'),('persona','캐릭터·페르소나','인물','동기, 조건부 행동과 말투'),('acting','행동·연기·블로킹','행동','행동 전환, 동선과 연기 의도'),('interaction','2인·그룹 상호작용','행동','인물 간 역할, 거리와 반응'),('space','공간·세트·환경','장면','공간 구조, 시간과 날씨'),('lighting','조명','장면','광원, 방향, 대비와 색'),('camera','카메라·구도','촬영','샷 크기, 시점과 프레이밍'),('camera-motion','카메라 이동','촬영','카메라 경로, 속도와 피사체 관계'),('look','비주얼 스타일·색·재질','장면','표현 매체, 팔레트와 재질'),('motion','모션·물리·VFX','행동','타이밍, 무게, 변형과 합성'),('voice','목소리 정체성','오디오','고정 음색, 공명과 발음 앵커'),('speech','말투·대사 연기·립싱크','오디오','대사 의도, 강세, 쉼과 입 움직임'),('sound','음악·환경음·효과음','오디오','음악, 폴리와 소리의 공간'),('story','이야기·대본·장르','서사·후반','비트, 장면 목적과 정보 공개'),('edit','편집·리듬·전환','서사·후반','컷 연결, 리듬과 전환'),('delivery','피니싱·자막·납품','서사·후반','그레이드, 자막과 출력 조건')]
rows.extend(NEW_CATEGORIES)
cats=[dict(id=x[0],name=x[1],group=x[2],description=x[3],target=1407 if x[0]=='costume' else 1400,sort=i) for i,x in enumerate(rows)]
catmap={'포즈':'pose','의상':'costume','헤어':'hair','표정':'expression','메이크업':'makeup','그루밍':'makeup','아이템':'fashion-items','손동작':'gesture','목소리':'voice','말투·성격':'persona','조명':'lighting','카메라':'camera','공간':'space','연속 동작':'acting','2인·그룹':'interaction','음악·효과음':'sound','편집·연속성':'edit','얼굴·체형':'anatomy','카메라 움직임':'camera-motion','대본·스토리':'story','촬영·납품':'delivery'}
# Descriptive bilingual tags, not unverified image observations.
words={'ivory':'아이보리','white':'화이트','black':'블랙','navy':'네이비','pink':'핑크','beige':'베이지','blue':'블루','green':'그린','grey':'그레이','gray':'그레이','brown':'브라운','cream':'크림','yellow':'옐로','mint':'민트','purple':'퍼플','red':'레드','orange':'오렌지','knit':'니트','frill':'프릴','ribbon':'리본','lace':'레이스','camisole':'캐미솔','dress':'원피스','skirt':'스커트','pants':'팬츠','shirt':'셔츠','blouse':'블라우스','jacket':'재킷','coat':'코트','cardigan':'카디건','sweater':'스웨터','denim':'데님','mini':'미니','midi':'미디','maxi':'맥시','pleated':'플리츠','socks':'양말','sneakers':'스니커즈','sandals':'샌들','boots':'부츠','pumps':'펌프스','heels':'힐','bag':'가방','tote':'토트','hat':'모자','necklace':'목걸이','choker':'초커','tights':'타이츠','shorts':'쇼츠','bra':'브라','briefs':'브리프','bikini':'비키니','swimsuit':'수영복','floral':'꽃무늬','satin':'새틴','silk':'실크','leather':'가죽','velvet':'벨벳','wool':'울','mesh':'메쉬','chiffon':'시폰','corset':'코르셋','gold':'골드','silver':'실버','belt':'벨트','robe':'로브','pajama':'파자마','suit':'수트','turtleneck':'터틀넥','loafers':'로퍼','tulle':'튤','cotton':'코튼','stockings':'스타킹','halter':'홀터','lingerie':'란제리'}
postures={'立ち':'서기','座り':'앉기','寝そべり':'눕기','寝':'눕기','膝立ち':'무릎 꿇기','しゃがみ':'쪼그리기'}
entries=[];variants=[];assets=[];prompts=[];tagdict={};entrytags=[]
def add_tags(e,labels):
 for label in dict.fromkeys(str(x).strip() for x in labels if x):
  tid=hashlib.sha256(label.encode()).hexdigest()[:16];tagdict[tid]=dict(id=tid,label=label,kind='keyword');entrytags.append(dict(entry_id=e,tag_id=tid))
def add(e,prompt,tags):
 e.update(version=1,updated='2026-10-29');e['search_text']=' '.join([e['id'],e['title'],e['original_title'],e['description'],*tags]).lower();entries.append(e);add_tags(e['id'],tags);prompts.append(dict(id='prompt-'+e['id'],entry_id=e['id'],text=prompt,language='mixed' if e['source_id']!='studio' else 'ko',authorship='FRAME 작성 보조 지침 / 원본 제작자 프롬프트 아님',parameters=json.dumps({'preserve':['정체성','체형','특징 위치'],'variable':[e['category_id']]},ensure_ascii=False)))
groups=collections.defaultdict(list)
for d in refs:
 if d['source']=='pose':groups[d['id'].rsplit('_',1)[0]].append(d)
for gid,items in groups.items():
 d=items[0];group='전신 화보' if 'full_sexy' in gid else '전신 표준' if gid.startswith('full') else '상반신' if gid.startswith('upper') else '2인';post=d['sub'].split(' · ')[0];post=postures.get(post,post);number=re.search(r'P\d+',gid).group() if re.search(r'P\d+',gid) else gid
 eid='pose-'+gid;labels=[group,post,d['title'],'여성',*[x['id'] for x in items],*[x['sub'] for x in items]]
 add(dict(id=eid,category_id='pose',source_id='pose-db',title=group+' · '+number,original_title=d['title'],description=d['title']+' / '+post,gender='여성',subtype=post,status='external',details=json.dumps({'원본 계통':d['tags'][0],'포즈 번호':number,'자세':post,'인원':'2인' if group=='2인' else '1인','이미지 수':len(items),'분류 근거':'원본 메타데이터; 미디어 전수 시각 검수 아님'},ensure_ascii=False)),d['prompt'],labels)
 for x in items:
  vid='v-'+x['id'];angle=x['sub'].split(' · ')[-1];variants.append(dict(id=vid,entry_id=eid,label=angle,angle=angle,attributes=json.dumps({'원본 ID':x['id'],'원본 데이터':x['original'],'리소스':x['resources']},ensure_ascii=False)));assets.append(dict(id='m-'+x['id'],entry_id=eid,variant_id=vid,kind='image',url=x['url'],availability='external_link',source_id='pose-db',original_id=x['id']))
 details=json.loads(entries[-1]['details']);details['원본 각도별 데이터']=[x['original'] for x in items];details['원본 리소스']=[dict(id=x['id'],**x['resources']) for x in items];entries[-1]['details']=json.dumps(details,ensure_ascii=False)
for d in refs:
 if d['source']!='costume':continue
 eid='costume-'+d['id'];terms=d['title'].split();ko=[words.get(x,x) for x in terms];title=' '.join(ko[:5]);labels=list(dict.fromkeys([d['sub'],*ko,*terms,'여성']))
 add(dict(id=eid,category_id='costume',source_id='costume-db',title=title,original_title=d['title'],description=' · '.join(ko),gender='여성',subtype=d['sub'],status='external',details=json.dumps({'계절·분류':d['sub'],'원본 ID':d['id'],'구성 키워드':ko,'분류 근거':'원본 키워드 기반 번역; 이미지 실측·재질 검증 아님'},ensure_ascii=False)),d['prompt'],labels)
 variants.append(dict(id='v-'+d['id'],entry_id=eid,label='원본 의상',angle=None,attributes=json.dumps({'원본 데이터':d['original'],'리소스':d['resources']},ensure_ascii=False)));assets.append(dict(id='m-'+d['id'],entry_id=eid,variant_id='v-'+d['id'],kind='image',url=d['url'],availability='external_link',source_id='costume-db',original_id=d['id']))
 details=json.loads(entries[-1]['details']);details['원본 데이터']=d['original'];details['원본 리소스']=d['resources'];entries[-1]['details']=json.dumps(details,ensure_ascii=False)
for d in old:
 cat=catmap[d['category']];add(dict(id=d['id'],category_id=cat,source_id='studio',title=d['title'],original_title='',description=d['sub'],gender=d['gender'],subtype=d['category'],status='text',details=json.dumps({'제작 지침':d['sub'],'미디어':'미확보','검토 범위':'초기 텍스트 초안; 실제 미디어 검수 전'},ensure_ascii=False)),d['prompt'],[d['category'],d['gender'],*d['tags']])
# A small independently authored foundation for domains absent from v1. Not multiplied to targets.
new={
'props':[('양손으로 머그 받치기','한 손은 손잡이를 잡고 반대 손은 컵 아래를 받친다. 뜨거운 내용물의 무게와 손목 각도를 함께 설계한다.'),('작은 제품 개봉','상자 고정 손과 덮개를 여는 손을 구분한다. 닫힘→열림→제품 노출의 상태를 유지한다.'),('휴대폰 화면 보여주기','화면을 카메라 쪽으로 향하게 하되 손가락이 주요 영역을 가리지 않도록 한다.'),('향수 분사','한 손으로 병을 고정하고 검지로 펌프를 누른다. 분사 방향과 얼굴 위치를 분리한다.')],
'look':[('중성 실사 룩','피부와 의상의 원래 색을 기준으로 삼는다. 중성 화이트밸런스와 절제된 대비를 사용한다.'),('따뜻한 필름 룩','중간톤의 온기를 유지하되 흰색과 피부색의 과도한 황변을 피한다. 입자는 출력 크기에서 비교한다.'),('차가운 도시 룩','청록 계열의 환경과 자연스러운 피부를 구분한다. 검은 영역의 디테일을 남긴다.'),('평면 일러스트','명확한 실루엣, 제한된 팔레트, 일관된 외곽선 규칙을 사용한다.'),('소프트 3D 애니메이션','둥근 형태와 넓은 하이라이트를 사용한다. 캐릭터 비율과 재질 규칙을 장면마다 유지한다.'),('흑백 인물 룩','색상 대신 명도 대비로 얼굴과 배경을 구분한다. 눈·피부·의상의 계조를 보존한다.')],
'motion':[('머리카락의 지연 반응','머리가 회전한 뒤 모발 끝이 약간 늦게 따라온다. 시작·방향 전환·정지의 차이를 구분한다.'),('옷자락의 관성','몸통 이동에 따른 옷의 뒤처짐과 정지 후 잔여 움직임을 설계한다.'),('무게 있는 물건 들기','손이 닿고 힘을 주고 물건이 이동하는 순서를 유지한다. 팔과 어깨의 반응을 연결한다.'),('물방울 낙하','중력 방향과 표면 접촉을 유지한다. 낙하·충돌·퍼짐을 구분해 표현한다.'),('얇은 증기 합성','열원 위로 상승하는 증기의 흐름, 가림과 빛의 방향을 맞춘다.'),('입자 효과의 깊이','전경·인물 주변·배경의 입자 크기와 초점을 구분한다.')],
'speech':[('수줍은 답변','정확한 대사와 의도를 먼저 기록한다. 대답 전 짧은 쉼과 작은 웃음을 사용하되 고정 음색은 유지한다.'),('단호한 거절','짧은 문장, 분명한 자음과 안정된 문장 끝을 사용한다. 큰 소리와 분노를 자동으로 추가하지 않는다.'),('발화자와 청자 반응','발화 중인 인물의 입 움직임과 듣는 인물의 반응을 별도로 지정한다.'),('쉼을 이용한 강조','강조할 단어 앞뒤 중 어디에 쉼을 둘지 명시한다. 의미와 관계없는 반복 쉼을 피한다.'),('자연스러운 호흡','대사의 의미 단위에서 호흡 위치를 기록한다. 호흡이 없는 구간은 기본값으로 명시한다.'),('언어별 대사 각색','번역문을 그대로 읽히기보다 장면의 의도·관계·발화 길이를 보존하는 현지어 대사를 작성한다.')]
}
for cat,rs in new.items():
 for i,(name,desc) in enumerate(rs):
  eid=f'FS2-{cat}-{i+1:03}';add(dict(id=eid,category_id=cat,source_id='studio',title=name,original_title='',description=desc,gender='공용',subtype='제작 지침',status='text',details=json.dumps({'미디어':'미확보','자료 유형':'직접 작성한 초기 텍스트 가이드'},ensure_ascii=False)),desc,[name,cat,'공용'])
# Curated explicit cross-domain relations, never semantic similarity claimed as measured.
lookup={e['title']:e['id'] for e in entries};rels=[]
for a,b,why in [('카페에 앉아 경청','햇살 드는 카페','경청 장면에 적용할 수 있는 공간'),('수줍은 웃음','칭찬을 들은 순간','표정과 행동 전환 연결'),('부드러운 중저음','수줍은 답변','음색 정체성과 대사 연기를 별도 적용'),('머리 귀 뒤로 넘기기','내추럴 단발','헤어와 손동작의 관계 확인'),('창가 소프트 라이트','햇살 드는 카페','공간의 창 방향에 맞춘 광원'),('네이비 비즈니스','넥타이 정리','의상과 접촉 동작'),('제품 개봉','작은 제품 개봉','연속 동작과 소품 상태'),('기준 얼굴 정면','얼굴 5각도','동일 정체성의 여러 참조 각도')]:
 if a in lookup and b in lookup:
  for x,y in [(a,b),(b,a)]:rels.append(dict(id='r-'+str(len(rels)),from_id=lookup[x],to_id=lookup[y],type='related',reason=why))
def existing_diagram(eid,cat,title,index):
 if cat not in ('lighting','camera','camera-motion'):return None
 path=root/'public/references/diagrams'/f'{eid}.svg'
 if not path.is_file():raise FileNotFoundError(path)
 return '/references/diagrams/'+path.name
# Normalization reuses the migrated diagrams; media creation is a separate operation.
diagram_generator=content_pack.diagram
try:
 content_pack.diagram=existing_diagram
 apply(entries,variants,assets,prompts,add,rels)
finally:
 content_pack.diagram=diagram_generator
paths={'pose':('designing-video-character-sheets/references/character-ssot-master-prompt.md','11,27D'),'costume':('designing-video-character-sheets/references/character-ssot-master-prompt.md','9,24,27C'),'hair':('designing-video-character-sheets/references/character-ssot-master-prompt.md','6,7'),'expression':('designing-video-character-sheets/references/character-ssot-master-prompt.md','10,11'),'anatomy':('designing-video-character-sheets/references/character-ssot-master-prompt.md','4,5,21,22,23'),'voice':('designing-character-personas/SKILL.md','voice_identity'),'speech':('designing-character-personas/SKILL.md','speech_style,performance_cues'),'persona':('designing-character-personas/SKILL.md','persona_core,behavior_rules'),'acting':('video-production-assets/SKILL.md','04-performance,06-shots'),'camera':('video-production-assets/references/storyboard-contract.md','camera,blocking'),'interaction':('video-production-assets/references/storyboard-contract.md','speech_ids,listener_response')}
for cid,(path,slots) in TEMPLATES.items():paths[cid]=(path,', '.join(slots))
mappings=[dict(id='skill-'+c['id'],category_id=c['id'],path=paths.get(c['id'],('video-production-assets/SKILL.md',c['name']))[0],slots=paths.get(c['id'],('',c['name']))[1],version='2026-10-29 / default branch inspected') for c in cats]
sources=[dict(id='pose-db',name='POSE-DB-01',url='https://ai-pose-gallery.pages.dev/',license='原寸画像の再配布・転載・再販は禁止。作品制作での参考利用等は原本条件に従う。',hosting='external_only',checked='2026-10-29'),dict(id='costume-db',name='COSTUME-DB-01',url='https://ai-costume-gallery.pages.dev/',license='画像データの再配布・転載・再販は禁止。作品制作での参考利用等は原本条件に従う。',hosting='external_only',checked='2026-10-29'),dict(id='studio',name='FRAME 제작 가이드·도식',url=None,license='직접 작성한 제작 지침과 기술 개념 도식. 실사 이미지·음성 생성 결과와 구분한다.',hosting='owned',checked='2026-10-29')]
imports=[dict(id='import-pose-20261029',source_id='pose-db',expected=1439,indexed=1439,groups=288,status='indexed',report=json.dumps({'missing':[],'coverage':'원본 메타데이터 전 항목 대조','media_downloaded':0,'media_visual_reviewed':0,'group_count':288,'angle_gap':'원본 1개 그룹은 로우앵글 없음'},ensure_ascii=False),checked='2026-10-29'),dict(id='import-costume-20261029',source_id='costume-db',expected=1407,indexed=1407,groups=1407,status='indexed',report=json.dumps({'missing':[],'coverage':'원본 메타데이터 전 항목 대조','media_downloaded':0,'media_visual_reviewed':0},ensure_ascii=False),checked='2026-10-29')]
for batch in imports:
 source=batch['source_id'].removesuffix('-db');records=[r for r in refs if r['source']==source];report=json.loads(batch['report'])
 report.update(resource_urls=len({url for r in records for url in r['resources'].values()}),raw_records_preserved=len(records),snapshot='data/gallery-sources.json')
 batch['report']=json.dumps(report,ensure_ascii=False)
result=dict(categories=cats,sources=sources,entries=entries,variants=variants,media_assets=assets,tags=list(tagdict.values()),entry_tags=entrytags,prompt_templates=prompts,entry_relations=rels,skill_mappings=mappings,import_batches=imports)
assert len(groups)==288 and len([x for x in assets if x['source_id']!='studio'])==2846
assert len(set(x['id'] for x in entries))==len(entries)
if drive_inputs:
 from drive_pack import apply_drive
 apply_drive(result,refs,*drive_inputs)
 # Reviewed web knowledge is metadata only, applied after all original Drive checks.
 from web_pack import apply_web,load_approved
 approved=load_approved(data/'web-research')
 result=apply_web(result,approved)
 from creative_pack import apply_creative,creative_revision,load_creative
 creative=load_creative(data/'web-research',approved)
 result=apply_creative(result,creative)
 from asset_pack import apply_assets,asset_revision,load_asset_pack
 asset_pack=load_asset_pack(data/'asset-production')
 result=apply_assets(result,asset_pack)
else:
 raise SystemExit('Normalization requires --drive; verified media must not regress to external links.')
(data/'database-seed.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
(data/'web-research/creative-revision.json').write_text(json.dumps(creative_revision(creative),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
(data/'asset-production/revision.json').write_text(json.dumps(asset_revision(asset_pack),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps({k:len(v) for k,v in result.items()}));print('distinct source references:',len(set(x['original_id'] for x in assets if x['source_id']!='studio')))
