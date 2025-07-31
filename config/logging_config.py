import logging.config
from . import settings

def setup_logging():
    """
    프로젝트 전체에 적용될 로깅 설정을 구성하고 적용
    main.py에서 애플리케이션 시작 시 한 번만 호출
    """
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        # 로그 출력 형식 정의
        "formatters": {
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "[%(levelname)s] %(message)s",
            },
        },
        #로그를 처리하는 방법 정의 (콘솔, 파일 등)
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": settings.LOG_FILE_PATH,
                "maxBytes": 1024 * 1024 * 10,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        # 어떤 로거를 사용할지 정의 (root 로거는 모든 로거의 기본 설정)
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        
        }
    }
    logging.config.dictConfig(LOGGING_CONFIG)