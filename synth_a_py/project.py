from pathlib import Path
from typing import Optional

from .spec import Spec


class Project(Spec):
    def synth(self, path: Optional[Path] = None) -> None:
        if path is None:
            path = Path.cwd()

        path.mkdir(parents=True, exist_ok=True)
