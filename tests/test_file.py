from pathlib import Path
from textwrap import dedent

from synth_a_py import EmptyFile, Project, SimpleFile


def test_empty_file(tmp_path: Path) -> None:
    spec = Project()
    with spec:
        EmptyFile("empty-file")

    spec.synth(tmp_path)

    file_path = tmp_path / "empty-file"
    assert file_path.stat().st_mode & 0o777 == 0o444
    assert file_path.read_text() == ""


def test_simple_file_from_string(tmp_path: Path) -> None:
    spec = Project()
    with spec:
        SimpleFile("file", "test content\n")

    spec.synth(tmp_path)

    file_path = tmp_path / "file"
    assert file_path.stat().st_mode & 0o777 == 0o444
    assert file_path.read_text() == "test content\n"


def test_simple_file_from_string_with_no_new_line(tmp_path: Path) -> None:
    spec = Project()
    with spec:
        SimpleFile("file", "test content")

    spec.synth(tmp_path)

    file_path = tmp_path / "file"
    assert file_path.stat().st_mode & 0o777 == 0o444
    assert file_path.read_text() == "test content\n"


def test_simple_file_from_list(tmp_path: Path) -> None:
    spec = Project()
    with spec:
        SimpleFile(
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

    file_path = tmp_path / "file"
    assert file_path.stat().st_mode & 0o777 == 0o444
    assert file_path.read_text() == dedent(
        """\
        Lorem ipsum dolor sit amet
        consectetur adipiscing elit
        Cras eros purus
        aliquet ac magna ut
        fermentum cursus turpis
        """
    )
