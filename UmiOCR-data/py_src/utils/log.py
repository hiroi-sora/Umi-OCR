"""
日志模块

from utils.log import log

log.debug("调试信息")
log.info("普通信息")
log.warning("警告信息")
log.error("错误信息"))
log.critical("严重错误信息")
log.custom("自定义信息")

# exc_info 只能在 except 块中开启
log.error("错误信息", exc_info=True, stack_info=True)
# 覆盖 LogRecord 的属性
log.debug("信息", extra={"cover": {"level": logging.ERROR, "filename": "11111"}}
"""

import os
import json
import logging
from threading import Lock
from datetime import datetime
from logging.handlers import RotatingFileHandler
from logging import LogRecord


# json 文件处理器
class _JsonRotatingFileHandler(RotatingFileHandler):
    # 日志信息转字典
    def _record_to_dict(self, record: LogRecord):
        # 时间戳格式化
        dt_object = datetime.fromtimestamp(record.created)
        formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
        # 构造消息字典
        log_dict = {
            # 时间
            "time": formatted_time,
            # 日志级别 ( DEBUG, INFO, WARNING, ERROR, CRITICAL )
            "level": record.levelname,
            # 日志消息
            "message": record.getMessage(),
            # =====
            # 代码所在文件
            "filename": record.filename,
            # 代码行号
            "lineno": record.lineno,
            # 模块名
            "module": record.module,
            # 函数名
            "funcName": record.funcName,
            # 异常信息，需在 except 块中开启 exc_info=True
            "exc_text": record.exc_text,
            # 堆栈信息，需开启 stack_info=True
            "stack_info": record.stack_info,
            # =====
            # 线程标识符
            "thread": record.thread,
            # 线程名称
            "threadName": record.threadName,
            # 进程标识符
            "process": record.process,
            # 进程名称
            "processName": record.processName,
            # 日志记录器的名称
            "name": record.name,
        }
        return log_dict

    # 发送日志
    def emit(self, record):
        # 处理信息
        try:
            # 提取自定义信息，覆盖给 record
            cover = record.__dict__.get("cover", {})
            for k, v in cover.items():
                if hasattr(record, k):
                    setattr(record, k, v)
            # 提取字典
            log_dict = self._record_to_dict(record)
        except Exception:
            self.handleError(record)
        # 输出到日志文件
        try:
            with open(self.baseFilename, "a", encoding=self.encoding) as f:
                json.dump(log_dict, f, ensure_ascii=False)
                f.write("\n")
        except Exception:
            self.handleError(record)


# 日志记录器 管理类
class _LogManager:

    # 日志目录路径
    _log_dir = "./logs"
    # 确保线程安全的锁
    _lock = Lock()

    @staticmethod  # 控制台处理器
    def _get_console_handler():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        fmt = "%(asctime)s %(levelname)s | %(message)s"
        formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")
        console_handler.setFormatter(formatter)
        return console_handler

    @staticmethod  # json处理器，输出到本地文件及UI
    def _get_json_handler():
        # 确保日志目录存在
        if not os.path.exists(_LogManager._log_dir):
            os.makedirs(_LogManager._log_dir)
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        # 构造错误日志文件路径
        log_file = os.path.join(_LogManager._log_dir, f"{current_date}.jsonl.txt")
        # 创建json处理器
        json_handler = _JsonRotatingFileHandler(
            log_file,
            mode="a",  # 追加写入
            maxBytes=10485760,  # 单个文件最大：10MB
            backupCount=3,  # 文件备份数量
            encoding="utf-8",  # 文件编码
            delay=True,  # 延迟创建文件
        )
        json_handler.setLevel(logging.DEBUG)
        return json_handler

    @staticmethod
    def create_logger(name):
        """创建并返回一个新的日志记录器。"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_LogManager._get_console_handler())
        logger.addHandler(_LogManager._get_json_handler())
        return logger


# 全局单例日志记录器
log = _LogManager.create_logger("Umi-OCR")


"""
log.debug(
    "测试",
    extra={
        "cover": {
            "level": logging.ERROR,
            "filename": "112213321231",
            "lineno": 999,
        }
    },
)
"""
