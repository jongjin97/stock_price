# 📈 AI 주식 뉴스 분석기 (AI Stock News Analyzer)

LangGraph와 Text-to-SQL을 활용하여 뉴스와 재무 데이터를 종합적으로 분석하고, 투자 인사이트를 제공하는 지능형 분석 시스템

## 📌 1. 프로젝트 개요 (Overview)

본 프로젝트는 최신 주식 뉴스를 단순히 전달하는 것을 넘어, AI가 해당 뉴스를 다각적이고 깊이 있게 분석하여 투자 판단에 실질적인 도움을 주는 것을 목표로 합니다.

가장 큰 특징은 LangGraph를 통해 "DB 최신 뉴스 조회 → 재무 데이터 확인 → 종합 분석"이라는 명시적인 작업 흐름을 구축하여, 일반적인 AI Agent의 예측 불가능성을 제어하고 분석 과정의 신뢰성을 확보했다는 점입니다. 또한, Text-to-SQL 기술을 도입하여 AI가 직접 데이터베이스와 대화하며 필요한 정보를 추출하도록 설계되었습니다.

## ✨ 2. 주요 특징 (Key Features)

제어 가능한 AI 워크플로우: LangGraph를 사용하여 분석의 각 단계를 명확하게 정의하고, 안정적이고 예측 가능한 결과 도출

하이브리드 데이터 소싱: 내부 DB의 정형 데이터(과거 뉴스, 재무 정보)를 우선적으로 활용하고, 부족한 정보는 실시간 웹 검색으로 보충

지능형 DB 조회: AI가 자연어 질문을 SQL 쿼리로 자동 변환하여 필요한 데이터를 직접 DB에서 추출 (Text-to-SQL)

심층 컨텍스트 분석: 최신 뉴스 1건(원문)과 이전 뉴스(요약), 그리고 yfinance를 통해 수집한 최신 4분기 재무제표를 종합하여 분석의 깊이를 더함

모듈화된 설계: 기능별(도구, 그래프, DB 모델 등)로 코드가 분리되어 있어 유지보수 및 기능 확장이 용이

## ⚙️ 3. 시스템 아키텍처 (System Architecture)

본 시스템은 LangGraph로 설계된 다음과 같은 순서로 작동합니다.

[시작] 재무제표 조회 (fetch_financials): yfinance를 통해 분석 대상의 최신 4분기 재무제표(재무상태표, 손익계산서, 현금흐름표)를 가져옵니다.

→ DB 뉴스 확인 및 요약 (fetch_db_news): 내부 데이터베이스에서 최신 뉴스 3건을 조회합니다. 가장 최신 뉴스는 원문을, 이전 2건은 AI를 통해 요약합니다.

→ 최종 보고서 생성 (generate_answer): 모든 수집된 정보(뉴스 원문/요약, 재무제표, 웹 검색 결과)를 종합하여 최종 분석 보고서를 생성합니다.

→ [종료]

## 📂 4. 폴더 구조 (Folder Structure)

```
ai_stock_analyzer/
│
├── .env # (직접 생성) API 키, DB 정보 등 환경 변수
├── .gitignore
├── README.md
├── requirements.txt
├── main.py # 🚀 전체 워크플로우 실행 파일
│
├── config/ # 설정 폴더
│ ├── settings.py
│ └── logging_config.py
│
├── stock_analyzer/ # 핵심 소스코드 패키지
│ ├── database.py # DB 연결 및 초기화
│ ├── models.py # SQLAlchemy DB 테이블 모델
│ │
│ ├── graph/ # LangGraph 워크플로우 패키지
│ │ ├── state.py
│ │ ├── nodes.py
│ │ └── builder.py
│ │
│ └── tools/ # AI가 사용하는 도구 패키지
│ ├── database_tools.py
│ └── financial_tools.py
│
└── logs/ # 로그 파일 저장 폴더
```

## 🛠️ 5. 기술 스택 (Tech Stack)

언어: Python 3.x

AI 프레임워크: LangChain, LangGraph

LLM: OpenAI GPT-4.1, OpenAI GPT-4.1-mini

데이터베이스: SQLAlchemy, MySQL

금융 데이터: yfinance

## 🚀 6. 설치 및 실행 방법 (Setup & Run)

1. 프로젝트 복제
   ```
   git clone https://github.com/your-username/ai_stock_analyzer.git
   cd ai_stock_analyzer
   ```
2. 가상환경 생성 및 활성화
   ```
   python -m venv venv
   ```
   ### Windows
   ```
   venv\Scripts\activate
   ```
   ### macOS / Linux
   ```
   source venv/bin/activate
   ```
3. 필요 라이브러리 설치
   ```
   pip install -r requirements.txt
   ```
4. 환경 변수 설정
   프로젝트 루트 디렉토리에 .env 파일을 생성하고 아래 내용을 채워주세요.

# .env

## --- API KEYS ---

```
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## --- DATABASE CONFIG ---

```
DB_TYPE="mysql"
DB_NAME="news_analysis"
```

5. 실행
   아래 명령어를 실행하면 DB 테이블이 자동으로 생성되고, main.py에 설정된 질문으로 분석이 시작됩니다.

```
python main.py
```

콘솔과 logs/app.log 파일에서 실행 과정을 확인할 수 있으며, 최종 분석 결과는 터미널에 출력됩니다.

## 🔮 7. 향후 개선 방향 (Future Improvements)

웹 대시보드 개발: 분석 결과를 시각적으로 보여주는 웹 인터페이스 구축 (Streamlit, FastAPI 등)

분석 모델 고도화: 예측 정확도를 실제 주가와 비교하여 백테스팅하고, 프롬프트와 그래프 로직을 지속적으로 개선

다중 종목 분석: 여러 주식 종목을 동시에 또는 주기적으로 분석하는 스케줄링 기능 추가 (APScheduler, Celery 등)

수집기 프로젝트 분리: 데이터 수집 파이프라인을 별도의 프로젝트로 분리하여 시스템 안정성 및 확장성 확보
