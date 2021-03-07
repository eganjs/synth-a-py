__all__ = [
    "ensure_nl",
]

from inspect import Parameter, Signature

from typing_extensions import Final


def ensure_nl(s: str) -> str:
    return s.rstrip() + "\n"


no_param_init: Final[Signature] = Signature(
    (Parameter("self", Parameter.POSITIONAL_OR_KEYWORD),),
    return_annotation=None,
)
