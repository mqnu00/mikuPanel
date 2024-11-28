import psutil
from utils.sysInfo.convert import bytes_to_GiB


def get_memory_info():
    return {
        "memoryTotal": bytes_to_GiB(psutil.virtual_memory().total)
    }


def get_memory_per():
    # 获取内存使用情况
    mem = psutil.virtual_memory()
    # 使用中的内存
    used = bytes_to_GiB(mem.used)
    # 空闲内存
    free = bytes_to_GiB(mem.free)
    return used, free, mem.percent


if __name__ == '__main__':
    print(get_memory_info())
    print(get_memory_per())
