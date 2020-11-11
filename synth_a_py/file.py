from typing import Tuple, Union

from .base import File

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

    def __ensure_new_line(self, s: str) -> str:
        return s if s.endswith("\n") else s + "\n"

    def synth_content(self) -> str:
        if isinstance(self.content, str):
            return self.__ensure_new_line(self.content)
        elif isinstance(self.content, tuple):
            return "".join(map(self.__ensure_new_line, self.content))

        raise TypeError(f"Unexpected type: {type(self.content)}")
