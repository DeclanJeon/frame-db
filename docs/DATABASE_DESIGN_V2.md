# FRAME DB v2 구현 설계

## 제품 기준

데이터베이스가 주 제품이다. 첫 화면은 검색·필터·갤러리이며, 프롬프트·프로젝트·생성 기능을 첫 화면의 중심으로 두지 않는다. 기본 항목, 변형, 실제 미디어, 제작 지침을 구분한다.

## 수량 기준

원본 포즈 1,439개 이미지는 288개 자세 그룹에 연결한다. 의상은 1,407개 세트에 연결한다. 원본 식별자·언어·외부 URL을 보존하고 자동 번역·분류는 메타데이터 기반임을 표시한다. 214개 직접 작성 텍스트는 실제 미디어 미확보의 초안이며, 정식 미디어 레퍼런스 목표 달성에 합산하지 않는다.

분야별 목표는 pose 1,400, costume 1,407, 나머지 22개 분야 각 1,400이다. 합계 33,607은 장기 기본 항목 목표다. 각도·색상만 바꾸어 기본 항목 수를 늘리지 않는다.

## 데이터 모델

categories → reference_entries → entry_variants → media_assets.

reference_entries는 sources, prompt_templates, tags/entry_tags, entry_relations, entry_versions에 연결한다. categories에는 skill_mappings를 연결한다. import_batches에는 원본 기대 수·색인 수·그룹 수·미디어 다운로드 여부·시각 검수 범위를 기록한다.

collections는 인증된 소유자 ID를 가지며 collection_entries에 연결한다. 사용자 컬렉션은 서버 D1에 저장한다. 브라우저는 화면 필터와 비교 선택만 메모리에 유지한다.

## 스킬 반영

콘텐츠 제작 저장소의 Character SSOT 0–33, Visual/Face/Hair Identity Lock, IMMUTABLE/STABLE/VARIABLE, Voice Identity/Speech Style/Performance 분리, 씬→샷→패널·발화자/청자 반응 연결을 분류 기준으로 사용한다. 원문 스킬 실행 파이프라인을 홈페이지에 옮기지 않고, 자료 상세에서 관련 필드와 참조 경로를 제공한다.

## 상태

external = 외부 원본을 가리키는 메타데이터 색인.
text = 직접 작성하거나 사용자가 추가한 텍스트 초안.

현재 owned/verified 미디어는 0개다. 현황에서는 이를 원본 색인 및 텍스트 초안과 별도로 표시한다.

## API

- GET /api/bootstrap?step=N: 단계별 멱등 카탈로그 초기 적재. private Site의 기본 데이터 준비에 사용.
- GET /api/catalog?summary=1: DB 집계와 수집 이력.
- GET /api/catalog: 바인딩 파라미터 기반 검색, 필터, 정렬, 페이지네이션.
- GET /api/entries/:id: 기본 항목·변형·링크·태그·프롬프트·관련 자료·스킬.
- POST /api/entries: 인증 및 같은 출처 확인 후 신규 텍스트 초안 등록.
- GET/POST /api/collections: 소유자별 컬렉션 조회·생성·항목 추가·제거.
- GET /api/export?ids=…&format=json|markdown: 최대 20개 기본 항목과 종속 정보 내보내기.
- GET /api/export/all: 전체 카탈로그·변형·링크·지침·관계 JSON. 개인 컬렉션은 제외.
- GET /api/status: 현재 DB 집계와 저장 구조 상태.

## 실제 미디어 확장 시 다음 단계

1. 권한이 확보된 파일과 provenance를 R2에 등록한다.
2. 항목별 이미지·음성·영상 샘플을 실제로 검사하고 상태를 갱신한다.
3. 남녀 분류가 필요한 분야는 독립적인 자료 계획을 수립한다.
4. 분야별 taxonomy·중복 판단·변형 구분을 확정한 뒤 미디어 확보를 확대한다.
5. PostgreSQL 등 다른 저장소로 이전할 때도 기본 항목 ID와 원본 ID를 유지한다.
