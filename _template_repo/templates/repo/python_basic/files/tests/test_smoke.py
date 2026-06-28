import unittest

import {{package_name}}


class SmokeTest(unittest.TestCase):
    def test_package_imports(self) -> None:
        self.assertTrue(hasattr({{package_name}}, "run"))

    def test_run_returns_message(self) -> None:
        self.assertIn("{{project_name}}", {{package_name}}.run())


if __name__ == "__main__":
    unittest.main()
