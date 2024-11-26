import psutil


def get_memory_info():
    return {
        "memoryTotal": psutil.virtual_memory().total / 1024 / 1024 / 1024
    }


def get_memory_per():
    # 获取内存使用情况
    mem = psutil.virtual_memory()
    # 使用中的内存
    used = mem.used / 1024 / 1024 / 1024
    # 空闲内存
    free = mem.free / 1024 / 1024 / 1024
    return used, free, mem.percent


if __name__ == '__main__':
    print(get_memory_info())
    print(get_memory_per())
