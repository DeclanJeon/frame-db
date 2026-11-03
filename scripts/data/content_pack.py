from pathlib import Path
import hashlib,json,re,math,html
ROOT=Path(__file__).resolve().parents[2]
NEW_CATEGORIES=[('brief','브리프·브랜드·기획','기획·운영','목적, 관객, 브랜드와 제작 범위'),('ops','제작운영·에셋관리','기획·운영','에셋 계보, 버전, 비용과 인계'),('evidence','근거·권리·출처','기획·운영','사실, 관찰, 제안과 사용 범위'),('handoff','AI 생성·참조 인계','기획·운영','참조 역할, 시간, 입력과 제출문'),('qa','품질·연속성 검수','기획·운영','정체성, 접촉, 시간과 실제 검사 범위')]
ROOT_SKILL='https://github.com/DeclanJeon/contents-production-skills/blob/main/'
TEMPLATES={
'pose':('designing-video-character-sheets/references/character-ssot-master-prompt.md',['11 Body Language','24 Variable States','27 Sheet D']),
'costume':('designing-video-character-sheets/references/character-ssot-master-prompt.md',['9 Costume DNA','24 Variable States']),
'hair':('designing-video-character-sheets/references/character-ssot-master-prompt.md',['6 Hair Identity Lock','7 Identity Anchors']),
'makeup':('designing-video-character-sheets/references/character-ssot-master-prompt.md',['5 Face Identity Lock','24 Variable States']),
'expression':('video-production-assets/assets/04-performance-template.md',['듣기 자극','전술 전환','물리 과제']),
'gesture':('video-production-assets/assets/04-performance-template.md',['상대에게 하는 행동','물리 과제']),
'anatomy':('designing-video-character-sheets/references/character-ssot-master-prompt.md',['4 Visual Identity Lock','5 Face Identity Lock','21 Silhouette','23 Proportion Reference']),
'fashion-items':('designing-video-character-sheets/references/character-ssot-master-prompt.md',['9 Costume DNA','25 DO NOT CHANGE']),
'props':('video-production-assets/assets/06-shots-template.md',['인물 블로킹','공개 정보','종료 프레임']),
'persona':('designing-character-personas/SKILL.md',['persona_core','behavior_rules','expression_bridge']),
'acting':('video-production-assets/assets/04-performance-template.md',['목표','장애','상대에게 하는 행동','숨긴 뜻','듣기 자극','전술 전환','물리 과제']),
'interaction':('video-production-assets/references/storyboard-contract.md',['speech_ids','visible_character_ids','청자 반응']),
'space':('video-production-assets/assets/06-shots-template.md',['인물 블로킹','시선/축','공개 정보']),
'lighting':('video-production-assets/assets/07-lighting-template.md',['광원 동기','방향/높이','경도/확산','색 의도','키/필 관계','배경 분리','그림자 규칙','노출 상태','매칭 주의']),
'camera':('video-production-assets/assets/06-shots-template.md',['크기/카메라 위치','인물 블로킹','시선/축','공개 정보','관점·감정/구도 의도','종료 프레임']),
'camera-motion':('video-production-assets/assets/06-shots-template.md',['shot-local time (s or frames; FPS if frames)','인물 블로킹','카메라 동작','종료 프레임','핸들']),
'look':('video-production-assets/assets/05-visual-template.md',['시각 구조','팔레트','재질','연속성']),
'motion':('video-production-assets/assets/08-animation-template.md',['행동 시작','정점','정착','보조 동작']),
'voice':('designing-character-personas/SKILL.md',['voice_identity','speech_style','performance_cues']),
'speech':('video-production-assets/assets/performance-cue-template.md',['시간/대사','화자','의도/서브텍스트','숨/멈춤','강조','속도/압력','입 우선순위','청자 반응','신체 행동']),
'sound':('video-production-assets/assets/09-edit-template.md',['audio_cues','음악','효과음','믹스']),
'story':('video-production-assets/assets/02-story-template.md',['서사 비트','정보 공개','감정 변화']),
'edit':('video-production-assets/assets/09-edit-template.md',['cut/time','대사','리듬','사운드']),
'delivery':('video-production-assets/assets/15-delivery-template.md',['자막','접근성','출력','납품']),
'brief':('video-production-assets/assets/01-brief-template.md',['목적','관객','형식','제약','미확인 사항']),
'ops':('video-production-assets/assets/14-production-ops-template.md',['일정','예산','asset_registry','dependencies']),
'evidence':('video-production-assets/assets/10-evidence-template.md',['주장','근거','출처','검증 범위']),
'handoff':('video-production-assets/assets/11-ai-handoff-template.md',['참조 역할표','초기 상태','주 행동과 구간','끝 상태','도구 지원 확인']),
'qa':('video-production-assets/assets/12-qa-template.md',['기준','실제 관찰','수정 변수','재검수 범위'])}
RULES={
'pose':('얼굴·체형·관절 길이·의상','자세·접촉·지지점','관절 꺾임, 접지 미끄러짐, 손의 소유 혼동'),
'costume':('얼굴·체형·옷의 구조·색·소재','착용법·주름·장면 상태','포켓·단추 증감, 옷이 신체를 관통함'),
'hair':('얼굴·헤어라인·길이·가르마 좌우','선택한 스타일과 선언한 상태','얼굴 재캐스팅, 머리 길이 변화, 좌우 반전'),
'makeup':('얼굴 비율·특징 위치·피부결','화장 색·질감·지정 영역','눈·입 크기 변경, 피부결 소실'),
'expression':('얼굴 구조·눈코입 비율·특징','눈·눈썹·입·턱·시선의 긴장','감정 선행, 표정 변화 중 얼굴 재설계'),
'gesture':('손 크기·손가락 수·소품 형태','그립·손목·제스처','손가락 융합, 소품 관통, 손 소유 불명'),
'anatomy':('공급된 정체성 앵커','명시한 설계 변수만','조명·화장·원근을 새 정체성으로 오인'),
'fashion-items':('제품 형태·재질·크기·착용 좌우','착용 상태·가림·자연스러운 사용감','좌우 바뀜, 스트랩 관통, 로고 임의 생성'),
'props':('수량·소유·형태·시작 상태','접촉과 물리 행동','접촉 전 이동, 소유 순간이동, 개수 증식'),
'persona':('승인된 인물 설정·행동 근거','관계·압박에 따른 반응','성격 유형으로 외모·음색 결정, 근거 없는 과거사'),
'acting':('이야기의 목표·자극·끝 상태','전술·물리 과제·반응','자극 전 반응, 시도와 완료 혼동'),
'interaction':('인물 ID·역할·시선 축·소유','인물별 행동과 반응','화자 혼동, 똑같은 군중 반응, 접촉 오류'),
'space':('문·창·가구·통로·스케일','시간·날씨·빛 상태','공간 반전, 랜드마크 이동, 불가능한 동선'),
'lighting':('공간 광원 위치·피부와 제품 기준색','광원 크기·강도 관계·색 의도','역방향 광원 이동, 그림자 불일치, 과노출'),
'camera':('인물 위치·시선 축·공간 구조','프레이밍·높이·초점 우선','필수 행동 잘림, 축 혼란, 원근으로 얼굴 변형'),
'camera-motion':('인물 동선·공간 축·필수 공개','카메라 경로·계기·감속·정착','순간이동, 컷과 원테이크 혼동, 지원 제어 과장'),
'look':('정체성·제품 고유색·장면 구조','팔레트·선·질감·대비','룩으로 형태·사실 변경, 컷마다 다른 재질'),
'motion':('물체 수량·형태·접촉·중력 기준','타이밍·변형·보조 움직임','발 미끄러짐, 접촉 없는 힘 전달, 무게 소실'),
'voice':('고정 음색·발음·문장 끝·기본 리듬','성량·속도·쉼의 허용 범위','감정마다 다른 음색, 샘플 없는 실제 보이스 선택 주장'),
'speech':('정확한 대사·화자·고정 음색','의도·서브텍스트·강세·쉼·호흡·속도','청자의 잘못된 립싱크, 미지원 제어를 적용됐다고 표시'),
'sound':('발화 원문·소리 출처·타이밍','편곡 밀도·거리·음량·잔향','대사 마스킹, 접촉과 효과음 시점 불일치'),
'story':('승인 이야기·사실·인물 목표','구조·비트·정보 공개 순서','페이지 맞추기용 씬 증식, 임의 사건 추가'),
'edit':('행동 단계·발화·소품 상태','컷 위치·길이·전환','연속성 파괴, 반응 삭제, 핸들과 최종 길이 혼동'),
'delivery':('승인 마스터·정확한 문구·목적지 조건','화면비·자막·출력 변형','원본 해상도 과장, 글자 잘림, 버전 혼동'),
'brief':('사용자 요청·브랜드·제품 사실','위임된 콘셉트 선택','범위 확대, 미정 값을 승인으로 취급'),
'ops':('파일 계보·정본·실제 사용량','일정·담당·진행 상태','이중 정본, 미실행 작업 완료 표시'),
'evidence':('원본 위치·사실 상태·사용 범위','확인 범위와 불확실성 기록','공개 자료를 재배포 허락으로 오인'),
'handoff':('핵심 사건·정체성·대사·끝 상태','지원 확인된 제어와 제출 형식','요약 중 누락, 생성 모드 오표기'),
'qa':('검수 기준·실제 파일·입력 버전','오류별 최소 수정','일부 검사를 전수 검수로 확대')}

