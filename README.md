# Book Data Pipeline

외부 도서 목록 웹 소스에서 책 데이터를 수집해 CSV 데이터셋으로 만드는 작은 수집 파이프라인입니다. 더미 데이터 생성 대신 실제 목록을 사용하되, 프로젝트 규모에 맞춰 Python 표준 기능과 최소한의 라이브러리만 사용합니다.

> 본 프로젝트는 웹 크롤링과 데이터 수집 파이프라인을 학습하기 위한 개인 프로젝트입니다. 실행 전 대상 사이트의 최신 `robots.txt`, 이용약관, API 및 접근 정책을 직접 확인해야 합니다. 자세한 내용은 [크롤링 정책 및 운영 원칙](docs/crawling-policy.md)을 참고하세요.

## 핵심 기획

- 목표: 전체 `TARGET_ROWS`만큼의 고유 도서 데이터 수집
- 수집 범위: 환경 설정에 정의된 카테고리별 수집 범위를 순회하고 전체 목표에 도달하면 종료
- 저장소: CSV append 방식
- 체크포인트: 마지막으로 저장에 성공한 카테고리와 페이지를 JSON에 기록
- 멱등성: 기존 CSV와 현재 페이지의 복합키를 비교해 중복 저장 방지
- 요청 정책: 설정된 요청 간 대기, `429` 응답 시 동일 페이지 재시도, 반복 실패 시 종료 코드 `1`
- 실패 정책: URL·네트워크 오류도 로그를 남기고 종료 코드 `1` 반환

현재 과제의 중복 기준은 다음 네 필드의 조합입니다.

```text
(title, primary_author, publisher, published_date)
```

상품·에디션 단위의 엄밀한 식별이나 데이터베이스 기반 운영은 이 프로젝트의 범위에 포함하지 않습니다.

## 동작 순서

```mermaid
flowchart TD
    A[환경 설정 로드] --> B[수집 URL 확인]
    B --> C[체크포인트 로드]
    C --> D[기존 CSV의 중복 키 로드]
    D --> E[카테고리와 페이지 순회]
    E --> F{HTTP 응답}
    F -->|429| G[설정된 대기 후 동일 페이지 재시도]
    G --> F
    F -->|429 반복 실패| X[로그 기록 후 종료 코드 1]
    F -->|네트워크·HTTP 오류| Y[로그 기록 후 종료 코드 1]
    F -->|정상 응답| H[HTML 파싱]
    H --> I[복합키 중복 제거]
    I --> J[CSV append 저장]
    J --> K[메모리 중복 키 갱신]
    K --> L[페이지 체크포인트 갱신]
    L --> M{TARGET_ROWS 도달?}
    M -->|아니오| N[설정된 범위에서 대기] --> E
    M -->|예| O[정상 종료]
```

재실행 시에는 저장된 체크포인트의 다음 페이지부터 시작하고, CSV에서 읽은 중복 키를 함께 사용합니다. 따라서 이미 저장된 페이지를 다시 읽더라도 동일한 레코드를 다시 append하지 않습니다.

## 폴더 구조

```text
.
├── src/
│   ├── main.py                    # 전체 파이프라인 orchestration
│   ├── common.py                  # 공통 logger와 timestamp
│   └── crawling/
│       ├── collector.py           # HTTP 요청, URL 확인, 429 처리
│       ├── parser.py              # HTML 파싱과 도서 필드 추출
│       ├── deduplicator.py        # 복합키 생성과 중복 제거
│       ├── writer.py              # CSV append 저장
│       └── checkpoint.py          # 체크포인트 저장과 복구
├── config/
│   └── logrotate.conf             # 로그 보관 설정 예시
├── docs/
│   └── crawling-policy.md         # 크롤링 정책 및 운영 원칙
├── .env.example                   # 실행 설정 예시
├── LICENSE                        # MIT 라이선스
├── requirements.txt               # Python 의존성 목록
└── README.md
```

실행 중 생성되는 CSV와 체크포인트의 위치는 각각 `LOADING_PATH`, `CHECKPOINT_PATH`로 지정합니다. 로그는 `logs/book-data-pipeline.log`에 터미널 출력과 함께 기록됩니다.

## 실행

### 1. 의존성 설치

```bash
conda activate sandbox
python -m pip install -r requirements.txt
```

### 2. 환경 설정 작성

`.env.example`을 복사한 뒤 실제 실행 환경에 맞는 URL, 경로, 카테고리 ID와 저장 경로를 `.env`에 작성합니다. 실제 `.env` 파일은 커밋하지 않습니다.

```bash
cp .env.example .env
```

### 3. 파이프라인 실행

```bash
PYTHONPATH=src python src/main.py
```

## 실행 결과

다음은 2026-08-17 실행에서 확인한 결과입니다. 대상 사이트와 환경별 식별 정보는 공개하지 않습니다.

- 목표 행 수: `100,000`
- 최종 저장 행 수: `100,000`
- 종료 상태: `TARGET_ROWS 도달 및 정상 완료`
- 마지막 페이지 처리: 50건 파싱, 중복 2건, 목표 잔여량에 따라 40건 저장

```text
[INFO] 페이지 처리 완료 - parsed=50, duplicated=2, saved=40, total=100000
[INFO] TARGET_ROWS 도달 및 정상 완료 - rows: 100000
```

> 이 기록은 2026-08-16 ~ 2026-08-17 당시의 단일 실행 결과입니다. 대상 데이터와 실행 환경에 따라 재실행 결과는 달라질 수 있습니다.

## License

이 프로젝트의 직접 작성한 소스 코드와 프로젝트 문서는 MIT License로 배포합니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

실제 수집 데이터, 외부 웹사이트의 콘텐츠, 상표 및 제3자 자료는 이 라이선스의 적용 대상이 아니며 각각의 권리와 이용 조건을 따릅니다.
