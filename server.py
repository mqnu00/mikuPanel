import asyncio
import json
import logging
import time

import grpc
import psutil

from grpcService import sysInfo_pb2_grpc, sysInfo_pb2
from concurrent import futures
from sysInfo import cpu, memory

INTERVAL = 1


def get_cpu_per():
    return psutil.cpu_percent(interval=INTERVAL)


class sysInfoService(sysInfo_pb2_grpc.SysInfoServiceServicer):
    async def cpuService(self, request: sysInfo_pb2.CpuRequest, context):
        while True:
            yield sysInfo_pb2.CpuReply(usage=get_cpu_per())

    async def sysInfoService(self, request: sysInfo_pb2.SysInfoRequest, context):
        return sysInfo_pb2.SysInfoReply(
            cpuInfo=cpu.get_cpu_info(),
            memoryInfo=memory.get_memory_info()
        )


async def serve():
    server = grpc.aio.server()
    sysInfo_pb2_grpc.add_SysInfoServiceServicer_to_server(sysInfoService(), server)
    server.add_insecure_port('[::]:50052')
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(process)d - %(threadName)s - %(filename)s - %(funcName)s - Line %(lineno)d - %(message)s'
    )
    asyncio.run(serve())
