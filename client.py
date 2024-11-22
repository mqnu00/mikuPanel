import asyncio

import grpc.aio
from grpcService import sysInfo_pb2_grpc, sysInfo_pb2


async def run():
    async with grpc.aio.insecure_channel("127.0.0.1:50052") as channel:
        stub = sysInfo_pb2_grpc.SysInfoServiceStub(channel)

        async def do_chat():
            response = await stub.sysInfoService(sysInfo_pb2.CpuRequest())
            print(response)

        await do_chat()


if __name__ == '__main__':
    asyncio.run(run())
