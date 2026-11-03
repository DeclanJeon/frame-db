# FRAME_DB 웹 기반 DB 확장을 위한 1차 출처 조사

조사 기준일: **2026-10-29**

## 1. 결론과 조사 범위

`data/database-seed.json`의 **29개 category ID 전부**에 구체적인 공식·제작사·교육기관·원연구자 출처를 연결했다. 이는 **출처 후보 29/29 확보**이며, 미디어 확보·권리 승인·DB 적재·전수 검수가 완료되었다는 뜻은 아니다. 이번 조사에서 미디어 파일을 수집하거나 생성하지 않았고, 재생·청취·수치 측정도 수행하지 않았다.

도메인은 `docs/REFERENCE_DB_EXPANSION_PLAN.md`를 기준으로 읽었다. FRAME_DB는 제작 요소를 분리해 비교하는 레퍼런스 DB이므로, 개념 설명과 실제 촬영·연기·소리 사례를 구별해야 한다. 기존 얼굴 없는 포즈·의상 자료에서 헤어나 메이크업을 추론하지 않는다. 완료된 Drive 이전은 이번 조사 대상이 아니다.

아래 표의 필드는 **향후 수집할 정보의 제안**이다. 출처에 해당 값이 실제로 기재되어 있을 때만 출처 사실로 옮기고, 영상 분석이나 측정이 필요한 값은 빈 상태로 남긴다. 현재 스키마의 구현 상태나 변경 요구를 뜻하지 않는다.

### 증거와 권리 상태를 읽는 방법

| 구분 | 의미 |
| --- | --- |
| **출처 설명** | 저자·제작사·연구자가 기재한 설명, 라벨, 촬영 조건. 출처의 주장으로 귀속한다. |
| **직접 관찰** | 수집자가 실제 이미지·영상·음원을 보고 들은 내용. 파일·구간·검사자를 남겨야 한다. 이번 조사에는 없음. |
| **측정** | 방법·도구·단위·구간을 갖춘 측정값. 원문 숫자를 옮기는 것은 수집자의 측정이 아니라 출처 설명이다. 이번 조사에는 없음. |
| **창작 지시 제안** | 향후 연출·제작을 위한 지시. 출처가 보장한 효과나 실제 사례의 관찰값과 합치지 않는다. |
| **텍스트 근거만** | 짧은 사실 요약과 원문 링크를 사용하는 수집 경로. 원문 전체·번역문 전체·프롬프트·도표의 복제 허가를 의미하지 않는다. |
| **조건부 재사용 근거 확인** | 소유자·배포자가 명시한 허락이 있으나, 대상 파일·조건·제외 권리의 확인이 남는다. FRAME_DB 공개 사용이 자동 승인된 것은 아니다. |
| **미확인** | 미디어 복제·편집·재배포의 근거를 확인하지 못함. 허용으로 해석하지 않고 링크와 사실 요약 단계에 둔다. |

페이지 본문·데이터셋 설명·라이선스 메타데이터를 확인했다. 검색 결과에만 나타난 정보, 접근이 막힌 정보, 내용이 충돌하는 정보는 뒤의 접근 기록과 제약에 따로 표시했다. 이미지 대체텍스트나 영상 소개를 실제 영상 시청으로 계산하지 않는다.

## 2. 전체 29개 분류 매트릭스

각 행의 URL은 검색어가 아니라 해당 기관의 구체적인 자료 주소다. `R1`~`R9`는 3절의 권리 원문 주소를 가리킨다. “지원 범위”는 해당 분류 전체를 채운다는 뜻이 아니라, 이 출처로 근거를 붙일 수 있는 부분이다.

