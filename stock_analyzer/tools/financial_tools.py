import logging
import yfinance as yf
import pandas as pd
from typing import Dict
from langchain.tools import Tool

logger = logging.getLogger(__name__)

def get_financial_statements(symbol: str) -> Dict[str, str]:
    """주어진 주식 심볼에 대한 재무제표 데이터를 문자열 딕셔너리 형태로 가져옵니다.
    최근 4분기의 재무상태표, 손익계산서, 현금흐름표를 반환합니다.

    Args:
        symbol (str): 주식 심볼 (e.g., "AAPL").

    Returns:
        Dict[str, str]: 각 제무제표의 문자열 버전을 답은 딕셔너리.
            Key: 'income', 'balance', 'cashflow'.
            데이터를 가져오지 못함녀 빈 딕셔너리를 반환합니다.
    """
    try:
        logger.info(f"'{symbol}'의 재무제표 데이터를 yfinance에서 가져옵니다.")
        ticker = yf.Ticker(symbol)

        # 각 재무제표의 최근 4분기 데이터 가져오기
        income_stmt_df = ticker.income_stmt.iloc[:, :4]
        balance_sheet_df = ticker.balance_sheet.iloc[:, :4]
        cash_flow_df = ticker.cashflow.iloc[:, :4]

        logger.info(f"'{symbol}' 데이터 수집 완료. 문자열로 변환합니다.")

        # DataFrame을 GraphState에 저장하기 용이한 문자열로 변환
        statements_as_strings = {
            "income_statement": income_stmt_df.to_string(),
            "balance_sheet": balance_sheet_df.to_string(),
            "cash_flow": cash_flow_df.to_string()
        }

        return statements_as_strings
    
    except Exception as e:
        logger.error(f"'{symbol}'의 재무제표 데이터를 가져오는 중 오류 발생: {e}", exc_info=True)
        return {}
    
financial_statement_tool = Tool(
    name="financial_statement_fetcher",
    func=get_financial_statements,
    description="""
    특정 주식 심볼(symbol)의 가장 최신 4분기 재무제표(재무상태표, 손익계산서, 현금흐름표)를 가져옵니다.
    이 도구는 주식의 펀더멘털을 분석할 때 필수적입니다.
    """
)