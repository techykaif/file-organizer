from file_organizer.config import DEFAULT_CATEGORIES, get_category_for_extension
from file_organizer.organizer import FileOrganizer


def test_get_category_for_extension():
    assert get_category_for_extension(".jpg", DEFAULT_CATEGORIES) == "Images"
    assert get_category_for_extension(".JPG", DEFAULT_CATEGORIES) == "Images"
    assert get_category_for_extension(".txt", DEFAULT_CATEGORIES) == "Documents"
    assert get_category_for_extension(".unknown", DEFAULT_CATEGORIES) == "Other"

def test_dry_run(tmp_path):
    # Setup test directory
    (tmp_path / "test1.txt").write_text("hello")
    (tmp_path / "test2.jpg").write_text("image")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=True)
    moved, errors = organizer.run()

    assert moved == 2
    assert errors == 0

    # Assert nothing was actually moved
    assert (tmp_path / "test1.txt").exists()
    assert (tmp_path / "test2.jpg").exists()
    assert not (tmp_path / "Documents").exists()
    assert not (tmp_path / "Images").exists()

def test_actual_run(tmp_path):
    (tmp_path / "test1.txt").write_text("hello")
    (tmp_path / "test2.jpg").write_text("image")
    (tmp_path / "unknown.xyz").write_text("unknown")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    moved, errors = organizer.run()

    assert moved == 3
    assert errors == 0

    assert not (tmp_path / "test1.txt").exists()
    assert (tmp_path / "Documents" / "test1.txt").exists()
    assert (tmp_path / "Images" / "test2.jpg").exists()
    assert (tmp_path / "Other" / "unknown.xyz").exists()

def test_filename_collision(tmp_path):
    (tmp_path / "test.txt").write_text("content 1")

    docs_dir = tmp_path / "Documents"
    docs_dir.mkdir()
    (docs_dir / "test.txt").write_text("content 2") # Different content, same name

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    moved, errors = organizer.run()

    assert moved == 1
    assert errors == 0

    assert (docs_dir / "test.txt").exists()
    assert (docs_dir / "test (1).txt").exists()

    assert (docs_dir / "test.txt").read_text() == "content 2"
    assert (docs_dir / "test (1).txt").read_text() == "content 1"

def test_duplicate_file_skipping(tmp_path):
    (tmp_path / "file1.txt").write_text("identical content")
    (tmp_path / "file2.txt").write_text("identical content")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    moved, errors = organizer.run()

    # Should only move one, and skip the other
    assert moved == 1
    assert errors == 0

    docs_dir = tmp_path / "Documents"
    # One file is moved
    assert len(list(docs_dir.iterdir())) == 1
    # One is skipped and left behind
    left_behind = [f for f in tmp_path.iterdir() if f.is_file()]
    assert len(left_behind) == 1

def test_recursive(tmp_path):
    sub = tmp_path / "subfolder"
    sub.mkdir()
    (sub / "test.txt").write_text("hello")

    # Run without recursive
    organizer_non_rec = FileOrganizer(target_dir=tmp_path, dry_run=False, recursive=False)
    moved, _errors = organizer_non_rec.run()
    assert moved == 0

    # Run with recursive
    organizer_rec = FileOrganizer(target_dir=tmp_path, dry_run=False, recursive=True)
    moved, _errors = organizer_rec.run()
    assert moved == 1

    assert (tmp_path / "Documents" / "test.txt").exists()
    assert not (sub / "test.txt").exists()

def test_hidden_file_skipping(tmp_path):
    (tmp_path / ".hidden.txt").write_text("hidden")

    organizer = FileOrganizer(target_dir=tmp_path, dry_run=False)
    moved, errors = organizer.run()

    assert moved == 0
    assert errors == 0
    assert (tmp_path / ".hidden.txt").exists()
