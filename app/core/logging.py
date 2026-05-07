# app/core/logging.py
import logging
import sys


def configure_logging() -> None:
    """تنظیمات logging مرکزی پروژه"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # کاهش سطح لاگ کتابخانه‌های شلوغ
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("rq.worker").setLevel(logging.WARNING)


# Alias برای backward compatibility با main.py
setup_logging = configure_logging