| ID / 분류 | 확인한 1차 출처와 실제 항목·사례 | 지원 범위 / 제안 필드 | 매체 | 증거 상태 / 텍스트 인용·미디어 재사용 |
| --- | --- | --- | --- | --- |
| `pose` / 포즈·자세 | **CMU Graphics Lab**, [걷기 검색 결과](http://mocap.cs.cmu.edu/search.php?maincat=3&subcat=2). Subject 7 Trial 4는 slow walk, Trial 12는 brisk walk로 기재된다. | subject/trial ID, 동작 라벨, 자세·이동 계열. 지지발·관절각·속도는 데이터 검토 전 미확인. 정지 포즈는 이후 특정 프레임과 연결하는 방식 제안. | 모션캡처 데이터; 설명 텍스트 | 출처 라벨 확인, 데이터 미측정. **조건부 재사용 근거 확인(R1)**. 데이터의 상업 제품 포함은 허용하지만 직접 재판매는 금지. DB 원자료 재배포와 동영상 권리는 별도 확인. |
| `costume` / 의상·코디 | **The Met**, [Round gown, 1979.20a–e, g](https://www.metmuseum.org/art/collection/search/81127). 약 1795년 이탈리아 복식, silk·linen 기재. | 소장번호, 연대, 문화권, 재료, 의복 구성. 계절 코디·현대 착용감·정확한 핏은 이 기록만으로 확정 불가. | 소장품 사진·카탈로그 | 메타데이터와 Public Domain 표시 확인. **표시된 공개 이미지 재사용 근거 확인(R2)**. 설명 에세이 전체에는 CC0를 확장하지 않는다. |
| `hair` / 헤어스타일 | **WorldSkills UK**, [Hairdressing Technical Handbook 2021](https://www.worldskillsuk.org/wp-content/uploads/2021/03/Hairdressing-Technical-Handbook-2021.pdf). 인쇄 p.10~12의 다운스타일·업스타일·테이퍼 과제 및 정면·후면·좌·우 사진 요구. | 커트/스타일링 과제명, 업두 여부, 평가 관점, 필요한 시점. 실제 커트 길이·가르마·후면 구조는 별도 사진 검수 필요. | 공식 교육·경기 지침 PDF, 도해·사진 | 문서 내용 확인. **텍스트 근거만 / 이미지·PDF 재배포 권리 미확인**. 과제 규격은 공개 스타일 사진 세트의 확보를 뜻하지 않는다. |
| `makeup` / 메이크업·그루밍 | **M·A·C Cosmetics**, [Instant Artistry: Winged Liner](https://www.maccosmetics.com.au/artistry-mac-how-to-video-winged-liner). Fabiana Gomes의 윙드 라이너 교육 영상, 페이지 표시 길이 1:15. | 적용 영역=눈, 기법명, 강사, 도구, 원문 영상 링크. 라인 각도·두께·마무리와 적용 전후 차이는 시청·비교 전 미확인. 수염·네일은 미포함. | 공식 튜토리얼 영상·소개 텍스트 | 제목·소개·길이 표시 확인, 영상 미시청. **텍스트 근거만 / 영상·썸네일 복제 권리 미확인**. 모델 얼굴·화장 전후 조건은 별도 확보. |
| `expression` / 표정·시선 | **Livingstone·Russo 원배포 기록**, [RAVDESS v1.0.0](https://zenodo.org/records/1188976). 배우·감정·보통/강한 강도·반복·모달리티를 구분하는 파일 식별 체계. | actor ID, 감정 라벨, 강도, 대사 ID, 반복, AV/영상/음성 구분. 감정 라벨은 연기 조건이며 실제 내면 감정의 증명이 아님. 시선 방향은 별도 관찰. | 배우 연기 영상·음성·메타데이터 | 원배포 설명 확인. **비상업 조건부 재사용(R3)**. FRAME_DB 상업 공개 사용은 미확정. 눈·입 움직임, 응시 좌표는 미관찰. |
| `gesture` / 손동작·제스처 | **UPF M3D 연구팀**, [Identifying Gesture Referentiality](https://m3d.upf.edu/challenges/identifying-referentiality). emblem, iconicity, metaphoricity, deixis 및 중첩 주석 설명. | 형태와 의미의 분리, 발화 문맥, 문화권, stroke 구간, 복수 의미 라벨. 모든 손동작을 보편적 기호로 취급하지 않는 근거. | 연구팀 교육 텍스트·영상·주석 예제 | 본문·전사 확인. **텍스트 근거만 / 예제 영상 재사용 미확인(R4)**. TED가 M3D에 준 사용 허락은 FRAME_DB 허락이 아니다. |
| `anatomy` / 얼굴·체형·실루엣 | **Rice University OpenStax**, [Anatomical Terminology, §1.6](https://openstax.org/books/anatomy-and-physiology-2e/pages/1-6-anatomical-terminology). 해부학적 자세, 신체 부위, 방향 및 평면. | 기준 좌우, 전/후, 근위/원위, 부위명, 표준 자세 용어. 개인 얼굴 비율·정체성 앵커·체형 분포는 이 교과서로 채울 수 없음. | 교육 텍스트·해부 도식 | 원문 확인. **비상업 조건부 재사용(R5)**. 상업 DB용 도식 권리 미확정; 도식별 별도 크레딧도 확인해야 함. |
| `fashion-items` / 패션 아이템 | **The Met**, [Shoes, 26.56.70](https://www.metmuseum.org/art/collection/search/98398). 19세기 초 이탈리아 가죽 신발. | 아이템 종류, 소장번호, 연대, 문화권, 재료. 브랜드·사이즈·착화감은 기록 없으면 미확인. 현대 액세서리 전반은 추가 출처 필요. | 소장품 사진·카탈로그 | 메타데이터와 Public Domain 표시 확인. **표시된 공개 이미지 재사용 근거 확인(R2)**. 다른 소장품으로 일괄 확대 금지. |
| `props` / 소품·제품 상호작용 | **CMU-MMAC 연구팀**, [Quality of Life Grand Challenge / Kitchen Capture](http://kitchen.cs.cmu.edu/). 샐러드 조리의 여러 센서 시연 및 스크램블에그 모션 시연을 소개한다. | 조리 과제, 식재료/도구, 행동 단계, 접촉 구간, 센서 종류·정렬 상태. 홈페이지의 자료 소개는 확인했지만 손-물체 접촉 정밀도는 미검사. | 다중 시점 영상·음성·모션·센서 데이터 | 실제 연구 수집 설명 확인. **텍스트 근거만 / MMAC 파일 재사용 권리 미확인**. 다른 CMU mocap DB의 R1 조건을 자동 적용하지 않는다. |
| `persona` / 캐릭터·페르소나 | **Pixar × Khan Academy**, [Character arc 실습](https://www.khanacademy.org/computing/pixar/storytelling/character/a/exercise-4), [공식 단원](https://www.khanacademy.org/computing/pixar/storytelling). 욕구·필요·장애물·변화의 구분. | 시작 욕구, 마지막에 깨닫는 필요, 장애물과 변화. 조건부 행동 규칙·말투는 이 틀을 활용한 자체 설계로 표시; 실제 인물 성격 진단 아님. | 교육 텍스트·영상 | **공식 페이지의 검색 색인으로 설명·실습 확인; 직접 열기는 차단**. 텍스트 근거 후보 / Pixar 영상·캐릭터 이미지 재사용 미확인. 수업 접근 가능성을 복제 허락으로 보지 않음. |
| `acting` / 행동·연기·블로킹 | **NYFA, Peter D. Marshall**, [The 5 Stages of Blocking a Scene](https://www.nyfa.edu/film-school-blog/the-5-stages-of-blocking-a-scene/). 블로킹→조명→리허설→조정→촬영. | 배우 위치, 첫 카메라 위치, 리허설·조정 단계, 샷리스트와 동선의 관계. 행동 전환 시점·연기 효과는 실제 테이크 검수 필요. | 교육 기사·사진 | 저자 명시 원문 확인. **텍스트 근거만 / 사진·기사 재배포 미확인**. 블로킹 방법의 근거이지 검증된 테이크 묶음은 아님. |
| `interaction` / 2인·그룹 상호작용 | **CMU Graphics Lab**, [two subjects 검색 결과](http://mocap.cs.cmu.edu/search.php?maincat=1&subcat=1). Subject 18/19의 Trial 1은 A/B 악수, Trial 3은 당김/저항 역할로 기재. | 참여자 역할, 대응 trial, 접근→접촉→이탈 구간. A/B를 독립 행동으로 분리하지 않는 연결 제안. 실제 거리·접촉력은 미측정. | 쌍을 이루는 모션 데이터·라벨 | 출처의 A/B 설명 확인. **조건부 재사용(R1)**. 동일인 판단과 손가락 동작에 제한; 그룹 전체 사례는 별도 필요. |
| `space` / 공간·세트·환경 | **Walt Disney Animation Studios**, [Modeling](https://www.disneyanimation.com/process/modeling/). 자연 지형·건축·식생·소품을 환경 모델의 구성으로 설명; Wish 성·나무 모델 예시 표기. | 환경 구성 요소, 컨셉→모델 관계, 부서 인계. 방 크기·실측 배치·날씨·시간은 이미지 소개만으로 확정하지 않음. | 제작 과정 텍스트·모델 이미지 | 제작사 설명·이미지 표제 확인. **텍스트 근거만 / 이미지·모델 파일 재사용 미확인(R6)**. 실측 세트 도면의 대체 자료가 아님. |
| `lighting` / 조명 | **ARRI / Bill Holshevnikoff**, [Lighting Handbook 4판](https://www.arri.com/resource/blob/83996/409091c612f371b0c68b41d9dcb636db/arri-lighting-handbook-english-data.pdf). 인쇄 p.7~17의 hard/soft, key/fill/separation/background와 그림자 설명. | 광질, 광원 역할, 방향·대비 설명, 사례 출처 쪽수. 실제 lux·색온도·거리·노출은 명시값이 있는 사례만 전사. | 공식 PDF·조명 도식·촬영 예시 | 목차·본문·저작권 표기 확인. **텍스트 근거만 / 사진·도식 재사용 미확인(R7)**. 무료 PDF 열람과 복제 허락을 구별. |
| `camera` / 카메라·구도 | **Nikon**, [Understanding Focal Length](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/understanding-focal-length?generate=pdf). 초점거리·화각·배율 및 FX/DX 예시. | 초점거리 mm, 센서 포맷, 화각 설명, 렌즈 종류. 이미지 외관만으로 렌즈·카메라 거리·센서를 역산하지 않는 기록 제안. | 제조사 교육 텍스트·도표·영상 소개 | 제조사 원문 확인. **텍스트 근거만 / 도표·영상 재사용 미확인**. 특정 초점거리의 감정 효과를 물리 측정값으로 쓰지 않음. |
| `camera-motion` / 카메라 이동 | **Columbia University**, [Camera Movement](https://filmglossary.ccnmtl.columbia.edu/term/camera-movement/); **Film Education**, [Terminology](https://www.filmeducation.org/resources/primary/teaching_with_film/film_in_the_classroom/terminology/). 고정축 pan/tilt와 tracking 구분; Columbia는 Goodfellas의 Copacabana 사례를 연결. | 이동 유형, 피사체 추종, 시작/종료 프레이밍, 원작·클립 식별. 정확한 3D 경로·렌즈·속도는 별도 자료나 측정 없이는 미확인. | 교육 텍스트·영화 클립·음성 해설 | 정의·작품/배급 출처 표기 확인, 클립 미시청. **텍스트 근거만 / 영화 클립 재사용 불성립(R8)**. 화면 운동 관찰과 실제 카메라 이동 추론을 분리. |
| `look` / 비주얼 스타일·색·재질 | **Walt Disney Animation Studios**, [Look Development](https://www.disneyanimation.com/process/look-development/). Raya 모자 재질 분해와 Mattias의 model/displacement/color/reflectance 단계 소개. | 색·텍스처·재질, 단계별 입력/결과, 모델과 표면의 관계. 픽셀 RGB를 실물 색이나 조명 독립 재질값으로 취급하지 않음. | 제작 과정·분해 이미지 | 제작사 설명과 단계 표제 확인. **텍스트 근거만 / 분해 이미지 재사용 미확인(R6)**. PBR 파라미터 실측 자료는 아님. |
| `motion` / 모션·물리·VFX | **Walt Disney Animation Studios**, [Animation](https://disneyanimation.com/process/animation/). timing, anticipation, squash/stretch, follow-through, secondary action을 제작 원리로 명시. | 원리명, 선행 동작/후속 동작, 무게 표현, 검수할 시간 구간. 충돌·중력·유체의 수치적 정확성이나 특정 VFX 구현은 별도 근거 필요. | 제작 원리 텍스트·페이지 내 시연 영역 | 텍스트 확인, 시연 미재생. **텍스트 근거만 / 시연 재사용 미확인(R6)**. 스타일화된 표현을 물리 시뮬레이션 검증으로 세지 않음. |
| `voice` / 목소리 정체성 | **University of Edinburgh CSTR**, [VCTK v0.92 원배포 메타데이터](https://datashare.ed.ac.uk/items/30e7453c-9ea8-48b4-8e18-f96d0dc62928/full). 영어 다화자 녹음과 동일 녹음 환경, 마이크 조건 설명. | speaker ID, 언어·억양, 마이크, 녹음/배포 포맷, 대사 연결. 고정 음색·공명·F0는 실제 청취·분석 후 별도 기록. | 음성·전사·녹음 조건 | **CC BY 4.0 배포 근거 확인(R9)**. 화자 사칭·보증·개별 초상/인격 관련 허락으로 확대하지 않음. 한국어·영상 얼굴 연결은 미지원. |
| `speech` / 말투·대사 연기·립싱크 | **Livingstone·Russo**, [RAVDESS v1.0.0](https://zenodo.org/records/1188976). 동일 대사 조건과 감정 강도·반복, 음성/영상 모달리티 비교 구조. | 대사 ID, 배우 ID, 감정·강도·반복, 음성/입 움직임 대응 구간. 강세·쉼·음소/viseme 타이밍은 별도 주석 필요. | AV·무음 영상·음성 | 출처 조건 확인, 정렬 미검사. **비상업 조건부 재사용(R3)**. 검증된 립싱크 주석 데이터라고 부르지 않음. |
| `sound` / 음악·환경음·효과음 | **BBC**, [Sound Effects Archive](https://sound-effects.bbcrewind.co.uk/), [Licensing](https://sound-effects.bbcrewind.co.uk/licensing). 자연·교통·발소리·군중 등 효과음 분류. | 음원 ID·설명·원문 링크, 환경/효과음 계열, 메타데이터의 출처와 라이선스. 실제 음색·길이·루프·음량은 청취·측정 전 미확인. | 효과음·환경음·메타데이터 | **메타데이터 OGL v3 / 음원은 용도 제한**. 업무·상업·AI/데이터 분석 등은 별도 허락 요구. 이번에는 텍스트 근거만; 음악 라이브러리의 재사용 근거로 확대 금지. |
| `story` / 이야기·대본·장르 | **Walt Disney Animation Studios**, [Story](https://www.disneyanimation.com/process/story/). 대본 썸네일→정제 보드 과정과 Once Upon A Snowman 보드 사례. | 대본/보드 관계, 내러티브·감정·타이밍·스테이징·프레이밍의 검토 관점. 비트·장면 목적은 수집자의 분석임을 표시. | 제작 설명·스토리보드 이미지 | 제작사 원문 확인. **텍스트 근거만 / 대본·보드·캐릭터 이미지 재사용 미확인(R6)**. 장르별 완결 대본 확보는 아님. |
| `edit` / 편집·리듬·전환 | **Columbia University**, [Editing](https://filmglossary.ccnmtl.columbia.edu/term/editing/). continuity, montage, jump cut 설명과 The Third Man의 Funeral 사례. | 기법명, 작품·클립 출처, 컷 연결 관계. 컷 수·샷 길이·리듬 수치는 실제 구간 분석 후 측정값으로 기록. | 교육 텍스트·영화 클립·해설 | 교육 설명·사례 정보 확인. **텍스트 근거만 / 영화·해설 파일 재사용 불성립(R8)**. 수업 이용 범위를 상업 DB로 확대하지 않음. |
| `delivery` / 피니싱·자막·납품 | **Netflix Partner Help Center**, [English (USA) Timed Text Style Guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide). 미국 영어 자막의 행 길이·행 수·화자/효과음 표기 지침. | 납품처, 언어, SDH/번역 자막 구분, 적용 절·개정일, 문자수 규칙. 한국어·그레이드·전체 마스터 규격은 별도 문서 필요. | 공식 규격 텍스트·짧은 예시 | 공개 원문 확인. **텍스트 근거만 / 문서·예시 일괄 재배포 미확인**. Netflix 전용 규칙을 모든 플랫폼의 표준으로 쓰지 않음. |
| `brief` / 브리프·브랜드·기획 | **Radio Advertising Bureau**, [Sample Creative Brief](https://www.rab.com/academylms/content/handouts/CreativeBriefTemplate.pdf). 목표·관객·브랜드 메시지·근거·성공지표·필수요소·납품/일정 항목. | 목적, 대상 관객, 단일 메시지, 주장 근거, KPI, 필수 문구, 결과물과 일정. 채운 값은 프로젝트별 기획 제안이며 사실 보증 아님. | 공식 교육용 1쪽 템플릿 | 항목 확인. **텍스트 근거만 / PDF·문구 전체 복제 권리 미확인**. 자체 브리프 구조 설계에 활용하되 양식을 통째로 복제하지 않음. |
| `ops` / 제작운영·에셋관리 | **Disney Animation**, [Production Management](https://www.disneyanimation.com/process/production-management/); **W3C**, [PROV Model Primer](https://www.w3.org/TR/prov-primer/). 일정·부서 조율 및 entity/activity/agent의 계보 표현. | 일정·마일스톤·담당 역할, 입력→작업→파생본 관계, 생성·사용 시점. 실제 예산·승인·파일 버전 로그는 자체 운영 기록이 필요. | 제작 설명·계보 명세/예제 | 원문 확인. **텍스트 근거만**. Disney 추적 화면 재사용 미확인(R6); W3C 예제의 일괄 복제 허가는 이번 조사에서 확정하지 않음. |
| `evidence` / 근거·권리·출처 | **Library of Congress**, [Understanding Copyright](https://www.loc.gov/legal/security-copyright-and-privacy/understanding-copyright/); **Creative Commons**, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en). 항목별 권리 정보·권리자·허락 범위와 표시 조건의 확인 근거. | 원출처·저자·권리자, 라이선스 URL/버전, 대상 파일, 취득일, 허락 범위·증빙. 출처 설명/관찰/측정/제안 분리는 FRAME_DB 기록 제안. | 기관 안내·라이선스 원문 연결 | 원문 확인. **텍스트 근거만 / 안내 페이지의 예시 미디어 권리 미확인**. 열람 가능·출처 표기만으로 재사용이 성립하지 않음. |
| `handoff` / AI 생성·참조 인계 | **Google**, [Video generation in the Gemini API](https://ai.google.dev/gemini-api/docs/video), [공식 SDK 타입 정의](https://github.com/googleapis/python-genai/blob/main/google/genai/types.py). 현재 안내와 참조 역할·입력 필드의 소유자 문서. | 공급자, 문서 확인일, 모델/API 식별자, 참조 역할, 입력/출력 관계. SDK의 필드 존재와 특정 모델의 실제 지원 여부는 별도 확인. | API 설명·코드 정의 | 공식 페이지 확인, Context7로 SDK 교차 확인. **페이지 문서는 예외 제외 CC BY 4.0, 코드 예제 Apache 2.0**(페이지 하단). 예시 미디어·사용자 입력·생성물 재사용은 이 문서 라이선스로 확정 불가. |
| `qa` / 품질·연속성 검수 | **Columbia University**, [180-Degree Rule](https://filmglossary.ccnmtl.columbia.edu/term/180-degree-rule/); **Netflix**, [Timed Text Style Guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide). 인물 배치·시선 연결과 납품 규격 검토의 근거. | 축·화면 좌우·시선 연결, 자막 규칙, 검사 대상/구간·판정·검사자. 축 넘김은 의도된 연출일 수도 있으므로 자동 오류로 단정하지 않음. | 교육 설명·납품 규격 | 방법 근거만 확인. **텍스트 근거만 / 클립·전체 문서 재사용 미확인(R8)**. 실제 FRAME_DB 품질 합격·정체성/접촉/시간 전수 검수 증거는 없음. |

## 3. 권리 원문과 수집을 제한하는 조건

### R1. CMU Graphics Lab: 이용 가능과 수집·재배포 가능은 다르다

원문: <http://mocap.cs.cmu.edu/>

홈페이지는 연구 이용과 상업 판매 제품에 데이터 포함을 허용하지만, 변환본을 포함한 데이터 자체의 직접 재판매는 금지한다. 크롤링을 하지 말라고도 명시한다. 따라서 공개 레퍼런스 DB가 원데이터를 재배포하는 구조는 “상업 제품 포함 가능”이라는 문장만으로 승인된 것으로 처리하지 않는다.

손·발끝 노이즈 경고가 있고, finger/thumb는 실제 캡처하지 않은 편의상 관절이라는 설명이 있다. 손가락 접촉 검증용으로 전용하면 안 된다. subject 번호도 항상 한 사람의 고유 정체성을 뜻하지 않는다. 데이터의 허락을 홈페이지 영상·외부 변환본·별개 MMAC 자료로 확대하지 않는다.

### R2. The Met: 항목별 Public Domain/OA 표시를 유지

정책: <https://www.metmuseum.org/policies/terms-and-conditions>

§3(a)는 Open Access 자료에 CC0와 상업·비상업 사용 범위를 명시한다. 위 두 소장품 기록에는 Public Domain 표시가 있다. 이를 근거로 **해당 표시가 붙은 이미지**를 후속 수집 후보로 둘 수 있다. 전체 웹사이트 사진·에세이·출판물·상표가 공개된다는 뜻은 아니다. 소장번호, 개별 이미지 주소, 표시 확인일과 정책 근거를 함께 남기는 방식 제안이다.

### R3. RAVDESS: 소개 문구보다 구체적 라이선스 기록을 확인

원배포: <https://zenodo.org/records/1188976>  
기계 판독 권리 기록: <https://zenodo.org/api/records/1188976>  
원연구실 상업 사용 안내: <https://smartlaboratory.org/resources/speech-song-database-ravdess/>

설명에는 Creative Commons Attribution이라는 축약 표현이 있지만, 원배포 API의 `metadata.license.id`는 **`cc-by-nc-sa-4.0`**이고, 원연구실도 상업 라이선스를 별도로 안내한다. 축약 문구만 보고 CC BY의 상업 사용 허락으로 읽지 않는다. 무료 다운로드와 상업 공개 DB 재배포는 다르다. 여기서는 비상업·동일조건 배포의 조건부 후보로만 분류한다.

감정·강도 라벨은 배우에게 주어진 연기 조건이다. 같은 라벨이 모든 화자·문화권에서 같은 감정으로 인식된다고 보장하지 않는다. 표정과 말투에 같은 파일을 연결하더라도 신규 파일 확보량을 두 번 세지 않는 방식 제안이다.

### R4. M3D: TED의 프로젝트 한정 허락은 이전되지 않는다

원문: <https://m3d.upf.edu/challenges/identifying-referentiality>

페이지 하단은 TED가 **이 교육 프로그램과 M3D 프로젝트에서** TED Talks 사용을 허락했다고 설명한다. 이는 제3자인 FRAME_DB의 복제·편집·재게시 허락이 아니다. 주석 방법과 원문 링크는 근거로 삼되 예제 영상 수집은 권리 미확인으로 남긴다. 손동작 의미는 문화·발화 문맥에 귀속시킨다.

### R5. OpenStax: 현재 판본의 비상업 조건과 도식별 예외

판본 권리 원문: <https://openstax.org/books/anatomy-and-physiology-2e/pages/preface>

현재 열람한 서문은 **CC BY-NC-SA 4.0**을 명시하고, 상업 주체의 그림 재사용은 OpenStax에 권리·허락을 문의하도록 안내한다. “OpenStax는 오픈 교재”라는 일반 설명으로 상업 이용을 허가 처리하지 않는다.

교차 확인한 [Oregon State University 개작판](https://open.oregonstate.education/anatomy2e/)은 검색 색인에 CC BY/CC BY-SA 문구가 남아 있었지만, 직접 연 본문은 원저작물·이미지에 NC-SA 문구를 표시했다. 서로 다른 시점·판본·개작물의 조건을 합치지 않았다. 위 매트릭스는 Rice/OpenStax의 현재 2판 원문과 서문을 기준으로 한다. 재사용 시 그림별 크레딧과 적용 버전을 다시 확인해야 한다.

### R6. Disney: 제작사 사례는 공개 에셋 라이브러리가 아니다

권리 표시를 확인한 공식 페이지:  
<https://disneyanimation.com/process/animation/>  
<https://www.disneyanimation.com/process/production-management/>

페이지는 Disney Enterprises의 권리 유보를 표시한다. 제작 과정의 출처로는 유용하지만, 모델·스토리보드·캐릭터·분해 이미지·추적 화면의 공개 DB 재사용 허락은 확인하지 못했다. 텍스트를 짧게 요약하고 원문에 연결하는 경로로 제한한다. 페이지에 보이는 예시가 다운로드 가능한 3D 모델이라는 주장도 하지 않는다.

### R7. ARRI: 공식 배포처와 저작권자는 구별

공식 배포: <https://www.arri.com/en/learn/lighting/lighting-handbook>  
권리 표기: 매트릭스의 영문 PDF 인쇄 p.2.

PDF는 이미지·텍스트의 저작권자를 **Bill Holshevnikoff, 2016**으로 기재한다. ARRI가 공식 배포한다는 사실만으로 도식·사진을 재사용 허가하지 않는다. 원저작자의 [무료 자료 안내](https://poweroflighting.com/free-downloads/)도 배포 경로이지 FRAME_DB의 재게시 라이선스 증빙은 아니다. 재사용 범위는 미확인으로 둔다.

### R8. Columbia: 대학 교육 자료와 영화 권리는 별개

원문: <https://filmglossary.ccnmtl.columbia.edu/about/>

Copyrights and Permissions는 교육·학술 목적과 그 밖의 사용에 대한 제한을 명시한다. 또한 개별 용어 페이지는 Warner Home Video, Criterion 등 영화 클립의 별도 출처를 표시한다. 대학이 교육 페이지를 제공한다는 이유로 클립·캡처·음성 해설을 상업 DB에 재배포할 수 있다고 판단하지 않는다. 권리자별 허락을 확보하지 않았으므로 실제 미디어 재사용은 불성립으로 기록한다. 오래된 영화의 제작연도만으로 해당 복원본·배급본·해설까지 공개 영역으로 단정하지 않는다.

### R9. VCTK: 명시된 오픈 라이선스와 남은 범위

원배포 권리 필드: <https://datashare.ed.ac.uk/items/30e7453c-9ea8-48b4-8e18-f96d0dc62928/full>  
라이선스 설명: <https://creativecommons.org/licenses/by/4.0/deed.en>

배포 기록은 **CC BY 4.0**을 명시한다. 해당 라이선스의 조건을 지키는 음성 자료 이용 후보로 둘 수 있다. 출처·라이선스 링크·변경 표시를 유지한다. CC의 설명 자체도 인격·프라이버시 등 다른 권리가 모두 해결되는 것은 아니라고 명시한다.

원배포는 p315의 전사 소실 및 일부 마이크 녹음 문제를 설명한다. 전사·음성이 모두 있다는 전제의 일괄 적재는 피해야 한다. 신문에서 가져온 대사 전체를 별도 텍스트 상품처럼 재배포할 권리까지 확정하지 않는다. 파일 단위 검수·청취와 실제 조건 확인이 남는다.

### BBC: 메타데이터와 오디오를 분리해야 한다

원문: <https://sound-effects.bbcrewind.co.uk/licensing>

§9의 OGL v3 적용은 **메타데이터**에 한정되고 오디오에는 적용되지 않는다. §7~8은 비상업 개인·연구·정규 교육 이용과 업무·상업 등 다른 이용을 구별하며, 후자는 사전 허락이 필요하다고 한다. AI 개발·훈련, 컴퓨터 분석·텍스트/데이터 마이닝도 별도 허락 대상으로 명시한다. 무료 스트리밍이나 다운로드 버튼을 상업 DB·AI 참조 업로드 권리로 바꾸지 않는다. 상업 음원 라이선스 경로가 있다는 사실은 이번 작업의 구매나 허락 완료를 뜻하지 않는다.

## 4. 근거를 DB 정보로 바꿀 때의 경계

다음은 **수집 설계 제안**이며, 이번에 데이터를 수정하거나 검증 흐름을 구현한 것이 아니다.

1. **출처당 사실 카드부터 만든다.** 원문 제목·저자/기관·URL·확인일·적용 절/쪽·원래 라벨을 남긴 뒤 짧은 한국어 요약을 연결한다. 원문 기사·튜토리얼·프롬프트를 통째로 복사하거나 유사 번역본으로 적재하지 않는다.
2. **근거의 주어를 유지한다.** CMU의 slow walk는 출처 라벨, BBC 설명은 아카이브 메타데이터, Netflix 규칙은 특정 납품처 요구다. 세 가지 모두 관찰자가 직접 측정한 보편 사실은 아니다.
3. **관찰과 측정은 다음 작업에서 추가한다.** 예를 들어 “오른손이 컵 손잡이에 닿음”은 실제 구간 관찰, “접촉 0.8초”는 프레임레이트·시작/끝 프레임을 명시한 측정이다. 지금 확인한 출처 목록만으로 이런 값을 채우지 않는다.
4. **연출 결과를 보장하지 않는다.** “저각도라서 강해 보임” 같은 교육적 해석과 “카메라를 아래에 배치하라”는 창작 지시를 분리한다. 창작 지시는 제작 의도이며 실증된 관객 반응으로 표기하지 않는다.
5. **권리는 사용 행위별로 판정한다.** 열람, 링크, 텍스트 요약, 썸네일 복제, 편집, 파일 재배포, 상업 공개, 제3자 AI 업로드는 별개다. 하나의 공개 라이선스나 교육 이용 예외를 나머지 행위에 자동 확장하지 않는다. LOC와 CC의 원문은 이 구별을 위한 출처이며, FRAME_DB의 개별 사용을 승인하는 문서는 아니다.
6. **미디어의 종류를 보존한다.** 모션 데이터는 촬영 영상이 아니고, 조명 도식은 실제 조명 결과가 아니며, 오디오 없는 영상은 음색 근거가 아니다. 카메라 경로는 화면 이동만으로 정확한 3D 측정값을 만들 수 없다.
7. **에셋 계보와 개념 중복을 분리한다.** 같은 RAVDESS 파일을 표정·말투에 연결하거나 같은 소장품의 여러 해상도를 연결해도, 원본 확보 수량을 중복 집계하지 않는 방식을 제안한다.

## 5. 다음 수집에서 가장 큰 공백

| 공백 | 현재 확보한 근거 | 남아 있는 일 |
| --- | --- | --- |
| 헤어·메이크업의 비교 가능 미디어 | 공식 과제 규격·윙드 라이너 교육 | 동일 정체성·고정 조명·정면/측면/후면 또는 적용 전후 자료와 명시적 재배포 권리. 현재 마네킹·크롭 의상에서는 추출 불가. |
| 손·접촉·다인 관계 | M3D 문맥 주석, CMU A/B 라벨, MMAC 조리 수집 | 손가락·가림·도구 상태·실제 접촉의 구간별 검사. CMU mocap의 미캡처 finger/thumb를 접촉 정답으로 쓸 수 없음. |
| 한국어 목소리·연기·립싱크 | 영어 VCTK·RAVDESS | 한국어 화자·대사·발음·입 움직임, 고정 화자 기준과 사용 범위. 시청·청취·음소 정렬은 아직 없음. |
| 실제 이동·VFX·편집 사례 | 공식 원리·교육기관 사례 설명 | 합법적 파일 확보, 타임코드와 재생 검수, 측정 조건. 정지 이미지·도식으로 동작 확보량을 대체할 수 없음. |
| 현대 패션·광범위한 룩 | 공개 영역 역사 복식·신발 | 현대 계절 코디·액세서리·실제 착용 핏. 역사 소장품을 현대 트렌드나 현재 판매 상품처럼 기록하지 않음. |
| 운영·납품·QA의 완결 사례 | RAB 템플릿, W3C 계보, Disney 운영 설명, Netflix 규칙 | 실제 브리프→버전→검사→수정→납품의 연결 기록. 템플릿과 규격 페이지는 완료된 제작·검수 사례가 아님. |
| 상업 공개에 바로 쓸 오픈 미디어 | The Met의 명시된 공개 이미지, VCTK의 배포 라이선스 | 대부분의 교육·제작사 예시는 별도 권리 확인 필요. NC/교육용 조건의 자료를 공개 상업 DB에 일괄 넣지 않음. |

## 6. 접근 확인 기록과 버전 주의

- **CMU**: HTTPS 직접 조회는 인증서/시간 초과 문제가 있었지만 동일 소유자의 HTTP 홈페이지와 두 검색 결과는 직접 열어 확인했다. 미러나 제3자 요약으로 권리 조건을 대신하지 않았다.
- **RAVDESS**: 웹 도구에서는 원배포 본문을 확인했으나 다른 요청 경로에서는 브라우저 검사 화면이 나왔다. 원배포 API는 열렸고 구체적 라이선스 필드를 확인했다. 상업 사용 안내도 원연구실에서 교차 확인했다.
- **BBC**: 검색 도구가 반환한 공식 아카이브·라이선스 본문으로 조건을 확인했다. 별도 직접 fetch에서는 본문을 재확보하지 못했다. 음원별 파일이나 라이선스 증빙을 취득한 것으로 계산하지 않는다.
- **Khan Academy**: 공식 페이지의 검색 색인에서 캐릭터 변화 실습의 욕구·필요·장애물 질문을 확인했다. 직접 fetch는 Client Challenge를 반환했다. 따라서 `persona`는 출처와 공개 색인 확인 수준이며, 전체 수업·영상 직접 검토로 표시하지 않았다.
- **GEMEP / UNIGE**: 공식 검색 결과는 있었지만 직접 열기는 Access Denied였다. 29개 분류를 채우는 필수 출처로 쓰지 않고, 표정·말투는 확인 가능한 RAVDESS 원배포로 연결했다.
- **Netflix QC Knowledge Hub**: 검색 색인은 있었지만 직접 요청은 JavaScript 셸만 반환했다. 실제 QC 본문을 읽었다고 기록하지 않는다. `qa` 행은 직접 확인한 Columbia의 연속성 설명과 공개 자막 지침으로 한정했다.
- **Google 인계 문서**: 직접 연 공식 페이지는 **2026-10-22 갱신**이며 Gemini API의 Veo 3.1 Preview 종료를 안내한다. 해당 날짜 이전 가이드나 Context7의 SDK 예제만으로 현재 모델 가용성을 확정하지 않았다. 이번 조사는 모델 호출·능력 실험을 하지 않았다. SDK에 참조 필드가 존재한다는 사실과, 선택한 모델/API가 그 조합을 실제 지원한다는 사실은 별개다.
- **권리 미확인 자료**: MAC·WorldSkills·Nikon·RAB 등에서 공개 자료의 존재는 확인했지만 FRAME_DB용 미디어 재배포 허락을 확보하지 않았다. 미확인은 허락도 금지도 단정하지 않는 상태이며, 이번 수집 경로는 텍스트 근거와 링크에 머문다.

## 7. 완료 기준 대조

### 실제 자동 수집 큐의 출처 선택 보완

CMU의 no-crawl 고지를 자동 배치에서 무시하지 않는다. CMU mocap/MMAC는 수동 참조 후보로 남기고 이번 예약의 자동 자료원으로 사용하지 않는다. 본문이 막힌 Khan Academy도 검색 색인만으로 채택 사실을 만들지 않는다.

- `pose` 대체 시작점: Adobe의 공식 [휴대폰 인물 촬영 안내](https://www.adobe.com/express/learn/blog/how-to-take-portrait-photos-with-your-phone). 본문을 직접 열어 자세·조명·구도에 관한 교육 설명을 확인했다. 짧은 사실 정리와 링크에 한하며 사진 재배포 권리는 미확인이다.
- `interaction` 대체 시작점: NYFA의 공식 [촬영 실습 안내](https://www.nyfa.edu/filmmaking/projects/). 대사 장면의 목표·행동·서브텍스트와 배우·카메라 블로킹 실습 설명을 직접 확인했다. 이는 실제 악수 모션 파일의 확보를 대신하지 않으며, 부족한 세부 항목은 다른 공개 1차 교육 자료로 확장한다.
- `persona` 대체 시작점: Open University의 [Start writing fiction](https://www.open.edu/openlearn/history-the-arts/creative-writing/start-writing-fiction/content-section-0). 본문과 인물 만들기·입체/평면 인물·인물 묘사 등의 단원 목록을 직접 확인했다. 등록 없이 학습 내용을 시작할 수 있다고 안내하지만 강의·제3자 이미지의 재배포 허락으로 해석하지 않는다.

예약 작업은 BBC 음원·분석 이용이나 NC/교육 한정 미디어를 자동 취득하지 않는다. 각 실행은 대체 자료원의 실제 본문·조건을 다시 확인하고, 제한이 발견되면 다른 공개 1차 자료원으로 바꾸거나 부족분을 보고한다.

- 시드 `categories`의 ID 29개와 매트릭스 29행을 1:1 대조한다.
- 각 행에 구체적 1차 URL, 지원 가능한 사실/사례, 매체, 증거 범위, 텍스트/미디어 권리 상태를 둔다.
- **29/29는 출처 커버리지**다. 수집 완료량·라이선스 승인량·검수 합격량으로 전환하지 않는다.
- 이 문서만 작성한다. 데이터·앱·스키마 변경, Drive 작업, 생성·유료 지출·업로드·예약 작업은 수행하지 않는다.
