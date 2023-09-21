from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ["seq_no", "ts", "name", "data"]
    SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    TS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    seq_no: int
    ts: float
    name: str
    data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, seq_no: _Optional[int] = ..., ts: _Optional[float] = ..., name: _Optional[str] = ..., data: _Optional[_Iterable[int]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
