import pytest, logging

from celestialvault.instances.inst_file import FileTree
from celestialvault.tools.FileOperations import get_dir_hash


def test_print_tree():
    # Test with a valid directory
    exclude_dirs = [
        ".git",
        ".pytest_cache",
        ".vscode",
        "__pycache__",
        "logs",
        "fallback",
        "old_logs",
    ]
    exclude_exts = [".txt", ".prof", ".json", ".ipynb"]
    print()

    file_tree = FileTree.build_from_path(
        r".", exclude_dirs=exclude_dirs, exclude_exts=exclude_exts, max_depth=99
    )
    file_tree.print_tree()

    assert file_tree.root.hash == get_dir_hash(
        r".", exclude_dirs=exclude_dirs, exclude_exts=exclude_exts
    )
    print("\nPass hash test.")


def test_print_tree_align_suffixes_in_same_dir(tmp_path, capsys):
    (tmp_path / "a").mkdir()
    (tmp_path / "very_long_directory_name").mkdir()
    (tmp_path / "mid.txt").write_text("mid")
    (tmp_path / "skip.json").write_text("{}")

    file_tree = FileTree.build_from_path(tmp_path)
    file_tree.print_tree(exclude_exts=[".json"], max_depth=99)

    output_lines = [
        line for line in capsys.readouterr().out.splitlines()
        if line.startswith("    ")
    ]

    tab_indexes = {line.index("\t(") for line in output_lines}

    assert len(output_lines) == 4
    assert len(tab_indexes) == 1
