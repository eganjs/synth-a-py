from configparser import ConfigParser
from io import StringIO
from typing import Any

from synth_a_py.base import File
from synth_a_py.utils import ensure_nl

__all__ = ["IniFile"]


class IniFile(File):
    def __init__(self, name: str, obj: Any):
        super().__init__(name)
        self.obj = obj

    def synth_content(self) -> str:
        config = ConfigParser()
        config.read_dict(self.obj)
        with StringIO() as buf:
            config.write(buf)
            return ensure_nl(buf.getvalue())
