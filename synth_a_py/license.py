from textwrap import dedent
from typing import Type

from .base import File

__all__ = ["License"]


class _MITLicense(File):
    def __init__(self, copyright_period: str, copyright_holders: str) -> None:
        super().__init__("LICENSE")
        self.copyright_period = copyright_period
        self.copyright_holders = copyright_holders

    def synth_content(self) -> str:
        return dedent(
            f"""\
            Copyright © {self.copyright_period} {self.copyright_holders}

            Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

            The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

            THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
            """  # noqa: E501
        )


class __License:
    @property
    def MIT(self) -> Type[_MITLicense]:
        return _MITLicense


License = __License()
