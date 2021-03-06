from abc import abstractmethod
from contextvars import ContextVar, Token
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Callable, Dict, Iterator, Optional, Tuple, Type, Union

from returns.functions import compose

from .utils import init_mix_ins

__all__ = [
    "File",
    "Project",
    "Dir",
]


PathResolver = Callable[[Path], Path]


class _FileContainerMixIn:
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

    def subpaths(self) -> Iterator[str]:
        return (str(path_resolver(Path("."))) for path_resolver, _ in self.walk())


if TYPE_CHECKING:
    _ContextToken = Token[Optional[_FileContainerMixIn]]
else:
    _ContextToken = Token

__context: ContextVar[Optional[_FileContainerMixIn]] = ContextVar(
    "__context", default=None
)


def _context_get() -> _FileContainerMixIn:
    project = __context.get()
    assert project is not None
    return project


def _context_set_root(value: _FileContainerMixIn) -> _ContextToken:
    project = __context.get()
    assert project is None
    return __context.set(value)


def _context_set(value: _FileContainerMixIn) -> _ContextToken:
    project = __context.get()
    assert project is not None
    return __context.set(value)


def _context_reset(token: _ContextToken) -> None:
    project = __context.get()
    assert project is not None
    __context.reset(token)


class _ChildMixIn:
    def __init__(self) -> None:
        self.parent = _context_get()
        assert isinstance(self, File) or isinstance(self, Dir)
        self.parent.add(self)


class File(_ChildMixIn):
    def __init__(self, name: str) -> None:
        self.name = name
        init_mix_ins(self, File)

    @abstractmethod
    def synth_content(self) -> str:
        ...


class _ContextMixIn(_FileContainerMixIn):
    def __init__(self) -> None:
        self.__context_token: Optional[_ContextToken] = None
        init_mix_ins(self, _ContextMixIn)

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


class Project(_ContextMixIn):
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


class Dir(_ContextMixIn, _ChildMixIn):
    def __init__(self, name: str) -> None:
        self.name = name
        init_mix_ins(self, Dir)
