from abc import ABC, abstractmethod

from driftwatch.core import Snapshot

class BaseSource(ABC):
    @abstractmethod
    def collect(self) -> Snapshot:
        ...