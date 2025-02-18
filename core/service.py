import multiprocessing
from rx.subject import Subject
from rx import operators as ops

# 定义一个消费者函数
def consumer(data):
    print(f"Consumer received: {data}")
    return data.upper()  # 示例处理：将字符串转为大写

# 定义一个观察者进程
def observer(queue):
    while True:
        data = queue.get()  # 从队列中获取数据
        if data is None:  # 使用 None 作为结束信号
            break
        return data  # 将数据传递回主进程

# 主函数
def main():
    # 创建一个 multiprocessing Queue
    queue = multiprocessing.Queue()

    # 创建一个 Subject
    subject = Subject()

    # 订阅 Subject，并应用 filter 和消费者函数
    subscription = subject.pipe(
        ops.filter(lambda x: "3" not in x),  # 示例过滤：忽略包含 "3" 的消息
        ops.map(consumer)  # 示例处理：将字符串转为大写
    ).subscribe(
        on_next=lambda x: print(f"Processed message: {x}"),
        on_error=lambda error: print(f"Error occurred: {error}"),
        on_completed=lambda: print("Queue processing completed")
    )

    # 启动一个生产者进程
    producer_process = multiprocessing.Process(target=producer, args=(queue,))
    producer_process.start()

    # 主进程处理队列数据并传递给 Subject
    while True:
        data = queue.get()
        if data is None:
            break
        subject.on_next(data)

    # 等待生产者进程结束
    producer_process.join()

    # 取消订阅
    subscription.dispose()

# 定义一个生产者进程
def producer(queue):
    for i in range(5):
        queue.put(f"Message {i}")
        print(f"Producer sent: Message {i}")
    queue.put(None)  # 发送结束信号

if __name__ == "__main__":
    main()