def diagram(eid,cat,title,index):
 W,H=720,460;esc=html.escape
 head=f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="460" viewBox="0 0 720 460"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#9b765a"/></marker><clipPath id="frame"><rect x="215" y="93" width="290" height="270" rx="4"/></clipPath></defs><rect width="720" height="460" fill="#f7f5f0"/><text x="28" y="36" fill="#514b60" font-family="sans-serif" font-size="17">{esc(title)}</text><text x="28" y="60" fill="#968b9e" font-family="sans-serif" font-size="10">FRAME DB / TECHNICAL REFERENCE / DESIGN EXAMPLE</text>'
 foot='<text x="28" y="412" fill="#81738d" font-family="sans-serif" font-size="11">개념 도식 · 실측값이나 실제 촬영 결과가 아닙니다.</text><text x="28" y="435" fill="#a296ac" font-family="sans-serif" font-size="10">선택한 인물·공간·도구에 맞춰 실제 결과를 확인하세요.</text></svg>'
 if cat=='lighting':
  angle=(-45 if '좌측' in title or '창' in title else 45 if '우측' in title else 180 if '역광' in title or '백라이트' in title else 0)
  if '90도' in title:angle=-90 if '좌측' in title else 90
  if '후방' in title:angle=-135 if '좌측' in title else 135
  r=125;x=360+math.sin(math.radians(angle))*r;y=220+math.cos(math.radians(angle))*r
  if '양측' in title:lights=[(220,220),(500,220)]
  else:lights=[(x,y)]
  body='<rect x="148" y="90" width="424" height="290" rx="8" fill="#fff" stroke="#ded8e5"/><circle cx="360" cy="220" r="28" fill="#dfd5e8" stroke="#8e7a9f"/><path d="M348 235L360 247L372 235" fill="none" stroke="#8e7a9f"/><text x="401" y="224" font-size="11" fill="#8e7a9f" font-family="sans-serif">SUBJECT</text><path d="M348 352H372V370H348ZM372 358L382 352V370L372 364" fill="#81718f"/><text x="318" y="391" fill="#81718f" font-family="sans-serif" font-size="10">CAMERA / FRONT</text>'
  body+='<text x="165" y="112" font-size="10" fill="#9a84aa" font-family="sans-serif">TOP VIEW / HEIGHT &amp; EXPOSURE: SET SEPARATELY</text>'
  for lx,ly in lights:
   body+=f'<path d="M{lx:.1f} {ly:.1f}L337 203L383 203Z" fill="#efd8bd" opacity=".4"/><path d="M{lx:.1f} {ly:.1f}L360 220" stroke="#b28b63" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#arrow)"/><rect x="{lx-23:.1f}" y="{ly-11:.1f}" width="46" height="22" rx="3" fill="#e9d2b6" stroke="#b28b63"/><text x="{lx-10:.1f}" y="{ly+4:.1f}" font-size="9" fill="#8e6e4c" font-family="sans-serif">KEY</text>'
  if any(z in title for z in ['반사판','클램셸']):body+='<path d="M470 278L502 238" stroke="#a5bca9" stroke-width="8"/><text x="490" y="294" font-size="10" fill="#7b9e83" font-family="sans-serif">REFLECTOR</text>'
  if '네거티브' in title:body+='<rect x="490" y="180" width="12" height="95" fill="#514b60"/><text x="507" y="228" font-size="9" fill="#514b60" font-family="sans-serif">NEG FILL</text>'
 elif cat=='camera':
  # A neutral framing diagram, not a portrait or a projection simulation.
  scales={'전신':.75,'무릎':.9,'허리':1.12,'흉상':1.5,'얼굴':2.0,'눈의':5.0,'와이드':.65};scale=next((v for k,v in scales.items() if k in title),1.0)
  dx=-60 if '삼분할' in title or '여백' in title else 0
  figure='<circle cx="360" cy="168" r="28" fill="#cabcd4"/><circle cx="350" cy="164" r="2" fill="#8e759e"/><circle cx="370" cy="164" r="2" fill="#8e759e"/><path d="M352 181Q360 185 368 181" fill="none" stroke="#9d83ac"/><path d="M332 199Q360 189 388 199L407 277H313Z" fill="#b5a5c3"/><path d="M335 271L327 360M385 271L393 360M334 207L298 274M387 207L422 274" stroke="#b5a5c3" stroke-width="18" stroke-linecap="round"/>'
  ty=215-164*scale if '눈의' in title else 115*(1-scale)
  body='<rect x="215" y="93" width="290" height="270" fill="#fff" stroke="#9e8bac" stroke-width="2"/><g clip-path="url(#frame)"><g transform="translate('+str(360*(1-scale)+dx)+' '+str(ty)+') scale('+str(scale)+')">'+figure+'</g></g><path d="M312 93V363M408 93V363M215 183H505M215 273H505" stroke="#cfc4d9" stroke-dasharray="4 5"/><path d="M344 219H376M360 203V235" stroke="#947aa6"/><text x="530" y="131" fill="#9a84aa" font-family="sans-serif" font-size="10">FRAME</text><text x="530" y="151" fill="#9a84aa" font-family="sans-serif" font-size="10">EYELINE</text><text x="530" y="171" fill="#9a84aa" font-family="sans-serif" font-size="10">HEADROOM</text>'
  if '탑뷰' in title:
   body='<rect x="215" y="93" width="290" height="270" fill="#fff" stroke="#9e8bac" stroke-width="2"/><rect x="242" y="127" width="236" height="200" rx="12" fill="#e2d8c9"/><circle cx="315" cy="188" r="24" fill="#f9f5ed" stroke="#b79f80"/><rect x="380" y="182" width="45" height="85" rx="5" fill="#cdbbd9"/><path d="M285 340L315 265M435 340L405 285" stroke="#c1a9b5" stroke-width="17" stroke-linecap="round"/><text x="530" y="150" font-size="10" fill="#9a84aa" font-family="sans-serif">TOP VIEW</text>'
  elif '손과 제품' in title or '주관' in title:
   body='<rect x="215" y="93" width="290" height="270" fill="#fff" stroke="#9e8bac" stroke-width="2"/><rect x="321" y="151" width="78" height="126" rx="8" fill="#d3c0df" stroke="#a88fba"/><rect x="330" y="173" width="60" height="60" fill="#f8f2fb"/><path d="M275 332L319 247M445 332L402 247" stroke="#c9aeb8" stroke-width="22" stroke-linecap="round"/><text x="530" y="150" font-size="10" fill="#9a84aa" font-family="sans-serif">CONTACT / PROP</text>'
  if '어깨 너머' in title:body+='<path d="M218 363V249Q233 215 263 249L292 363Z" fill="#b4a3bd" opacity=".8"/>'
  if '투숏' in title or '2인' in title:body+='<circle cx="445" cy="175" r="22" fill="#d8c7ba"/><path d="M423 200H467L478 280H410Z" fill="#c4b19e"/>'
 elif cat=='camera-motion':
  path='M360 350L360 270'
  if '풀아웃' in title:path='M360 270L360 350'
  elif '측면 추적' in title:path='M190 300L510 300'
  elif '앞에서' in title:path='M360 275L360 350'
  elif '뒤에서' in title:path='M360 350L360 275'
  elif '팬' in title:path='M285 290Q360 245 440 290'
  elif '틸트업' in title:path='M310 300Q275 245 310 190'
  elif '틸트다운' in title:path='M310 190Q275 245 310 300'
  elif '좌측 트럭' in title:path='M510 300L190 300'
  elif '리빌' in title:path='M190 300L510 300'
  elif '오비트' in title:path='M210 300Q150 100 360 105Q560 110 515 300'
  elif '크레인업' in title:path='M220 325L220 150'
  elif '핸드헬드' in title:path='M260 300L274 297L280 306L296 300L312 303L325 299'
  elif '뒤늦게' in title:path='M190 300L510 300'
  elif '랙포커스' in title:path='M360 280L360 170'
  elif '줌과' in title:path='M360 350L360 270'
  body='<rect x="135" y="91" width="450" height="285" rx="7" fill="#fff" stroke="#ded6e6"/><circle cx="360" cy="200" r="30" fill="#d7c7e1" stroke="#9a7faa"/><text x="340" y="204" fill="#8d729e" font-family="sans-serif" font-size="9">SUBJECT</text><path d="'+path+'" stroke="#9b765a" stroke-width="3" fill="none" marker-end="url(#arrow)"/><text x="159" y="118" font-size="10" fill="#9b765a" font-family="sans-serif">PLANNED CAMERA PATH</text><text x="159" y="357" font-size="10" fill="#9d8aa8" font-family="sans-serif">START → MOVE → DECELERATE → SETTLE</text>'
 else:return None
 dest=ROOT/'public/references/diagrams'/f'{eid}.svg';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(head+body+foot);return '/references/diagrams/'+dest.name

