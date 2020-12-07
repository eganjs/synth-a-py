from typing import Tuple, Union

from .base import File
from .utils import ensure_nl

__all__ = [
    "EmptyFile",
    "SimpleFile",
]


class EmptyFile(File):
    def synth_content(self) -> str:
        return ""


class SimpleFile(File):
    def __init__(self, name: str, content: Union[str, Tuple[str, ...]]):
        super().__init__(name)
        self.content = content

    def synth_content(self) -> str:
        if isinstance(self.content, str):
            return ensure_nl(self.content)
        elif isinstance(self.content, tuple):
            return "".join(map(ensure_nl, self.content))

        raise TypeError(f"Unexpected type: {type(self.content)}")
