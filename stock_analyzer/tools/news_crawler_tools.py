import logging
import requests
from bs4 import BeautifulSoup
from typing import List
from langchain.tools import Tool

# 로거 설정
logger = logging.getLogger(__name__)

def get_stock_soup(symbol: str) -> BeautifulSoup:
    """
    STOCK TITAN의 특정 기업 뉴스 페이지의 BeautifulSoup 객체를 반환합니다.
    """
    url = f"https://www.stocktitan.net/news/{symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # 200 OK가 아니면 예외를 발생시킵니다.
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logger.error(f"URL {url}에 접근 중 네트워크 오류 발생: {e}")
        raise


def get_stock_news_url(soup: BeautifulSoup) -> List[str]:
    """
    STOCK TITAN 주식 페이지에서 뉴스 URL을 추출합니다.
    최근 3개의 뉴스만 반환합니다.
    """
    news_links = soup.find_all("a", class_="feed-link")

    urls = [link['href'] for link in news_links]

    return urls[:3]

def fetch_latest_news_urls(symbol: str) -> List[str]:
    """
    주어진 심볼에 대해 StockTitan에서 최신 뉴스 URL 목록을 가져오는 메인 함수.
    두 헬퍼 함수를 호출하고 오류를 처리합니다.
    """
    try:
        logger.info(f"'{symbol}'의 최신 뉴스 URL 크롤링을 시작합니다...")
        soup = get_stock_soup(symbol)
        urls = get_stock_news_url(soup)
        logger.info(f"'{symbol}'에 대한 뉴스 URL {len(urls)}개를 성공적으로 가져왔습니다.")
        return urls
    except Exception as e:
        logger.error(f"'{symbol}'의 뉴스 URL을 가져오는 전체 과정에서 오류 발생: {e}", exc_info=True)
        # 오류 발생 시 빈 리스트를 반환하여 다음 단계에 영향을 주지 않도록 합니다.
        return []


# AI가 사용할 수 있는 LangChain Tool 객체로 생성
stock_news_url_crawler_tool = Tool(
    name="stock_news_url_crawler",
    func=fetch_latest_news_urls,
    description="""
    특정 주식 심볼(symbol)에 대한 최신 뉴스 기사의 URL 목록을 StockTitan 웹사이트에서 직접 크롤링할 때 사용합니다.
    데이터베이스의 뉴스를 최신화하거나, 가장 즉각적인 반응을 확인해야 할 때 유용합니다.
    """
)