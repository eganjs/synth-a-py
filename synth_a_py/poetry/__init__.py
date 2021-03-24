from typing import Any, Dict, List, Optional, cast

from synth_a_py.base import Dir
from synth_a_py.poetry.versions import (
    DependencyDict,
    ManagableDependencyDict,
    ManagableVersion,
    Managed,
    Version,
    VersionSpec,
)
from synth_a_py.toml import TomlFile

__all__ = [
    "PoetryModule",
]


def resolve_dependencies(
    managable_dependencies: ManagableDependencyDict,
    dependency_management: DependencyDict,
) -> DependencyDict:
    if not dependency_management:
        return cast(DependencyDict, managable_dependencies)

    def get_managed_version(dep: str) -> Version:
        try:
            return dependency_management[dep]
        except Exception as e:
            raise Exception(f"Dependency {dep} missing from dependency_management", e)

    def resolve_dependency(dep: str, version: ManagableVersion) -> Version:
        if isinstance(version, str):
            return version
        elif version == Managed:
            return get_managed_version(dep)
        elif isinstance(version, dict) and version["version"] == Managed:
            managed_version = get_managed_version(dep)
            resolved_version: VersionSpec = {
                "version": managed_version
                if isinstance(managed_version, str)
                else managed_version["version"]
            }

            if "extras" in version:
                resolved_version["extras"] = version["extras"]

            return resolved_version
        else:
            return cast(VersionSpec, version)

    return {
        dep: resolve_dependency(dep, version)
        for dep, version in managable_dependencies.items()
    }


class PoetryModule:
    def __init__(
        self,
        *,
        name: str,
        description: str,
        version: str,
        authors: Optional[List[str]] = None,
        license: Optional[str] = None,
        dependencies: Optional[ManagableDependencyDict] = None,
        dev_dependencies: Optional[ManagableDependencyDict] = None,
        dependency_management: Optional[DependencyDict] = None,
    ):
        self.dir = Dir(name)
        with self.dir:
            pyproject_tool_poetry: Dict[str, Any] = {
                "name": name,
                "description": description,
                "version": version,
                "authors": authors or [],
            }

            if license:
                pyproject_tool_poetry["license"] = license

            dependency_management = dependency_management or {}

            if dependencies:
                pyproject_tool_poetry["dependencies"] = resolve_dependencies(
                    dependencies,
                    dependency_management,
                )

            if dev_dependencies:
                pyproject_tool_poetry["dev-dependencies"] = resolve_dependencies(
                    dev_dependencies,
                    dependency_management,
                )

            self.pyproject = TomlFile(
                "pyproject.toml",
                {
                    "build-system": {
                        "requires": ["poetry-core>=1.0.0"],
                        "build-backend": "poetry.core.masonry.api",
                    },
                    "tool": {
                        "poetry": pyproject_tool_poetry,
                    },
                },
            )
