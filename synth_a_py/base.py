from abc import ABC, abstractmethod
from contextvars import ContextVar, Token
from pathlib import Path
from types import TracebackType
from typing import Callable, Dict, Iterator, Optional, Tuple, Type, Union

__all__ = [
    "File",
    "Project",
    "Dir",
]


__container_context: "ContextVar[Optional[Container]]" = ContextVar(
    "__container_context", default=None
)


def _context_get() -> "Container":
    container = __container_context.get()
    assert container is not None
    return container


def _context_set_root(
    value: "Container",
) -> "Token[Optional[Container]]":
    container = __container_context.get()
    assert container is None
    return __container_context.set(value)


def _context_set(value: "Container") -> "Token[Optional[Container]]":
    container = __container_context.get()
    assert container is not None
    return __container_context.set(value)


def _context_reset(token: "Token[Optional[Container]]") -> None:
    container = __container_context.get()
    assert container is not None
    __container_context.reset(token)


PathResolver = Callable[[Path], Path]


class Container(ABC):
    def __init__(self) -> None:
        self._store: "Dict[str, Union[File, Dir]]" = dict()
        self._context_token: "Optional[Token[Optional[Container]]]" = None

    def add(self, item: Union["File", "Dir"]) -> None:
        assert item.name not in self._store
        self._store[item.name] = item

    def walk(self) -> Iterator[Tuple[PathResolver, "File"]]:
        item: Union[File, Dir]
        for item in self._store.values():

            def path_resolver(path: Path) -> Path:
                return path / item.name

            if isinstance(item, Container):
                for subpath_resolver, subitem in item.walk():
                    yield lambda p: path_resolver(subpath_resolver(p)), subitem
            else:
                yield path_resolver, item

    def subpaths(self) -> Iterator[str]:
        return (str(path_resolver(Path("."))) for path_resolver, _ in self.walk())

    def __enter__(self) -> None:
        assert self._context_token is None
        self._context_token = _context_set(self)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        assert self._context_token is not None
        _context_reset(self._context_token)
        self._context_token = None


class Project(Container):
    def __enter__(self) -> None:
        assert self._context_token is None
        self._context_token = _context_set_root(self)

    def synth(self, root: Optional[Path] = None) -> None:
        if root is None:
            root = Path.cwd()

        root.mkdir(parents=True, exist_ok=True)

        for path_resolver, f in self.walk():
            path = path_resolver(root)

            path.parent.mkdir(parents=True, exist_ok=True)

            # ensure writable
            if path.is_file():
                path.chmod(0o644)

            # write and mark read only
            path.write_text(f.synth_content())
            path.chmod(0o444)


class Dir(Container):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        _context_get().add(self)


class File:
    def __init__(self, name: str) -> None:
        self.name = name
        self.parent = _context_get()
        self.parent.add(self)

    @abstractmethod
    def synth_content(self) -> str:
        ...
