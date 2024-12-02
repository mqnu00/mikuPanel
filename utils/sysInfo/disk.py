import asyncio
from utils.sysInfo.convert import bytes_to_MiB


async def get_disk_per():
    import psutil

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
    return bytes_to_MiB(now_read - last_read), bytes_to_MiB(now_write - last_write)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_disk_per())
