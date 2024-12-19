
import unittest
import os
import tempfile
import hashlib
from md5sift import calculate_hash, load_file_names, walk_directory_and_log

class TestMd5sift(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        # Create a test file
        self.test_file_path = os.path.join(self.test_dir, 'test.txt')
        with open(self.test_file_path, 'w') as f:
            f.write('This is a test file.')
        # Create a test CSV file
        self.test_csv_path = os.path.join(self.test_dir, 'filelist.csv')
        with open(self.test_csv_path, 'w') as f:
            f.write('test.txt\n')

    def tearDown(self):
        # Remove the temporary directory after tests
        import shutil
        shutil.rmtree(self.test_dir)

    def test_calculate_hash_md5(self):
        # Test calculate_hash function with MD5 algorithm
        file_path, hash_value, modified_time = calculate_hash(self.test_file_path, 'md5')
        self.assertIsNotNone(hash_value)
        expected_hash = hashlib.md5('This is a test file.'.encode()).hexdigest()
        self.assertEqual(hash_value, expected_hash)

    def test_calculate_hash_sha1(self):
        # Test calculate_hash function with SHA1 algorithm
        file_path, hash_value, modified_time = calculate_hash(self.test_file_path, 'sha1')
        self.assertIsNotNone(hash_value)
        expected_hash = hashlib.sha1('This is a test file.'.encode()).hexdigest()
        self.assertEqual(hash_value, expected_hash)

    def test_load_file_names(self):
        # Test loading file names from a CSV file
        file_names = load_file_names(self.test_csv_path)
        self.assertIn('test.txt', file_names)

    def test_walk_directory_and_log(self):
        # Test walk_directory_and_log function
        output_csv = os.path.join(self.test_dir, 'output.csv')
        walk_directory_and_log(
            directory=self.test_dir,
            csv_file_path=output_csv,
            algorithm='md5',
            exclude_paths=set(),
            file_extension='.txt',
            file_names=None,
            verbose=False,
            limit=None
        )
        self.assertTrue(os.path.exists(output_csv))
        with open(output_csv, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)  # Header and one file entry

if __name__ == '__main__':
    unittest.main()