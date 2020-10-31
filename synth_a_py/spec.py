from abc import ABC, abstractmethod
from pathlib import Path


class Spec(ABC):
    @abstractmethod
    def synth(self, path: Path) -> None:
        ...
