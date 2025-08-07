import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from stock_analyzer.graph.builder import get_graph_app
from config.logging_config import setup_logging

# 1. 로깅 및 FastAPI 앱, 그래프 앱 초기화
try:
    setup_logging()
    logger = logging.getLogger(__name__)
    app = FastAPI(
        title="AI 주식 뉴스 분석기 API",
        description="LangGraph 기반의 AI 분석 모델을 서빙하는 API입니다.",
        version="1.0.0"
    )
    graph_app = get_graph_app()
except Exception as e:
    # 초기화 단계에서 오류 발생 시 로그를 남기고 프로그램을 종료할 수 있도록 처리
    logging.critical(f"애플리케이션 초기화 실패: {e}", exc_info=True)
    raise

# 2. 입력 데이터 모델 정의 (Pydantic 사용)
# API 요청의 본문(body) 형식을 강제하여 데이터 유효성을 검사합니다.
class AnalysisRequest(BaseModel):
    symbol: str

# 3. API 엔드포인트 생성
@app.post("/analyze", summary="주식 분석 실행", description="주어진 심볼에 대해 분석 워크플로우를 실행하고 최종 보고서를 반환합니다.")
def analyze_stock(request: AnalysisRequest):
    """
    주어진 심볼에 대해 분석을 수행하고 결과를 반환하는 API 엔드포인트입니다.
    
    - **symbol**: 분석할 주식의 심볼 (예: "AAPL")
    """
    try:
        symbol = request.symbol.upper()
        logger.info(f"API 분석 요청 수신: {symbol}")

        # LangGraph 실행을 위한 초기 상태 정의
        initial_state = {
            "question": symbol,
            "crawled_urls": [],
            "db_result": "",
            "web_result": "",
            "balance_sheet": "",
            "income_statement": "",
            "cash_flow": "",
            "final_answer": ""
        }

        # 그래프 워크플로우 실행
        final_answer = "분석 결과를 생성하지 못했습니다."
        for event in graph_app.stream(initial_state):
            # 'generate_answer' 노드가 실행된 이벤트에서 최종 결과를 찾습니다.
            if "generate_answer" in event:
                final_answer = event["generate_answer"].get('final_answer', final_answer)

        logger.info(f"'{symbol}'에 대한 분석 완료.")
        return {"symbol": symbol, "analysis_report": final_answer}

    except Exception as e:
        logger.error(f"'/analyze' 엔드포인트 처리 중 오류 발생: {e}", exc_info=True)
        # 클라이언트에게 서버 내부 오류를 알립니다.
        raise HTTPException(status_code=500, detail="분석 중 서버 내부 오류가 발생했습니다.")


@app.get("/", summary="API 상태 확인", description="API 서버가 정상적으로 실행 중인지 확인합니다.")
def read_root():
    return {"status": "AI Stock Analyzer API is running."}