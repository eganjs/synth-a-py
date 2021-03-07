from typing import Any, Dict

from mypyc.build import mypycify  # type: ignore


def build(setup_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    setup_kwargs.update({
        "ext_modules": mypycify(["synth_a_py"], opt_level="3")
    })
    return setup_kwargs


if __name__ == "__main__":
    print(build({}))
