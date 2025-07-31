import os
import sys
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

try:
    # This works when the script is imported as part of a package.
    from config import settings
except ImportError:
    # This is a fallback for running the script directly.
    # It adds the project root to the Python path.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    from config import settings

# LangChain이 사용할 DB 연결 객체 생성
# settings.py의 DATABASE_URL을 사용
# AI가 테이블 정보를 더 잘 이해핟고록 스키마에 포함시킬 테이블을 명시
db = SQLDatabase.from_uri(
    settings.DATABASE_URL,
    include_tables=["stock", "news", "analysis_results"],
    sample_rows_in_table_info=2 # 각 테이블의 샘플 데이터를 2개씩 보여줘서 AI의 이해를 돕습니다.
)

# Text-to-SQL을 수행할 LLM 초기화
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    api_key=settings.OPENAI_API_KEY
)

# SQL Agent 생성
# 이 Agent가 자연어 -> SQL 변환 및 실행 -> 결과 반환을 모두 처리
sql_agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",
    verbose=settings.DEBUG, # Agent의 생각과 행동을 콘솔에 출려가형 디버깅에 용이하게 합니다.
    handle_parsing_errors=True # SQL 파싱 에러 발생 시 대처 방안을 설정합니다.
)

# Agent를 LangGraph에서 사용할 수 있는 Tool 객체로 변환
db_query_tool = Tool(
    name="database_query",
    func=sql_agent_executor.invoke,
    description="""
    주식, 뉴스, 분석 결과에 대한 정보를 얻기 위해 데이터베이스에 질문할 때 사용합니다.
    질문은 반드시 하나의 완전한 자연어 문장이어야 합니다.
    예시 질문: "AAPL의 가장 최근 뉴스 5개는 무엇인가요?", "최근에 수집된 뉴스 기사 3개의 제목을 알려주세요."
"""
)