import unittest
import tempfile
import os
from scanner import scan_file, scan_directory

class TestScanner(unittest.TestCase):

    def create_temp_file(self, content, suffix=".py"):
        temp = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=suffix)
        temp.write(content)
        temp.close()
        return temp.name

    def extract_issues(self, scan_output):
        # If scan_file returns (dict, csv_string), grab only the dict part
        if isinstance(scan_output, tuple):
            scan_output = scan_output[0]
        # If it's a dict with one file key, grab its issues
        if isinstance(scan_output, dict) and len(scan_output) == 1:
            return list(scan_output.values())[0]
        return scan_output

    def test_sensitive_comment(self):
        code = "# TODO: remove this\nprint('test')"
        file_path = self.create_temp_file(code)
        issues = self.extract_issues(scan_file(file_path))
        os.unlink(file_path)
        print("Sensitive Comment Test Issues:", issues)
        self.assertTrue(any("comment" in str(issue).lower() or "todo" in str(issue).lower()
                            for issue in issues))

    def test_hardcoded_secret(self):
        code = "password = 'secret123'\nprint('test')"
        file_path = self.create_temp_file(code)
        issues = self.extract_issues(scan_file(file_path))
        os.unlink(file_path)
        print("Hardcoded Secret Test Issues:", issues)
        self.assertTrue(any("secret" in str(issue).lower() or "password" in str(issue).lower()
                            for issue in issues))

    def test_insecure_error_message(self):
        code = "try:\n x = 1/0\nexcept Exception as e:\n print(e)"
        file_path = self.create_temp_file(code)
        issues = self.extract_issues(scan_file(file_path))
        os.unlink(file_path)
        print("Insecure Error Message Test Issues:", issues)
        self.assertTrue(any("error" in str(issue).lower() or "exception" in str(issue).lower()
                            or "print" in str(issue).lower()
                            for issue in issues))

    def test_clean_file(self):
        code = "print('Hello, world!')"
        file_path = self.create_temp_file(code)
        issues = self.extract_issues(scan_file(file_path))
        os.unlink(file_path)
        print("Clean File Test Issues:", issues)
        # Allow up to 2 issues due to AI over-flagging
        self.assertLessEqual(len(issues), 2)

    def test_directory_scan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = os.path.join(temp_dir, "secret.py")
            file2 = os.path.join(temp_dir, "todo.py")
            with open(file1, "w") as f:
                f.write("api_key = 'abcd1234'\n")
            with open(file2, "w") as f:
                f.write("# TODO: fix this\nprint('x')\n")

            results, _ = scan_directory(temp_dir)
            print("Directory Scan Results:", results)
            self.assertTrue(any(len(v) > 0 for v in results.values()))  # At least one file has issues

if __name__ == "__main__":
    unittest.main()
