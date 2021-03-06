__all__ = [
    "ensure_nl",
    "init_mix_ins",
]

from inspect import Parameter, Signature, signature
from typing import Any

from typing_extensions import Final


def ensure_nl(s: str) -> str:
    return s.rstrip() + "\n"


no_param_init: Final[Signature] = Signature(
    (Parameter("self", Parameter.POSITIONAL_OR_KEYWORD),),
    return_annotation=None,
)


def init_mix_ins(self: Any, t: type) -> None:
    bases = t.__bases__
    for base in bases:
        init = getattr(base, "__init__")
        if signature(init) == no_param_init:
            init(self)
