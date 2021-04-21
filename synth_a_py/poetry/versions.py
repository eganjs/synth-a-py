from typing import Dict, List, Type, Union

from typing_extensions import TypedDict

__all__ = [
    "ManagableDependencyDict",
    "DependencyDict",
    "ManagableVersion",
    "Managed",
    "Version",
    "VersionSpec",
]


class VersionSpecBase(TypedDict):
    version: str


class VersionSpec(VersionSpecBase, total=False):
    extras: List[str]


Version = Union[
    str,
    VersionSpec,
]


DependencyDict = Dict[
    str,
    Version,
]


class Managed:
    def __init__(self) -> None:
        raise Exception("Do not instanitate")


class ManagableVersionSpecBase(TypedDict):
    version: Union[str, Type[Managed]]


class ManagableVersionSpec(ManagableVersionSpecBase, total=False):
    extras: List[str]


ManagableVersion = Union[
    str,
    ManagableVersionSpec,
    Type[Managed],
]


ManagableDependencyDict = Dict[
    str,
    ManagableVersion,
]
