import cpuinfo
import psutil


class CpuInfo:

    def __init__(self, cpu_name, cpu_core, cpu_thread, cpu_freq):
        self.cpu_name = cpu_name
        self.cpu_core = cpu_core
        self.cpu_thread = cpu_thread
        self.cpu_freq = cpu_freq


def get_cpu_info():
    cpu_name: str = cpuinfo.get_cpu_info()['brand_raw']
    cpu_core = psutil.cpu_count(logical=False)
    cpu_thread = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq().max
    return CpuInfo(cpu_name, cpu_core, cpu_thread, cpu_freq)


if __name__ == '__main__':
    print(get_cpu_info())
