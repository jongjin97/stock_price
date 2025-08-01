from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime,
    ForeignKey, BigInteger, Enum as SQLAlchemyEnum, DECIMAL
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, declarative_base
import enum

# SQLAlchemy Base 클래스 생성
Base = declarative_base()

# 분석 결과 예측을 위한 Enum 정의
class PredictionEnum(enum.Enum):
    RISE = "RISE",
    FALL = "FALL",
    NEUTRAL = "NEUTRAL"

class Stock(Base):
    """
    주식의 기본 정보를 저장하는 테이블 모델.
    SQL 스키마에 맞춰 stock_id를 기본 키로 사용합니다.
    """
    __tablename__ = 'stock'
    stock_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(6), nullable=False, unique=True)
    exchange = Column(String(6), nullable=False)

    # 관계 설정: 하나의 주식은 여러 개의 뉴스와 재무제표를 가질 수 있음
    news = relationship("News", back_populates="stock")

class News(Base):
    """
    수집된 뉴스 기사 데이터를 저장하는 테이블 모델.
    SQL 스키마에 맞춰 컬럼명과 관계를 수정했습니다.
    """
    __tablename__ = 'news'
    news_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    content = Column(LONGTEXT, nullable=False) # 긴 텍스트는 Text 타입이 더 유연합니다.
    url = Column(String(300), nullable=False, unique=True)
    stock_id = Column(Integer, ForeignKey("stock.stock_id"), nullable=False)
    news_upload_time = Column(DateTime, default=None)

    # 관계 설정: 뉴스는 하나의 주식과 하나의 분석 결과를 가짐
    stock = relationship("Stock", back_populates="news")
    analysis = relationship("AnalysisResults", back_populates="news_article", uselist=False, cascade="all, delete-orphan")

class AnalysisResults(Base):
    """
    AI의 분석 결과를 저장하는 테이블 모델.
    News 테이블과의 관계를 유지합니다.
    """
    __tablename__ = "analysis_results"
    
    analysis_id = Column(BigInteger, primary_key=True, autoincrement=True)
    # 외래 키를 news.news_id로 설정
    news_id = Column(Integer, ForeignKey("news.news_id"), nullable=False, unique=True)
    create_at = Column(DateTime, nullable=False)
    prediction = Column(SQLAlchemyEnum(PredictionEnum))
    reasoning = Column(Text)

    # 관계 설정: news_article 속성을 통해 News 모델과 연결
    news_article = relationship("News", back_populates="analysis")
