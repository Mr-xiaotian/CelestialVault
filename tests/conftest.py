# # conftest.py
# from loguru import logger
# import logging
# import pytest

# class InterceptHandler(logging.Handler):
#     def emit(self, record):
#         # 获取原始日志的日志级别
#         level = logger.level(record.levelname).name
#         # 使用 loguru 记录器根据不同的日志级别来处理日志
#         logger.log(level, record.getMessage())

# def pytest_configure(config):
#     # 移除所有已存在的 loguru 处理器
#     logger.remove()
#     # 添加一个转发到标准 logging 模块的处理器
#     logger.add(InterceptHandler(), format="{time} {level} {message}")

# @pytest.fixture(autouse=True)
# def set_loguru_level():
#     logger.enable("__main__")  # Enable logging for the main module
