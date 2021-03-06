from typing import List, Optional

from .base import File

__all__ = ["GitIgnore"]

from .utils import ensure_nl


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
                        f"!{path}"
                        for allow_provider in [
                            self.parent.subpaths(),
                            self.allow,
                        ]
                        for path in allow_provider
                    ),
                ]
            )
        )
