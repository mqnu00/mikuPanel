import asyncio
import multiprocessing
import threading
import traceback
from enum import Enum
from typing import ClassVar, List

from rx.subject import Subject
from rx import operators as ops
from transitions import Machine, EventData

from core.LoopManager import Loop
from core.communication import Message
from utils.log_util import log


class ServiceState(Enum):
    IDLE = 1
    PENDING = 2
    WORKING = 3
    DONE = 4
    CONFIG = 5
    ERROR = 6


# todo state_change
class Service(object):
    _initial_state: ClassVar[ServiceState] = ServiceState.IDLE
    _transitions: ClassVar[List] = [
        {
            'trigger': 'config',
            'source': [ServiceState.IDLE, ServiceState.PENDING, ServiceState.WORKING],
            'dest': ServiceState.CONFIG,
            'after': '_config'
        },
        {
            'trigger': 'pending',
            'source': [ServiceState.CONFIG, ServiceState.WORKING],
            'dest': ServiceState.PENDING,
        },
        {
            'trigger': 'working',
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
            'dest': ServiceState.ERROR,
            'after': '_error'
        }
    ]

    def __init__(self, loop: Loop):
        self.messages: dict[str: Message] = {}
        self.is_config = False
        self.loop = loop
        self.obs = Subject()
        self.obs.subscribe(lambda state: log.info(f'{state}'))

    def _config(self, event: EventData):
        pass

    def _pending(self, event: EventData):
        pass

    def _working(self, event: EventData):
        pass

    def _error(self, event):
        pass

    def start(self):
        self.config()

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
        machine.on_enter_PENDING('_pending')
        machine.on_enter_WORKING('_working')
        machine.on_enter_ERROR('_error')
        return service


if __name__ == "__main__":
    # main()
    loop = Loop.create(thread_name=threading.current_thread().name)
    service = Service.create(loop)
    service.start()
