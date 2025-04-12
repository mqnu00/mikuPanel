import os
from datetime import datetime
from typing import List

from utils.log_util import log


class LogReader:
    def __init__(self):
        # 获取环境变量中的日志目录路径
        self.log_dir = os.getenv('LOG_PATH', './logs')
    def get_log_file_path(self) -> str:
        """
        根据当前日期生成日志文件的路径。
        :return: 日志文件的完整路径
        """
        # 获取当前日期并格式化为字符串
        current_date = datetime.now().strftime('%Y-%m-%d')
        # 拼接日志文件路径
        log_file_name = f"{current_date}.log"
        log_file_path = os.path.join(self.log_dir, log_file_name)
        return log_file_path

    def read_log(self, path: str = None):
        """
        读取日志文件的最后100行。
        :param path: 日志文件路径，默认使用当前日期的日志文件
        :return: 日志内容的列表，每行日志为一个元素
        """
        if path is None:
            path = self.get_log_file_path()

        try:
            log.exception("???")
            with open(path, 'r', encoding='utf-8') as file:
                # 读取所有行并保留最后100行
                lines = file.readlines()
                log_lines = lines[-100:]


            return {
                "logs": log_lines
            }
        except FileNotFoundError:
            log.info(f"Error: The file '{path}' does not exist.")
            return []
        except Exception as e:
            log.info(f"An error occurred while reading the log file: {e}")
            return []

# 示例用法
if __name__ == "__main__":
    import env_loader
    pass
    # log_reader = LogReader()
    # logs = log_reader.read_log()
    # for log in logs:
    #     print(log.strip())