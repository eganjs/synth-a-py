from copy import deepcopy
from typing import Any

from ruamel.yaml.compat import StringIO
from ruamel.yaml.main import YAML
from ruamel.yaml.scalarstring import walk_tree as insert_multiline_literals_inplace

from .base import File

__all__ = ["YamlFile"]


class _YAML(YAML):
    def dumps(self, data: Any) -> str:
        stream = StringIO()
        self.dump(data, stream)
        return stream.getvalue()


yaml = _YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


class YamlFile(File):
    def __init__(self, name: str, obj: Any):
        super().__init__(name)
        self.obj = obj

    def synth_content(self) -> str:
        obj = deepcopy(self.obj)
        insert_multiline_literals_inplace(obj)
        return yaml.dumps(obj)
