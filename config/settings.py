import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일의 경로를 프로젝트 루트 디렉토리로 설정
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# OpenAI API KEY
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 데이터베이스 종류 (e.g., "mysql", "sqlite")
DB_TYPE = os.getenv("DB_TYPE")

# 데이터베이스 연결 정보
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"{DB_TYPE}+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 디버그 유무 MODE의 값이 debug일 시 True 반환
MODE = os.getenv("MODE")
DEBUG = MODE == "debug"


# 로그 파일 경로
LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_FILE_PATH = LOGS_DIR / 'app.log'

# 로그 디렉토리가 없으면 생성
LOGS_DIR.mkdir(exist_ok=True)

