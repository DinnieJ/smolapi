from typing import Self
from smolapi.routing import Router, Route
from abc import ABCMeta

class Provider(metaclass=ABCMeta):
    def __new__(cls: type[Self]) -> Self:
        return object.__new__(cls)