# README.md



```text
├── src/
│   ├── crawling/
│   │   ├── collector.py      # HTTP 요청 및 응답 획득
│   │   ├── parser.py         # HTML 파싱 및 도서 데이터 추출
│   │   ├── writer.py         # CSV 저장
│   │   ├── checkpoint.py     # 수집 진행 상태 저장/복구
│   │   ├── deduplicator.py   # 수집 데이터 unique 검사
│   │   ├── common.py         # 공통 모듈 (시간 포맷/타임스탬프, 공통 logger)
│   │   └── config.py         # URL, CID, sleep, 요청 옵션 등
│   └── main.py               # orchestration, 유일 진입점
├── data/
│   └── books.csv             # 최종 수집 데이터
├── state/
│   └── checkpoint.json       # 마지막 정상 처리 상태
├── logs/
│   └── crawler.log           # 실행 로그
├── docs/
│   ├── architecture.md       # 모듈 역할 및 전체 파이프라인
│   └── idempotency.md        # checkpoint / 중복 제거 / 재실행 정책
├── .gitignore                # git이 추적하지 않을 폴더 및 파일 설정
└── README.md
```

