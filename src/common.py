import logging
from datetime import datetime
from pathlib import Path


# 프로젝트 전체에서 사용하는 시간 표현 규칙을 한 곳에서 관리합니다.
# 로깅뿐만 아니라 추후 checkpoint, 파일명, 실행 이력 등에서도
# 동일한 시간 형식을 사용할 수 있도록 공통 함수로 분리합니다.
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_logger():
    # 프로젝트에서 공통으로 사용할 logger를 생성합니다.
    logger = logging.getLogger("book-data-pipeline")
    logger.setLevel(logging.INFO)

    # 여러 모듈에서 get_logger()를 호출하더라도
    # 동일한 handler가 중복으로 등록되는 것을 방지합니다.
    if logger.handlers:
        return logger

    # 현재 파일을 기준으로 프로젝트 루트 경로를 계산합니다.
    project_root = Path(__file__).resolve().parent.parent

    # 프로젝트 루트 하위의 logs 디렉토리에 로그 파일을 저장합니다.
    # 디렉토리가 존재하지 않는 경우 자동으로 생성합니다.
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 애플리케이션은 하나의 고정된 로그 파일에만 기록합니다.
    # 로그 파일의 rotation, 압축, 보관 정책은 logrotate가 담당합니다.
    log_path = log_dir / "book-data-pipeline.log"

    # 프로젝트 공통 시간 규칙인 get_timestamp()를 직접 사용하기 위해
    # logging formatter에서는 전달받은 메시지만 그대로 출력합니다.
    formatter = logging.Formatter("%(message)s")

    # 로그를 터미널에도 출력합니다.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 동일한 로그를 고정된 로그 파일에도 저장합니다.
    # 실제 로그 rotation은 애플리케이션에서 수행하지 않고,
    # 운영 환경에서 logrotate 등을 통해 처리할 수 있도록 구성합니다.
    file_handler = logging.FileHandler(
        log_path,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # 하나의 logger에서 터미널 출력과 파일 저장을 동시에 수행합니다.
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()


def log_info(message):
    logger.info(
        f"[{get_timestamp()}] [INFO] {message}"
    )


def log_warning(message):
    logger.warning(
        f"[{get_timestamp()}] [WARNING] {message}"
    )


def log_error(message):
    logger.error(
        f"[{get_timestamp()}] [ERROR] {message}"
    )