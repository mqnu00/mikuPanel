from enum import Enum
from typing import ClassVar, List
from rx.subject import Subject
from transitions import Machine, EventData
from utils.log_util import log


class MissionState(Enum):
    IDLE = 1
    CONFIG = 2
    READY = 3
    BROKEN = 4
    BUSY = 5
    SHUTDOWN = 6


class Mission(object):
    _initial_state: ClassVar[MissionState] = MissionState.IDLE
    _transitions: ClassVar[List] = [
        {
            'trigger': 'config',
            'source': MissionState.IDLE,
            'dest': MissionState.CONFIG,
            'after': '_config',
        },
        {
            'trigger': 'done',
            'source': MissionState.CONFIG,
            'dest': MissionState.READY,
            'conditions': 'is_config'
        },
        {
            'trigger': 'done',
            'source': MissionState.CONFIG,
            'dest': MissionState.BROKEN,
            'unless': 'is_config'
        },
        {
            'trigger': 'action',
            'source': MissionState.READY,
            'dest': MissionState.BUSY,
        },
        {
            'trigger': 'action_done',
            'source': MissionState.BUSY,
            'dest': MissionState.READY,
        },
        {
            'trigger': 'stop',
            'source': '*',
            'dest': MissionState.SHUTDOWN,
        },
    ]

    def __init__(self):
        self.obs = Subject()
        self.obs.subscribe(
            on_next=lambda info: log.info('mission状态切换为：info')
        )
        pass

    def state_change(self, event: EventData):
        self.obs.on_next(event.event.name)
        pass

    def _config(self, event: EventData):
        pass

    def is_config(self):
        pass

    @classmethod
    def create(cls):
        mission = cls()
        Machine(
            mission,
            states=MissionState,
            transitions=cls._transitions,
            initial=cls._initial_state,
            send_event=True,
            after_state_change=mission.state_change,
        )
        return mission