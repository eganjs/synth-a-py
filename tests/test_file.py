from pathlib import Path
from textwrap import dedent

from synth_a_py import EmptyFile, SimpleFile


def test_empty_file(tmp_path: Path) -> None:
    spec = EmptyFile("empty-file")
    spec.synth(tmp_path)
    assert (tmp_path / "empty-file").read_text() == ""


def test_simple_file_from_string(tmp_path: Path) -> None:
    spec = SimpleFile("file", "test content\n")
    spec.synth(tmp_path)
    assert (tmp_path / "file").read_text() == "test content\n"


def test_simple_file_from_string_with_no_new_line(tmp_path: Path) -> None:
    spec = SimpleFile("file", "test content")
    spec.synth(tmp_path)
    assert (tmp_path / "file").read_text() == "test content\n"


def test_simple_file_from_list(tmp_path: Path) -> None:
    spec = SimpleFile(
        "file",
        (
            "Lorem ipsum dolor sit amet",
            "consectetur adipiscing elit",
            "Cras eros purus",
            "aliquet ac magna ut",
            "fermentum cursus turpis",
        ),
    )
    spec.synth(tmp_path)
    assert (tmp_path / "file").read_text() == dedent(
        """\
        Lorem ipsum dolor sit amet
        consectetur adipiscing elit
        Cras eros purus
        aliquet ac magna ut
        fermentum cursus turpis
        """
    )
