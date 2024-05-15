import sys, pytest
from loguru import logger
import logging



def test_log():
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    logger.info('"logger success"')
    print("print success")
    logging.info("logging success")

def test_logger():
    # 定义控制台输出的格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
        "<level>{level}</level> "
        "<cyan>{message}</cyan>"
    )

    # 定义文件输出的格式
    file_format = "{time:YYYY-MM-DD HH:mm:ss} {level} {message}"

    # 配置 logger
    logger.remove()  # 移除默认的日志输出

    # 添加控制台输出，并使用控制台格式
    logger.add(lambda msg: print(msg, end=""), format=console_format)

    # 添加文件输出，并使用文件格式
    logger.add("thread_manager.log", format=file_format)

    highlighted_message = "\033[1;31mThis part is red\033[0m and this part is normal."
    logger.info(f"This is an info message with highlighted part: {highlighted_message}")