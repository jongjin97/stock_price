import logging
from .state import GraphState
from stock_analyzer.tools.database_tools import db_query_tool
from stock_analyzer.tools.financial_tools import financial_statement_tool
from langchain_openai import ChatOpenAI
from config import settings

logger = logging.getLogger(__name__)
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0,
    api_key=settings.OPENAI_API_KEY
)

summary_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    api_key=settings.OPENAI_API_KEY
)

def fetch_db_news_node(state: GraphState):
    """
    DB에서 최신 뉴스 3개를 가져와, 가장 최신 뉴스는 원문을, 이전 2개는 요약하는 노드.
    """
    logger.info("--- 노드 실행: DB 뉴스 조회 및 부분 요약 ---")
    question = state['question']
    
    try:
        # 1. Text-to-SQL 도구를 사용하여 최신 뉴스 3개를 가져오도록 지시
        # 각 기사를 명확히 구분하기 위해 구분자(separator)를 사용하도록 요청
        db_query = f"""
        '{question}'에 대한 가장 최신 뉴스 3개를 news_upload_time 기준으로 알려줘. 
        각 기사의 제목과 내용을 포함하고, 기사 사이를 '---ARTICLE SEPARATOR---'로 구분해줘.
        """
        raw_news_text = db_query_tool.invoke(db_query)
        logger.debug(f"DB 최신 뉴스 원문 검색 결과: {raw_news_text}")

        # 2. 가져온 뉴스가 유효한지 확인하고 처리
        if not raw_news_text or "찾을 수 없습니다" in raw_news_text or "오류" in raw_news_text:
            logger.warning("DB에서 유효한 뉴스를 찾지 못했거나 오류가 발생했습니다.")
            state['db_result'] = raw_news_text
            return state

        # 3. 개별 기사로 분리
        articles = raw_news_text.split('---ARTICLE SEPARATOR---')
        articles = [article.strip() for article in articles if article.strip()]

        if not articles:
            state['db_result'] = "DB에 뉴스가 없습니다."
            return state

        # 4. 가장 최신 뉴스(원문)와 이전 뉴스(요약 대상) 분리
        most_recent_news_raw = articles[0]
        older_news_to_summarize = "\n\n".join(articles[1:])
        
        older_news_summary = "이전 뉴스 없음."
        if older_news_to_summarize:
            logger.info("이전 뉴스 요약을 시작합니다.")
            summarization_prompt = f"""
            다음은 이전 뉴스 기사들의 내용입니다. 각 기사의 핵심 내용을 간결하게 요약해주세요.

            [뉴스 원문]
            {older_news_to_summarize}

            [요약 결과]
            """
            older_news_summary = summary_llm.invoke(summarization_prompt).content
            logger.debug(f"이전 뉴스 요약 결과: {older_news_summary}")

        # 5. 최종 결과 조합
        final_db_result = f"""
        [가장 최신 뉴스 (원문)]
        {most_recent_news_raw}

        ---
        [이전 뉴스 요약]
        {older_news_summary}
        """
        state['db_result'] = final_db_result
        return state

    except Exception as e:
        logger.error(f"DB 뉴스 처리 중 오류: {e}", exc_info=True)
        state['db_result'] = "오류: DB에서 뉴스를 처리할 수 없습니다."
        return state
    
def fetch_financials_node(state: GraphState):
    """
    주어진 심볼에 대한 재무제표를 가져오는 노드.
    yfinance 도구를 사용하여 재무상태표, 손익계산서, 현금흐름표를 가져옵니다.
    """
    logger.info("--- 노드 실행: 재무제표 조회 ---")
    question = state["question"]
    try:
        financial_data = financial_statement_tool.invoke({"input": question})
        
        state["income_statement"] = financial_data.get("income_statement", "")
        state["balance_sheet"] = financial_data.get("balance_sheet", "")
        state["cash_flow"] = financial_data.get("cash_flow", "")

        logger.info("재무제표 조회를 완료하고 상태를 업데이트했습니다.")

        return state
    except Exception as e:
        logger.error(f"yfinance 검색 중 오류: {e}", exc_info=True)

        state["income_statement"] = "오류: 재무제표를  가져올 수 없습니다."
        state["balance_sheet"] = "오류: 재무제표를  가져올 수 없습니다."
        state["cash_flow"] = "오류: 재무제표를  가져올 수 없습니다."

        return state
    
def generate_final_answer_node(state: GraphState):
    """모든 수집된 정보를 종합하여 최종 분석 보고서를 생성하는 노드"""
    logger.info("--- 노드 실행: 최종 분석 보고서 생성 ---")
    
    # LLM에게 전달할 최종 프롬프트 구성
    final_prompt = f"""
    당신은 15년 경력의 월스트리트 애널리스트입니다. 제공된 모든 데이터를 종합하여, 주어진 질문에 대한 심층 분석 보고서를 작성해주세요.
    객관적인 데이터에 기반하여 논리적으로 추론하고, 최종 결론을 명확하게 제시해야 합니다.

    [분석 대상 질문]
    {state['question']}

    ---
    [1. 내부 데이터베이스 뉴스 분석 (최신 1건 원문 + 이전 뉴스 요약)]
    {state.get('db_result', '정보 없음')}
    ---
    [2. 재무상태표 요약 (최근 4분기)]
    {state.get('balance_sheet', '정보 없음')}
    ---
    [3. 손익계산서 요약 (최근 4분기)]
    {state.get('income_statement', '정보 없음')}
    ---
    [4. 현금흐름표 요약 (최근 4분기)]
    {state.get('cash_flow', '정보 없음')}
    ---

    [심층 분석 보고서]
    (위 모든 정보를 종합하여, 질문에 대한 답변을 분석 리포트 형식으로 작성하세요.)
    """
    response = llm.invoke(final_prompt)
    state['final_answer'] = response.content
    logger.info("최종 분석 보고서 생성을 완료했습니다.")
    return state