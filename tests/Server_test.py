import httpx

# 目标WebSocket服务端的URI
uri = "http://localhost:6444"

# 故意不包含WebSocket所需的头信息
headers = {
    "Host": "localhost:8000",
    "Upgrade": "websocket",
    # 故意省略了Sec-WebSocket-Key和Sec-WebSocket-Version头
}


# 发送不完整的WebSocket升级请求
async def send_incomplete_request():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(uri, headers=headers, timeout=5.0)
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


# 运行异步函数
import asyncio

asyncio.run(send_incomplete_request())
