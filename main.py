import logging
from config.logging_config import setup_logging
from stock_analyzer.database import init_db
from stock_analyzer.graph.builder import get_graph_app

# 1. 로깅 설정 적용
# 애플리케이션의 다른 어떤 코드보다 먼저 실행되어야 합니다.
setup_logging()

# 로거 객체 생성
logger = logging.getLogger(__name__)

def run_analysis(symbol: str):
    """
    주어진 질문에 대해 전체 분석 워크플로우를 실행합니다.

    Args:
        question (str): 분석할 질문 (예: "AAPL 주가 전망 분석해줘").
    """
    try:
        # 2. 컴파일된 그래프 애플리케이션을 가져옵니다.
        app = get_graph_app()

        # 3. 그래프 실행을 위한 초기 상태를 정의합니다.
        # 모든 값은 빈 문자열로 시작하며, 각 노드를 거치면서 채워집니다.
        initial_state = {
            "question": symbol,
            "crawled_urls": [],
            "db_result": "",
            "balance_sheet": "",
            "income_statement": "",
            "cash_flow": "",
            "final_answer": ""
        }

        logger.info(f"===== '{symbol}'에 대한 분석 워크플로우 시작 =====")
        
        # 4. 그래프를 스트리밍 방식으로 실행하고 각 단계의 결과를 로깅합니다.
        final_state = None
        for event in app.stream(initial_state):
            for key, value in event.items():
                logger.info(f"--- 노드: '{key}' 실행 완료 ---")
                # 상세한 상태 변화는 DEBUG 레벨로 기록합니다.
                # logger.debug(f"상태 값: {value}") 
            final_state = event

        # 마지막 이벤트에서 최종 답변을 추출합니다.
        if final_state:
            final_answer = final_state.get("generate_answer", {}).get('final_answer', "최종 답변을 생성하지 못했습니다.")
            logger.info("===== 분석 워크플로우 종료 =====")
            print("\n" + "="*50)
            print("[ {symbol}최종 분석 보고서 ]")
            print("="*50)
            print(final_answer)
            print("="*50)

    except Exception as e:
        logger.critical(f"분석 워크플로우 실행 중 심각한 오류 발생: {e}", exc_info=True)


if __name__ == "__main__":
    # 5. 데이터베이스 초기화
    # DB에 테이블이 없으면 생성합니다. 이미 있으면 아무 작업도 하지 않습니다.
    init_db()
    
    # 6. 분석 실행
    # 분석하고 싶은 질문을 여기에 입력하세요.
    analysis_question = "AAPL"
    run_analysis(analysis_question)
    