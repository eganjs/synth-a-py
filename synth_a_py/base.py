from abc import abstractmethod
from contextvars import ContextVar, Token
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Callable, Dict, Iterator, Optional, Tuple, Type, Union

from returns.functions import compose

__all__ = [
    "File",
    "Project",
    "Dir",
]


PathResolver = Callable[[Path], Path]


class _FileContainerMixin:
    def __init__(self) -> None:
        self.__store: Dict[str, Union[File, Dir]] = dict()

    def add(self, item: Union["File", "Dir"]) -> None:
        assert item.name not in self.__store
        self.__store[item.name] = item

    def walk(self) -> Iterator[Tuple[PathResolver, "File"]]:
        item: Union[File, Dir]
        for item in self.__store.values():

            def path_resolver(path: Path) -> Path:
                return path / item.name

            if isinstance(item, File):
                yield path_resolver, item
            else:
                for subpath_resolver, subitem in item.walk():
                    yield compose(path_resolver, subpath_resolver), subitem


if TYPE_CHECKING:
    _ContextToken = Token[Optional[_FileContainerMixin]]
else:
    _ContextToken = Token

__context: ContextVar[Optional[_FileContainerMixin]] = ContextVar(
    "__context", default=None
)


def _context_get() -> _FileContainerMixin:
    project = __context.get()
    assert project is not None
    return project


def _context_set_root(value: _FileContainerMixin) -> _ContextToken:
    project = __context.get()
    assert project is None
    return __context.set(value)


def _context_set(value: _FileContainerMixin) -> _ContextToken:
    project = __context.get()
    assert project is not None
    return __context.set(value)


def _context_reset(token: _ContextToken) -> None:
    project = __context.get()
    assert project is not None
    __context.reset(token)


class File:
    def __init__(self, name: str):
        self.name = name
        _context_get().add(self)

    @abstractmethod
    def synth_content(self) -> str:
        ...


class _ContextMixin(_FileContainerMixin):
    def __init__(self) -> None:
        super().__init__()
        self.__context_token: Optional[_ContextToken] = None

    def __enter__(self) -> None:
        assert self.__context_token is None
        if isinstance(self, Project):
            self.__context_token = _context_set_root(self)
        else:
            self.__context_token = _context_set(self)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        assert self.__context_token is not None
        _context_reset(self.__context_token)
        self.__context_token = None


class Project(_ContextMixin):
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


class Dir(_ContextMixin):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        _context_get().add(self)
