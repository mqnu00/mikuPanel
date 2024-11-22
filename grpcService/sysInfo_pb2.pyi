from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CpuRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CpuReply(_message.Message):
    __slots__ = ("usage",)
    USAGE_FIELD_NUMBER: _ClassVar[int]
    usage: float
    def __init__(self, usage: _Optional[float] = ...) -> None: ...

class MemoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MemoryReply(_message.Message):
    __slots__ = ("usage", "total", "used")
    USAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    USED_FIELD_NUMBER: _ClassVar[int]
    usage: int
    total: int
    used: int
    def __init__(self, usage: _Optional[int] = ..., total: _Optional[int] = ..., used: _Optional[int] = ...) -> None: ...

class SysInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CpuInfo(_message.Message):
    __slots__ = ("cpuName", "cpuCore", "cpuThread", "cpuFreq")
    CPUNAME_FIELD_NUMBER: _ClassVar[int]
    CPUCORE_FIELD_NUMBER: _ClassVar[int]
    CPUTHREAD_FIELD_NUMBER: _ClassVar[int]
    CPUFREQ_FIELD_NUMBER: _ClassVar[int]
    cpuName: str
    cpuCore: int
    cpuThread: int
    cpuFreq: float
    def __init__(self, cpuName: _Optional[str] = ..., cpuCore: _Optional[int] = ..., cpuThread: _Optional[int] = ..., cpuFreq: _Optional[float] = ...) -> None: ...

class MemoryInfo(_message.Message):
    __slots__ = ("memoryTotal",)
    MEMORYTOTAL_FIELD_NUMBER: _ClassVar[int]
    memoryTotal: float
    def __init__(self, memoryTotal: _Optional[float] = ...) -> None: ...

class SysInfoReply(_message.Message):
    __slots__ = ("cpuInfo", "memoryInfo")
    class diskInfo(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    CPUINFO_FIELD_NUMBER: _ClassVar[int]
    MEMORYINFO_FIELD_NUMBER: _ClassVar[int]
    cpuInfo: CpuInfo
    memoryInfo: MemoryInfo
    def __init__(self, cpuInfo: _Optional[_Union[CpuInfo, _Mapping]] = ..., memoryInfo: _Optional[_Union[MemoryInfo, _Mapping]] = ...) -> None: ...
