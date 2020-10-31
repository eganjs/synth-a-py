from abc import abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Union

from .spec import Spec


class File(Spec):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def _synth_content(self) -> str:
        ...

    def synth(self, path: Optional[Path] = None) -> None:
        if path is None:
            path = Path.cwd()

        path.mkdir(parents=True, exist_ok=True)

        (path / self.name).write_text(self._synth_content())


class EmptyFile(File):
    def _synth_content(self) -> str:
        return ""


class SimpleFile(File):
    def __init__(self, name: str, content: Union[str, Tuple[str, ...]]):
        super().__init__(name)
        self.content = content

    def __ensure_new_line(self, s: str) -> str:
        return s if s.endswith("\n") else s + "\n"

    def _synth_content(self) -> str:
        if isinstance(self.content, str):
            return self.__ensure_new_line(self.content)
        elif isinstance(self.content, tuple):
            return "".join(map(self.__ensure_new_line, self.content))

        raise TypeError(f"Unexpected type: {type(self.content)}")
