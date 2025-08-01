import  logging
from typing import Set, Dict, List
from sqlalchemy.orm import Session
from stock_analyzer.database import SessionLocal
from stock_analyzer.models import Stock, News
from datetime import datetime
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

def get_urls_by_symbol(symbol: str) -> Set[str]:
    """
    주어진 심볼에 해당하는 모든 뉴스의 URL을 데이터베이스에서 조회합니다.

    Args:
        symbol (str): 조회할 주식 심볼 (예: '"APL").

    Returns:
        Set[str]: 해당 심볼의 모든 뉴스 URL을 담은 집합.
    """
    db: Session = SessionLocal()
    urls = set()
    try:
        # symbole을 사용하여 stock_id를 찾습니다.
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.warning(f"DB에 '{symbol}' 심볼이 존재하지 않아 URL을 조회할 수 없습니다.")
            return urls
        
        # 찾은 stock_id를 사용하여 모든 뉴스 URL을 조회합니다.
        results = db.query(News.url).filter(News.stock_id == stock.stock_id).all()
        # 쿼리 결과는 튜플 리스트이므로, 각 튜플의 첫 번째 요소(URL)만 추출합니다.
        urls = {result[0] for result in results}
        logger.info(f"'{symbol}'에 대한 {len(urls)}개의 기존 URL을 DB에서 찾았습니다.")
        return urls
    except Exception as e:
        logger.error(f"'{symbol}'의 URL 조회 중 DB 오류 발생: {e}", exc_info=True)
        return urls # 오류 발생 시 빈 집합 반환
    finally:
        db.close()

def save_news_articles(news_list: List[Dict], symbol: str):
    """
    여러개의 새로운 뉴스 데이터를 데이터베이스에 한 번에 저장합니다.

    Args:
        news_list (List[Dcit]): 각 딕셔너리는 'title', 'content', 'url', 'upload_time' 키를 포함해야 합니다.
        symbol str: 주식 심볼
    """
    db: Session = SessionLocal()
    try:
        for news_item in news_list:
            # symbol을 사용하여 stock_id를 찾습니다.
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                logger.error(f"뉴스 저장 실패: '{symbol}' 심볼을 DB에서 찾을 수 없습니다.")
                continue

            # 날짜 파싱
            upload_time_str = news_item.get('upload_time')
            upload_time_obj = datetime.now() # 기본값은 현재 시간

            if upload_time_str:
                try:
                    # '2025-07-31T12:31:00.000Z' 형식에 맞는 포맷으로 수정
                    # .%f는 마이크로초를, Z는 UTC 시간대를 의미합니다.
                    upload_time_obj = datetime.strptime(upload_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    logger.warning(f"날짜 형식 파싱 실패: '{upload_time_str}'. 현재 시간으로 대체합니다.")


            # 새로운 News 객체를 생성
            new_article = News(
                stock_id=stock.stock_id,
                title=news_item.get('title', 'N/A'),
                content=news_item.get('content', 'N/A'),
                url=news_item.get('url', 'N/A'),
                news_upload_time=upload_time_obj
            )
            db.add(new_article)

        db.commit()
        logger.info(f"총 {len(news_list)}개의 뉴스 항목을 DB에 저장했습니다.")
    except Exception as e:
        logger.error(f"뉴스 저장 중 오류 발생: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

def crawl_full_content(url: str) -> Dict:
    """
    주어진 URL에서 뉴스의 상세 내용(제목, 본문, 발행일시 등)을 크롤링합니다.

    Args:
        url (str): DB에 저장되지 않는 뉴스의 URL

    Returns:
        Dict: 뉴스의 상세 내용(제목, 본문, 발행일시 등
    """
    logger.info(f"상세 내용 크롤링 시작: {url}")
    request_url = "https://www.stocktitan.net" + url

    response = requests.get(request_url)
    if response.status_code != 200:
        logger.error(f"URL {url}에 접근 중 네트워크 오류 발생: {response.status_code}")
        raise Exception(f"URL {url}에 접근 중 네트워크 오류 발생: {response.status_code}")
    
    # 뉴스 페이지의 BeautifulSoup 객체를 반환합니다.
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스의 symbol을 추출합니다.

    # 뉴스 페이지의 article 객체를 추출합니다.
    article_soup = soup.find("article", class_="article")

    # 뉴스의 특정 div를 제거합니다.
    tool_divs = article_soup.find("div", class_="article-rhea-tools")
    if tool_divs:
        tool_divs.decompose()
    
    # 뉴스의 업로드 시간을 추출합니다.
    article_time = soup.find("time")['datetime'].strip()

    # 뉴스의 제목을 추출합니다.
    article_title = soup.find("h1", class_="article-title").text

    # 뉴스의 본문을 추출합니다.
    content = soup.find_all("p")
    article_content = ""
    for paragraph in content:
        article_content += paragraph.get_text().strip() + "\n"

    return {
        "title": article_title,
        "content": article_content,
        "upload_time": article_time,
        "url": url,
    }