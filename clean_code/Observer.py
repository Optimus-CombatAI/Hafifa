from __future__ import annotations
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self) -> None:
        """React to a change in the subject."""


class Subject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update()

    def add_observer(self, observer: Observer) -> None:
        self._observers.append(observer)
        observer.update()

    def remove_observer(self, observer: Observer) -> None:
        self._observers.remove(observer)
