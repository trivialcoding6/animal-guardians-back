import logging
import sys
from typing import List
from loguru import logger
from app.core.config import settings

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    # 기본 로깅 핸들러 설정
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # 기존 로거 설정 제거
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # loguru 설정
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            },
            {
                "sink": "logs/app.log",
                "rotation": "00:00",  # 매일 자정에 로그 파일 교체
                "compression": "zip",  # 이전 로그 파일 압축
                "retention": "30 days",  # 30일간 보관
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            },
        ]
    )