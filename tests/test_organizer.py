from file_organizer.config import DEFAULT_CATEGORIES, get_category_for_extension
from file_organizer.organizer import FileOrganizer


def test_get_category_for_extension():
    assert get_category_for_extension(".jpg", DEFAULT_CATEGORIES) == "Images"
    assert get_category_for_extension(".JPG", DEFAULT_CATEGORIES) == "Images"
    assert get_category_for_extension(".txt", DEFAULT_CATEGORIES) == "Documents"
    assert get_category_for_extension(".unknown", DEFAULT_CATEGORIES) == "Other"


def test_dry_run(tmp_path):
    (tmp_path / "test1.txt").write_text("hello")
    (tmp_path / "test2.jpg").write_text("image")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=True)
    summary = organizer.run()

    assert summary.moved == 2
    assert summary.errors == 0
    assert (tmp_path / "test1.txt").exists()
    assert (tmp_path / "test2.jpg").exists()
    assert not (tmp_path / "Documents").exists()
    assert not (tmp_path / "Images").exists()


def test_actual_run(tmp_path):
    (tmp_path / "test1.txt").write_text("hello")
    (tmp_path / "test2.jpg").write_text("image")
    (tmp_path / "unknown.xyz").write_text("unknown")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    summary = organizer.run()

    assert summary.moved == 3
    assert summary.errors == 0
    assert not (tmp_path / "test1.txt").exists()
    assert (tmp_path / "Documents" / "test1.txt").exists()
    assert (tmp_path / "Images" / "test2.jpg").exists()
    assert (tmp_path / "Other" / "unknown.xyz").exists()


def test_filename_collision(tmp_path):
    (tmp_path / "test.txt").write_text("content 1")

    docs_dir = tmp_path / "Documents"
    docs_dir.mkdir()
    (docs_dir / "test.txt").write_text("content 2")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    summary = organizer.run()

    assert summary.moved == 1
    assert summary.errors == 0
    assert summary.collisions_handled == 1
    assert (docs_dir / "test.txt").exists()
    assert (docs_dir / "test (1).txt").exists()
    assert (docs_dir / "test.txt").read_text() == "content 2"
    assert (docs_dir / "test (1).txt").read_text() == "content 1"


def test_duplicate_file_skipping(tmp_path):
    (tmp_path / "file1.txt").write_text("identical content")
    (tmp_path / "file2.txt").write_text("identical content")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    summary = organizer.run()

    assert summary.moved == 1
    assert summary.errors == 0
    assert summary.duplicates_skipped == 1

    docs_dir = tmp_path / "Documents"
    assert len(list(docs_dir.iterdir())) == 1
    left_behind = [f for f in tmp_path.iterdir() if f.is_file()]
    assert len(left_behind) == 1


def test_recursive(tmp_path):
    sub = tmp_path / "subfolder"
    sub.mkdir()
    (sub / "test.txt").write_text("hello")

    organizer_non_rec = FileOrganizer(
        target_dir=tmp_path, dry_run=False, recursive=False
    )
    summary_non_rec = organizer_non_rec.run()
    assert summary_non_rec.moved == 0

    organizer_rec = FileOrganizer(target_dir=tmp_path, dry_run=False, recursive=True)
    summary_rec = organizer_rec.run()
    assert summary_rec.moved == 1

    assert (tmp_path / "Documents" / "test.txt").exists()
    assert not (sub / "test.txt").exists()


def test_hidden_file_skipping(tmp_path):
    (tmp_path / ".hidden.txt").write_text("hidden")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    summary = organizer.run()

    assert summary.moved == 0
    assert summary.errors == 0
    assert (tmp_path / ".hidden.txt").exists()


def test_symlink_skipping(tmp_path):
    import os

    real_file = tmp_path / "real.txt"
    real_file.write_text("real content")
    symlink_file = tmp_path / "link.txt"
    os.symlink(real_file, symlink_file)

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    summary = organizer.run()

    assert summary.moved == 1
    assert summary.errors == 0
    assert not real_file.exists()
    assert symlink_file.is_symlink()


def test_invalid_target_dir(tmp_path):
    not_exist = tmp_path / "does_not_exist"
    organizer = FileOrganizer(target_dir=not_exist)
    summary = organizer.run()
    assert summary.moved == 0
    assert summary.errors == 1

    is_file = tmp_path / "file.txt"
    is_file.write_text("not a dir")
    organizer2 = FileOrganizer(target_dir=is_file)
    summary2 = organizer2.run()
    assert summary2.moved == 0
    assert summary2.errors == 1


def test_custom_config(tmp_path):
    (tmp_path / "code.py").write_text("print('hello')")
    (tmp_path / "data.csv").write_text("1,2,3")

    custom_categories = {
        "PythonFiles": [".py"],
        "DataFiles": [".csv"],
    }

    organizer = FileOrganizer(
        target_dir=tmp_path, categories=custom_categories, dry_run=False
    )
    summary = organizer.run()

    assert summary.moved == 2
    assert summary.errors == 0
    assert (tmp_path / "PythonFiles" / "code.py").exists()
    assert (tmp_path / "DataFiles" / "data.csv").exists()
