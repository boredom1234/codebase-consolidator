import unittest
import tempfile
import shutil
import os
from pathlib import Path
from codebase_consolidator import CodebaseConsolidator

class TestCodebaseConsolidator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.root_path = Path(self.test_dir)

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_gitignore_parsing(self):
        """Test that .gitignore patterns are correctly loaded"""
        gitignore_path = self.root_path / ".gitignore"
        with open(gitignore_path, "w") as f:
            f.write("*.log\n")
            f.write("temp/\n")
            f.write("# This is a comment\n")

        consolidator = CodebaseConsolidator(str(self.root_path))

        # Check standard ignores are present
        self.assertTrue(".git/*" in consolidator.ignored_patterns)

        # Check custom ignores are present
        self.assertTrue("*.log" in consolidator.ignored_patterns)
        self.assertTrue("temp/" in consolidator.ignored_patterns)

    def test_file_collection_ignores(self):
        """Test that files are collected and ignored correctly"""
        # Create some files
        (self.root_path / "main.py").touch()
        (self.root_path / "ignored.log").touch()

        temp_dir = self.root_path / "temp"
        temp_dir.mkdir()
        (temp_dir / "temp_file.txt").touch()

        # Create gitignore
        with open(self.root_path / ".gitignore", "w") as f:
            f.write("*.log\n")
            f.write("temp/\n")

        consolidator = CodebaseConsolidator(str(self.root_path))
        files = consolidator._collect_files()

        # main.py should be found
        self.assertTrue(any(f.name == "main.py" for f in files))

        # ignored.log should NOT be found
        self.assertFalse(any(f.name == "ignored.log" for f in files))

        # temp_file.txt should NOT be found
        self.assertFalse(any(f.name == "temp_file.txt" for f in files))

    def test_bucketing_logic(self):
        """Test that files are distributed into buckets correctly"""
        # Create 10 dummy files of equal size (approx)
        for i in range(10):
            p = self.root_path / f"file_{i}.txt"
            with open(p, "w") as f:
                f.write("x" * 100) # 100 bytes

        # Target 2 output files
        consolidator = CodebaseConsolidator(str(self.root_path), target_files=2)
        files = consolidator._collect_files()
        self.assertEqual(len(files), 10)

        buckets = consolidator._distribute_files(files)

        # Should have at most 2 buckets
        self.assertLessEqual(len(buckets), 2)

        # Total files in buckets should be 10
        total_files = sum(len(b) for b in buckets)
        self.assertEqual(total_files, 10)

    def test_bucketing_more_targets_than_files(self):
        """Test bucketing when target files > source files"""
        # Create 3 files
        for i in range(3):
            (self.root_path / f"file_{i}.txt").touch()

        # Target 10 files
        consolidator = CodebaseConsolidator(str(self.root_path), target_files=10)
        files = consolidator._collect_files()
        buckets = consolidator._distribute_files(files)

        # Should have 3 buckets (one per file)
        self.assertEqual(len(buckets), 3)

if __name__ == "__main__":
    unittest.main()
