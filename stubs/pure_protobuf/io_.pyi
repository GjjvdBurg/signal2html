import abc

from abc import ABC
from abc import abstractmethod
from io import BytesIO

from typing import Any
from typing import BinaryIO
from typing import Union

IO = Union[BinaryIO, BytesIO]

class Dumps(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def dump(self, value: Any, io: IO) -> Any: ...
    def dumps(self, value: Any) -> bytes: ...

class Loads(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def load(self, io: IO) -> Any: ...
    def loads(self, bytes_: bytes) -> Any: ...
