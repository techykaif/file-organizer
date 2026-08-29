import os

from file_organizer.organizer import FileOrganizer


def test_unicode_and_special_filename_is_preserved(tmp_path):
    source = tmp_path / "résumé 2026 (final).txt"
    source.write_text("hello", encoding="utf-8")
    summary = FileOrganizer(target_dir=tmp_path).run()
    destination = tmp_path / "Documents" / source.name
    assert summary.moved == 1
    assert destination.read_text(encoding="utf-8") == "hello"


def test_collision_chain_preserves_every_file(tmp_path):
    docs = tmp_path / "Documents"
    docs.mkdir()
    (docs / "report.txt").write_text("existing")
    (docs / "report (1).txt").write_text("existing-1")
    (tmp_path / "report.txt").write_text("source")
    summary = FileOrganizer(target_dir=tmp_path).run()
    assert summary.moved == 1
    assert summary.collisions_handled == 1
    assert (docs / "report.txt").read_text() == "existing"
    assert (docs / "report (1).txt").read_text() == "existing-1"
    assert (docs / "report (2).txt").read_text() == "source"


def test_dry_run_does_not_mutate_existing_files(tmp_path):
    source = tmp_path / "report.txt"
    source.write_text("original")
    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    summary = FileOrganizer(target_dir=tmp_path, dry_run=True).run()
    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert summary.moved == 1
    assert before == after
    assert source.exists()
    assert not (tmp_path / "Documents").exists()


def test_symlink_to_file_is_never_moved(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("content")
    link = tmp_path / "alias.txt"
    os.symlink(source, link)
    summary = FileOrganizer(target_dir=tmp_path).run()
    assert summary.moved == 1
    assert not source.exists()
    assert link.is_symlink()


def test_recursive_unicode_nested_file_is_moved(tmp_path):
    nested = tmp_path / "nested folder" / "日本語"
    nested.mkdir(parents=True)
    source = nested / "café notes.txt"
    source.write_text("notes", encoding="utf-8")
    summary = FileOrganizer(target_dir=tmp_path, recursive=True).run()
    destination = tmp_path / "Documents" / source.name
    assert summary.moved == 1
    assert destination.read_text(encoding="utf-8") == "notes"
    assert not source.exists()
