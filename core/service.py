import multiprocessing
from enum import Enum
from typing import ClassVar, List

from rx.subject import Subject
from rx import operators as ops
from transitions import Machine, EventData
from utils.log_util import log


class ServiceState(Enum):
    IDLE = 1
    PENDING = 2
    WORKING = 3
    DONE = 4
    CONFIG = 5
    ERROR = 6


class Service(object):
    _initial_state: ClassVar[ServiceState] = ServiceState.IDLE
    _transitions: ClassVar[List] = [
        {
            'trigger': 'config',
            'source': [ServiceState.IDLE, ServiceState.PENDING, ServiceState.WORKING],
            'dest': ServiceState.CONFIG,
        },
        {
            'trigger': 'pend',
            'source': [ServiceState.CONFIG, ServiceState.WORKING],
            'dest': ServiceState.PENDING,
            'conditions': 'is_config'
        },
        {
            'trigger': 'work',
            'source': ServiceState.PENDING,
            'dest': ServiceState.WORKING
        },
        {
            'trigger': 'done',
            'source': ServiceState.WORKING,
            'dest': ServiceState.DONE
        },
        {
            'trigger': 'error',
            'source': '*',
            'dest': 'error',
            'after': '_error'
        }
    ]

    def __init__(self):
        self.obs = Subject()
        self.obs.subscribe(lambda msg: log.info(f'{msg}'))

    def _config(self):
        pass

    def consumer(self):
        pass

    def productor(self):
        pass

    def handle(self):
        pass

    def state_change(self, event: EventData):
        self.obs.on_next(event.state.value)

    @classmethod
    def create(cls, *args, **kwargs):
        service = cls(*args, **kwargs)
        machine = Machine(
            model=service,
            states=ServiceState,
            transitions=cls._transitions,
            initial=cls._initial_state,
            send_event=True,
            queued=True,
            after_state_change=service.state_change,
        )
        # machine.on_enter_CONNECTING('_connect')
        return service


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
    # main()
    service = Service.create()
    service.config()
    service.done()