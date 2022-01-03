import pickle
import sys

from abc import ABC, abstractmethod
from enum import Enum, auto

import numpy as np


class Topic(Enum):
    UNDEFINED = auto()
    IMU = auto()
    ATTITUDE = auto()


# https://docs.python-guide.org/scenarios/serialization/


class DeserializeError(ValueError):
    """Raised if a message could not be parsed."""

    pass


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
        try:
            data = cls._deserialize(bytes_[1:])
        except Exception as e:
            raise DeserializeError() from e
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


class NumpyMessage(Message):

    array_dtype = np.float32

    def __init__(self, array: np.ndarray, topic: Topic = Topic.UNDEFINED):
        self.array = array
        self.topic = topic

        # array shape and dtype have to be known for deserialize
        # assert: array is flat and dtype is self.array_dtype
        if array.shape != (len(array),):
            raise ValueError("array must be flat.")
        if array.dtype != self.array_dtype:
            raise ValueError(f"array must be of type {self.array_dtype}.")

    def _serialize(self):
        return self.array.tobytes()

    @classmethod
    def _deserialize(cls, bytes_: bytes):
        return np.frombuffer(bytes_, dtype=cls.array_dtype)

    @property
    def content(self):
        return self.array


class TimeOrientPosMessage(NumpyMessage):
    def __init__(self, array: np.ndarray, topic: Topic = Topic.UNDEFINED):
        assert len(array) == 8
        super().__init__(array, topic)

    @property
    def timestamp(self):
        return self.array[0]

    @property
    def orientation(self):
        return self.array[1:5]

    @property
    def position(self):
        return self.array[5:8]
