<div align="center">

# FRAME DB

### 이미지·영상 제작을 위한 시각 레퍼런스 데이터베이스

인물, 촬영, 장면, 오디오, 후반 작업의 제작 요소를 찾아보고 비교할 수 있도록
정리한 29개 분야의 레퍼런스 라이브러리입니다.

![React 19](https://img.shields.io/badge/React-19-149ECA?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)
![Cloudflare D1](https://img.shields.io/badge/Database-Cloudflare_D1-F38020?logo=cloudflare&logoColor=white)
![Vinext](https://img.shields.io/badge/Framework-Vinext-111111)

</div>

## 프로젝트

FRAME DB는 포즈나 의상 같은 기존 레퍼런스뿐 아니라 헤어, 메이크업, 표정,
시선, 손동작, 조명, 카메라, 연기, 사운드 등 제작에 필요한 정보를 한곳에서
검색하고 조합하기 위한 데이터베이스입니다.

각 자료는 출처 사실, 직접 작성한 가이드, 창작 제안, 미디어를 구분합니다.
이미지가 적합한 항목은 이미지를 중심으로 보여주고 짧은 사용 가이드를
제공합니다. 제작용 상세 프롬프트와 출처 정보는 기본 화면에 길게 노출하지
않습니다.

## 현재 데이터

기준: 2026-10-30 로컬 데이터셋

| 범위 | 수량 |
| --- | ---: |
| 분야 | 29 |
| 전체 항목 | 2,814 |
| 사용 가이드가 있는 항목 | 2,814 |
| 출처 검토를 거친 웹 개념 | 482 |
| 이미지 생성·검수 완료 | 147 |
| 검증된 Drive 파일 표현 | 7,167 |

147개 생성 이미지는 헤어 44개, 메이크업·그루밍 34개, 표정 37개, 시선
8개, 손동작 24개입니다. 시선 정면은 중립 기준 이미지를 공유하므로 고유
이미지 147장에 참조 슬롯 148개가 연결됩니다.

웹 개념 수집의 1차 기준은 분야별 최대 20개, 총 최대 580개였습니다.
482개는 승인·반영된 수량이며, 목표 수량은 확보 수량이나 가능한 전체 개념의
수가 아닙니다. 조사·검수 결과와 미달 사유는 `docs/WEB_DB_POPULATION_RESULT.md`를
참고하세요.

## 주요 기능

- 분야, 하위 분류, 출처, 상태, 성별, 각도, 다국어 키워드와 원본 ID로 검색
- 상세 이미지, 각도별 이미지, 원본 링크와 짧은 사용 가이드 확인
- 항목 간 관계와 연결된 제작 스킬 탐색
- 최대 4개 항목 비교
- JSON 및 Markdown 내보내기
- 사용자별 컬렉션과 텍스트 초안 지원
- D1 데이터베이스의 단계별·멱등 시드 초기화
- 원본 Drive 미디어의 검증된 매니페스트 제공 및 오류 응답 처리

## 기술 구성

- **화면/API:** React 19, TypeScript, Vinext
- **데이터베이스:** Cloudflare D1, Drizzle ORM, SQLite 스키마
- **런타임:** Cloudflare Workers / Wrangler
- **데이터 파이프라인:** 원본 스냅샷과 검수된 웹·창작·이미지 산출물을 분리한 정규화 작업

```text
app/                 카탈로그 화면과 API
components/          공통 UI
db/                  D1 스키마
drizzle/             스키마 마이그레이션
data/                정규화 시드, 출처 기록, 미디어 매니페스트
lib/                 데이터 조회와 Drive 미디어 응답 처리
public/generated/    승인된 자체 생성 이미지
scripts/data/        데이터 수집·검증·정규화 도구
tests/               데이터·Drive·콘텐츠 무결성 검사
docs/                설계, 출처 조사, 이전 및 결과 기록
```

## 로컬 개발

### 요구 사항

- Node.js 22.13 이상
- pnpm 11.25
- 로컬 D1을 제공하는 프로젝트 런타임

### 설치 및 실행

```bash
pnpm install
pnpm dev
```

로컬 D1을 처음 구성할 때는 먼저 빌드해 Wrangler 설정을 만든 뒤 스키마를
적용합니다.

```bash
pnpm build
node node_modules/wrangler/bin/wrangler.js d1 execute DB \
  --local \
  --config dist/server/wrangler.json \
  --persist-to .wrangler/state \
  --file drizzle/0000_yielding_shadowcat.sql
```

서버를 실행한 다음 `GET /api/bootstrap?step=0`부터 `step=10`까지 호출해
11개 시드 단계를 초기화합니다. 각 단계는 재실행할 수 있습니다.

## 검증

```bash
pnpm test:data
pnpm exec tsc --noEmit
pnpm build
```

`pnpm test:data`는 갤러리 동기화, Drive 응답과 미디어 매핑, 시드 및 웹·창작·
에셋 데이터 계약을 확인합니다.

## 미디어와 출처

원본 포즈·의상 미디어는 Git 저장소에 포함하지 않고 검증된 Drive 매핑을 통해
불러옵니다. `public/generated/frame-assets/`에는 승인된 자체 생성 이미지가
포함됩니다. 저작권이 있는 원본 파일의 재배포·전재·재판매 권리는 각 출처의
조건을 따릅니다. 공개 열람이나 검색 결과가 미디어 재사용 허가를 뜻하지
않습니다.

출처 자료를 전수 다운로드하거나 저장소에 복제하지 마세요. 원본 이미지를
사용하는 경우에는 해당 출처의 약관과 개별 미디어 조건을 먼저 확인하세요.

이 저장소에는 현재 `LICENSE` 파일이 없습니다. 별도 라이선스가 추가되기 전까지
코드나 미디어가 오픈소스로 허가되었다고 간주하지 마세요. 데이터베이스 안의
외부 자료에는 각기 다른 출처·권리 정보가 적용됩니다.

## 문서

- [데이터베이스 설계](docs/ASSET_DB_DESIGN.md)
- [확장 요구사항](docs/ASSET_EXPANSION_REQUIREMENTS.md)
- [에셋 확장 작업 지시서](docs/ASSET_EXPANSION_WORK_ORDER.md)
- [에셋 확장 결과와 검증](docs/ASSET_EXPANSION_RESULT.md)
- [Drive 이전 및 검증](docs/DRIVE_MIGRATION_STATUS.md)
- [웹 자료 수집 설계](docs/WEB_DB_POPULATION_PLAN.md)
- [웹 자료 수집 결과](docs/WEB_DB_POPULATION_RESULT.md)
