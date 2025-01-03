import cpuinfo
import psutil


def get_cpu_info():
    cpu_name: str = cpuinfo.get_cpu_info()['brand_raw']
    cpu_core = psutil.cpu_count(logical=False)
    cpu_thread = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq().max
    return {
        "cpuName": cpu_name,
        "cpuCore": cpu_core,
        "cpuThread": cpu_thread,
        "cpuFreq": cpu_freq
    }


def get_cpu_per():
    value = psutil.cpu_percent()
    if value == 0:
        value = psutil.cpu_percent()
    return value


if __name__ == '__main__':
    print(get_cpu_info())
    print(get_cpu_per())