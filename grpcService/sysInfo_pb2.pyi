from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class cpuRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class cpuReply(_message.Message):
    __slots__ = ("usage",)
    USAGE_FIELD_NUMBER: _ClassVar[int]
    usage: float
    def __init__(self, usage: _Optional[float] = ...) -> None: ...

class memoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class memoryReply(_message.Message):
    __slots__ = ("usage", "total", "used")
    USAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    USED_FIELD_NUMBER: _ClassVar[int]
    usage: int
    total: int
    used: int
    def __init__(self, usage: _Optional[int] = ..., total: _Optional[int] = ..., used: _Optional[int] = ...) -> None: ...

class sysInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class cpuInfo(_message.Message):
    __slots__ = ("cpu_name", "cpu_core", "cpu_thread", "cpu_freq")
    CPU_NAME_FIELD_NUMBER: _ClassVar[int]
    CPU_CORE_FIELD_NUMBER: _ClassVar[int]
    CPU_THREAD_FIELD_NUMBER: _ClassVar[int]
    CPU_FREQ_FIELD_NUMBER: _ClassVar[int]
    cpu_name: str
    cpu_core: int
    cpu_thread: int
    cpu_freq: float
    def __init__(self, cpu_name: _Optional[str] = ..., cpu_core: _Optional[int] = ..., cpu_thread: _Optional[int] = ..., cpu_freq: _Optional[float] = ...) -> None: ...

class memoryInfo(_message.Message):
    __slots__ = ("memory_total",)
    MEMORY_TOTAL_FIELD_NUMBER: _ClassVar[int]
    memory_total: float
    def __init__(self, memory_total: _Optional[float] = ...) -> None: ...

class sysInfoReply(_message.Message):
    __slots__ = ("cpu_info", "memory_info")
    class diskInfo(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    CPU_INFO_FIELD_NUMBER: _ClassVar[int]
    MEMORY_INFO_FIELD_NUMBER: _ClassVar[int]
    cpu_info: cpuInfo
    memory_info: memoryInfo
    def __init__(self, cpu_info: _Optional[_Union[cpuInfo, _Mapping]] = ..., memory_info: _Optional[_Union[memoryInfo, _Mapping]] = ...) -> None: ...
