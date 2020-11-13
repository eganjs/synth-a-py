from typing import Any

import toml

from .base import File


class TomlFile(File):
    def __init__(self, name: str, obj: Any):
        super().__init__(name)
        self.obj = obj

    def synth_content(self) -> str:
        return toml.dumps(self.obj)
