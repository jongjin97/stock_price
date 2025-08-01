from typing import TypedDict, Annotated, List
import operator

class GraphState(TypedDict):
    """
    그래프의 상태를 나타내는 객체입니다.
    각 노드는 이 상태 객체를 읽고, 자신의 작업 결과를 추가하여 다음 노드로 전달합니다.

    Attributes:
        question: 사용자의 원본 질문
        crawled_urls: 크롤링된 뉴스 URL 목록
        db_result: 데이터베이스 검색 결과
        income_statement: 재무상태표 결과
        balance_sheet: 손익계산서 결과
        cash_flow: 현금흐름표 결과
        final_answer: 최종 생성된 분석 답변
    """
    question: str
    crawled_urls: List[str]
    db_result: str
    income_statement: str
    balance_sheet: str
    cash_flow: str
    final_answer: str


