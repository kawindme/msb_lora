import pickle
import sys

from abc import ABC, abstractmethod
from enum import Enum, auto

try:
    import numpy as np
except ImportError:
    pass


class Topic(Enum):
    UNDEFINED = auto()
    IMU = auto()


# https://docs.python-guide.org/scenarios/serialization/


class Message(ABC):

    topic = Topic.UNDEFINED

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def content(self):
        pass

    @abstractmethod
    def _serialize(self):
        pass

    @classmethod
    @abstractmethod
    def _deserialize(cls, bytes_: bytes):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self.content}, {str(self.topic)})"

    def __str__(self):
        return f"{self.topic}: {self.content}"

    def serialize(self):
        return bytes([self.topic.value]) + self._serialize()

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        topic = Topic(bytes_[0])
        data = cls._deserialize(bytes_[1:])
        return cls(data, topic)


class TextMessage(Message):
    def __init__(self, text: str, topic: Topic = Topic.UNDEFINED):
        self.text = text
        self.topic = topic

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.content}", {str(self.topic)})'

    def _serialize(self):
        return self.text.encode("utf-8")

    @classmethod
    def _deserialize(cls, bytes_: bytes):
        return bytes_.decode("utf-8")

    @property
    def content(self):
        return self.text


class PickleMessage(Message):
    def __init__(self, data, topic: Topic = Topic.UNDEFINED):
        self.data = data
        self.topic = topic

    def _serialize(self):
        return pickle.dumps(self.data)

    @classmethod
    def _deserialize(cls, bytes_: bytes):
        return pickle.loads(bytes_)

    @property
    def content(self):
        return self.data


if "numpy" in sys.modules:

    class NumpyMessage(Message):
        def __init__(self, array: np.ndarray, topic: Topic = Topic.UNDEFINED):
            self.array = array
            self.topic = topic

        def _serialize(self):
            return self.array.tobytes()

        @classmethod
        def _deserialize(cls, bytes_: bytes):
            return np.frombuffer(bytes_)  # TODO: numpy dtype necessary for deserialize

        @property
        def content(self):
            return self.array

else:

    class NumpyMessage:
        def __init__(self):
            raise RuntimeError("Missing dependency numpy.")
