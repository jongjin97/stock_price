import logging
from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import (
    fetch_db_news_node,
    fetch_financials_node,
    generate_final_answer_node
)

logger = logging.getLogger(__name__)

def get_graph_app():
    """
    LangGraph 워크플로우를 구성하고 컴파일하여 실행 가능한 app을 반환합니다.
    """
    logger.info("LangGraph 워크플로우를 구성합니다...")
    
    workflow = StateGraph(GraphState)

    # 1. 노드(작업 단위) 등록
    logger.debug("그래프 노드를 등록합니다.")
    workflow.add_node("fetch_financials", fetch_financials_node)
    workflow.add_node("fetch_db_news", fetch_db_news_node)
    workflow.add_node("generate_answer", generate_final_answer_node)

    # 2. 엣지(흐름) 연결
    logger.debug("그래프 엣지를 연결합니다.")
    
    # 시작점 설정: 재무제표 조회부터 시작
    workflow.set_entry_point("fetch_financials")
    
    # 일반 엣지 연결
    workflow.add_edge("fetch_financials", "fetch_db_news")
    workflow.add_edge("fetch_db_news", "generate_answer")
    workflow.add_edge("generate_answer", END) # 최종 답변 생성 후 워크플로우 종료

    # 3. 그래프 컴파일
    app = workflow.compile()
    logger.info("LangGraph 컴파일이 완료되었습니다.")
    
    return app