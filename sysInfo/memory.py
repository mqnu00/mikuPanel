import psutil


def get_memory_info():
    return {
        "memoryTotal": psutil.virtual_memory().total
    }


if __name__ == '__main__':
    print(get_memory_info())
