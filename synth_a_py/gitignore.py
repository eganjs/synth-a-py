from pathlib import Path
from typing import List, Optional

from .base import File
from .utils import ensure_nl

__all__ = ["GitIgnore"]


class GitIgnore(File):
    def __init__(
        self,
        ignore: Optional[List[str]] = None,
        allow: Optional[List[str]] = None,
    ):
        super().__init__(".gitignore")
        self.ignore = ignore or []
        self.allow = allow or []

    def synth_content(self) -> str:
        return ensure_nl(
            "\n".join(
                [
                    *self.ignore,
                    *(
                        f"!{'/'.join(Path(path).parts)}"
                        for path in self.parent.subpaths()
                    ),
                    *(f"!{path}" for path in self.allow),
                ]
            )
        )
