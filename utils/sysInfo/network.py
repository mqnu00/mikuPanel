import asyncio

import psutil
from utils.sysInfo import convert


def networkInfo():
    io_stats = psutil.net_io_counters()
    return convert.bytes_to_GiB(io_stats.bytes_sent), convert.bytes_to_GiB(io_stats.bytes_recv)


async def get_network_per():
    last_send, last_recv = networkInfo()
    await asyncio.sleep(1)
    now_send, now_recv = networkInfo()
    return convert.GiB_to_Mib(now_send - last_send), convert.GiB_to_Mib(now_recv - last_recv)


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_network_per())
    # asyncio.run(network())