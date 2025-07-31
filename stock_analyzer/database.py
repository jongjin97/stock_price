from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from .models import Base
import logging

logger = logging.getLogger(__name__)


# 데이터베이스 엔진 생성
engine = create_engine(settings.DATABASE_URL, echo=True)

# 데이터베이스 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    데이터베이스를 초기화하고 모든 테이블을 생성합니다.
    애플리케이션 시작 시 한 번만 호출합니다.
    """
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization completed.")

def get_db():
    """
    데이터베이스 세션 객체를 제공하는 Dependency
    이 함수를 통해 세션을 얻고, 작업이 끝나면 세션을 자동으로 닫습니다.
    데이터를 DB에 추가/수정/삭제하는 작업 시 사용합니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()