import psutil


class MemoryInfo(object):

    def __init__(self, memory_total: float):
        self.memory_total = memory_total


def get_memory_info():
    return MemoryInfo(psutil.virtual_memory().total)


if __name__ == '__main__':
    print(get_memory_info().memory_total)
