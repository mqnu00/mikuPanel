import asyncio
import socket
import platform
import datetime
import cpuinfo
import psutil
import distro

def bytes_to_MiB(num):
    return num / 1024 / 1024


def bytes_to_GiB(num):
    return num / 1024 / 1024 / 1024


def GiB_to_Mib(num):
    return num * 1024


def MiB_to_GiB(num):
    return num / 1024

class SysInfo:

    @staticmethod
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

    @staticmethod
    def get_cpu_per(interval=0.5):
        value = psutil.cpu_percent(interval=interval)
        if value == 0:
            value = psutil.cpu_percent(interval=0.1)
        return {'percent': value}

    @staticmethod
    def get_memory_info():
        return {
            "memoryTotal": bytes_to_GiB(psutil.virtual_memory().total)
        }

    @staticmethod
    def get_memory_per():
        # 获取内存使用情况
        mem = psutil.virtual_memory()
        # 使用中的内存
        used = bytes_to_GiB(mem.used)
        # 空闲内存
        free = bytes_to_GiB(mem.free)
        return {
            "used": used,
            "free": free,
            "percent": mem.percent
        }

    @staticmethod
    async def get_disk_per():

        # 获取磁盘IO统计信息

        # 打印获取到的磁盘IO信息
        # print("读IO数:", io_stats.read_count)
        # print("写IO数:", io_stats.write_count)
        last_read, last_write = psutil.disk_io_counters().read_bytes, psutil.disk_io_counters().write_bytes
        await asyncio.sleep(1)
        now_read, now_write = psutil.disk_io_counters().read_bytes, psutil.disk_io_counters().write_bytes
        # print("磁盘读时间:", io_stats.read_time)
        # print("磁盘写时间:", io_stats.write_time)
        # print(now_read - last_read, now_write - last_write)
        return {
            "read": now_read - last_read,
            "write": now_write - last_write
        }

    @staticmethod
    def network_info():
        io_stats = psutil.net_io_counters()
        return {
            "send": io_stats.bytes_sent,
            "recv": io_stats.bytes_recv,
        }

    @staticmethod
    def get_system_info():
        # 获取主机名称
        host_name = socket.gethostname()

        # 获取发行版本
        distribution = distro.name() if distro.name() else "Unknown"

        # 获取内核版本
        kernel_version = platform.release()

        # 获取系统类型
        machine_type = platform.machine()

        # 获取主机地址
        host_ip = socket.gethostbyname(socket.gethostname())

        # 获取启动时间
        start_time = datetime.datetime.fromtimestamp(psutil.boot_time())

        # 获取运行时间
        now = datetime.datetime.now()
        runtime = now - start_time
        runtime_days = runtime.days
        runtime_hours = runtime.seconds // 3600
        runtime_minutes = (runtime.seconds % 3600) // 60
        runtime_seconds = runtime.seconds % 60

        # 将系统信息存储在字典中
        system_info = {
            "主机名称": host_name,
            "发行版本": distribution,
            "内核版本": kernel_version,
            "系统类型": machine_type,
            # "主机地址": host_ip,
            "启动时间": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "运行时间": f"{runtime_days}天 {runtime_hours}小时 {runtime_minutes}分钟 {runtime_seconds}秒"
        }

        return system_info


if __name__ == '__main__':
    print(SysInfo.get_system_info())
    # print(get_cpu_info())