def apply(entries,variants,assets,prompts,add,rels):
 pack=ROOT/'data/content-packs/production-craft.txt';records=[]
 for line in pack.read_text().splitlines():
  if not line or line.startswith('#'):continue
  cat,title,subtype,gender,desc=line.split('|');records.append((cat,title,subtype,gender,desc))
 for idx,(cat,title,subtype,gender,desc) in enumerate(records):
  key=hashlib.sha256((cat+'|'+title).encode()).hexdigest()[:12];eid='CRAFT-'+cat+'-'+key;preserve,variable,errors=RULES[cat];path,slots=TEMPLATES[cat]
  details={'자료 유형':'직접 작성한 제작 가이드','설계 지시':desc,'적용 범위':subtype,'보존할 요소':preserve,'변경 가능한 요소':variable,'오류 포인트':errors,'검수 기준':['입력의 고정 요소와 충돌하지 않는지 확인','핵심 행동·정보가 결과에서 읽히는지 확인','실제 파일 생성·시각/청각 검수는 별도 기록'],'스킬 연결 슬롯':slots,'근거 구분':'콘텐츠 제작 스킬의 구조를 참고해 작성한 창작·실무 지침. 원문 사례의 관찰·측정값이 아님.','미디어 상태':'실사 이미지·음성 샘플 미확보'}
  if cat=='voice':details.update({'voice_identity_direction':desc,'speech_style':'음색 정체성과 별도로 관계·격식·문장 길이를 선택한다. 성격 유형에서 음색을 자동 유도하지 않는다.','performance_cue':'정확한 대사별 의도·서브텍스트·압력·강세·쉼·호흡·속도를 별도 기록한다.','실제 voice ID':'미선정','실제 모델·설정':'미확인','음성 샘플':'미생성','청취 검수':'미실행'})
  if cat=='speech':
   line=re.search('“([^”]+)”',desc);stress=re.findall('‘([^’]+)’',desc)
   details['performance_cue']={'exact_text':line.group(1) if line else '이 항목은 전달·검수 절차이며 발화문은 별도 공급','intent':desc.split('의도는 ')[1].split('다.')[0]+'다.' if '의도는 ' in desc else '항목에 명시된 발화·반응 기능을 보존','subtext':desc.split('숨긴 뜻은 ')[1].split('다.')[0]+'다.' if '숨긴 뜻은 ' in desc else '추가 숨긴 뜻 없음; 실제 이야기에서 공급되면 적용','pressure':'항목의 관계와 의도에 맞게 절제; 성량과 별개','stressed_words':stress or ['특별한 추가 강세 없음'],'pause':'위 설계 지시의 쉼을 따름; 미지정 구간은 자연스러운 문장 경계','breath':'위 설계 지시의 호흡을 따름; 미지정이면 자연 호흡','pace':'위 설계 지시의 속도를 따름; 미지정이면 보통 대화 속도'}
  if cat in ('acting','interaction','props','pose','motion'):details['상태와 인계']={'초기':'핵심 접촉·소유·자세를 행동 전에 기록','변화':desc,'종료':'완료된 접촉·소유·위치를 다음 컷에 유지','시간 기준':'장면별 shot-local seconds 또는 frames+FPS; 여기서는 실측 시간 미지정'}
  if cat=='lighting':details['조명 설계 슬롯']={'광원 동기':subtype,'방향/높이':desc,'경도/확산':'선택한 광원 크기와 확산 상태를 실제 장면에서 조정','색 의도':'피부·제품 기준색과 구분','키/필 관계':'실제 장면에서 선택; 미측정','배경 분리':'인물/제품과 배경의 명도·윤곽 구분','그림자 규칙':'세계 기준 광원 위치 보존','노출 상태':'설계 제안; 실측 아님','매칭 주의':errors}
  if cat in ('camera','camera-motion'):details['샷 인계 슬롯']={'크기/카메라 위치':title,'인물 블로킹':'카메라 동작과 별도로 지정','시선/축':'기존 공간과 인물 축 유지','공개 정보':desc,'종료 프레임':'중요 행동·정보를 읽을 수 있는 구도','핸들':'실제 생성·편집 계획에서 별도 지정','도구 제어 등급':'UNVERIFIED; 개념 설계가 실제 제어 지원을 뜻하지 않음'}
  prompt=f'[제작 방향]\n{title}\n{desc}\n\n[보존]\n{preserve}\n\n[변경 범위]\n{variable}\n\n[피할 오류]\n{errors}\n\n[검수]\n고정 요소와 실제 결과를 대조한다. 이 지침은 설계 제안이며 미디어 생성·측정·검수 완료를 뜻하지 않는다.'
  e=dict(id=eid,category_id=cat,source_id='studio',title=title,original_title='',description=desc,gender=gender,subtype=subtype,status='guide',details=json.dumps(details,ensure_ascii=False))
  add(e,prompt,[title,subtype,gender,'제작 가이드',*slots,preserve,variable]);entries[-1]['search_text']+=' '+json.dumps(details,ensure_ascii=False).lower()
  image=diagram(eid,cat,title,idx)
  if image:
   details['미디어 상태']='자체 제작한 기술 개념 도식. 실제 인물 사진·촬영 결과가 아님.';entries[-1]['details']=json.dumps(details,ensure_ascii=False)
   vid='v-'+eid;variants.append(dict(id=vid,entry_id=eid,label='기술 개념 도식',angle=None,attributes=json.dumps({'type':'technical_diagram','observed':False},ensure_ascii=False)));assets.append(dict(id='m-'+eid,entry_id=eid,variant_id=vid,kind='image',url=image,availability='owned_diagram',source_id='studio',original_id=eid))
 # Explicit cross-domain associations via craft role, not fabricated visual similarity.
 bycat={}
 for e in entries:bycat.setdefault(e['category_id'],[]).append(e)
 edges={'hair':['anatomy','makeup'],'pose':['gesture','acting'],'costume':['fashion-items','hair'],'expression':['acting','speech'],'gesture':['props','pose'],'props':['gesture','interaction'],'voice':['speech','persona'],'speech':['voice','interaction'],'lighting':['space','camera'],'camera':['lighting','camera-motion'],'camera-motion':['camera','handoff'],'look':['lighting','delivery'],'motion':['qa','acting'],'story':['brief','edit'],'edit':['sound','delivery'],'brief':['story','evidence'],'ops':['handoff','qa'],'evidence':['brief','qa'],'handoff':['ops','camera-motion'],'qa':['ops','delivery']}
 for e in entries:
  if not e['id'].startswith('CRAFT-'):continue
  for target in edges.get(e['category_id'],[]):
   targetentry=next((x for x in bycat.get(target,[]) if x['id'].startswith('CRAFT-')),None)
   if targetentry:rels.append(dict(id='r-craft-'+e['id']+'-'+target,from_id=e['id'],to_id=targetentry['id'],type='workflow_related',reason='제작 과정에서 함께 결정할 분야의 대표 지침. 자동 시각 유사도나 특정 장면의 검증된 호환을 뜻하지 않음.'))
 return len(records)
