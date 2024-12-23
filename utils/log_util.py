import multiprocessing
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime


def setup_logger(
        name,
        level=logging.INFO,
        is_console: bool = True,
        is_file: bool = True,
        log_dir: str = None,
        encoding: str = 'utf8',
        max_bytes: int = 2 * 1024 * 1024,  # 最大文件大小2MB
        backup_count: int = 15,  # 保留最多15个备份
        use_gzip: bool = True  # 是否压缩旧日志
) -> logging.Logger:
    """
    创建一个指定服务的日志记录器。
    线程安全，进程不安全
    :param name: 日志记录器名称
    :param level: 日志级别
    :param is_console: 是否使用控制台输出
    :param is_file: 是否使用文件输出
    :param log_dir: 日志文件路径
    :param encoding: log文件编码
    :param max_bytes: 每个日志文件的最大字节大小
    :param backup_count: 最多备份多少个日志文件
    :param use_gzip: 是否对旧日志进行gzip压缩
    """
    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 创建日志格式器
    formatter = logging.Formatter(
        '|%(asctime)s|%(levelname)s|pid: %(process)d|tid: %(thread)s|%(filename)s|%(funcName)s|Line %(lineno)d|%(message)s|',
        datefmt='%Y-%m-%d %H:%M:%S'  # 时间格式，不包含毫秒
    )

    if is_console:
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if is_file:
        if log_dir:
            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)

            log_file_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

            # 使用TimedRotatingFileHandler进行日志文件滚动
            handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, encoding=encoding)
            handler.suffix = "%Y-%m-%d"  # 文件名后缀（日期）

            # 设置最大文件大小和备份数量
            handler.maxBytes = max_bytes
            handler.backupCount = backup_count

            # 压缩旧的日志文件
            if use_gzip:
                handler.extMatch = r"^\d{4}-\d{2}-\d{2}.gz$"

            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    return logger


log = setup_logger(
    name=multiprocessing.current_process().name,
    log_dir='./logs'
)
log.info(log.name)

# 示例：使用 logger
if __name__ == "__main__":
    # 配置日志
    log_dir = "logs"  # 设置日志目录路径
    logger = setup_logger("my_service", log_dir=log_dir)

    # 打印一些日志
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.error("This is an error message.")
