import unittest

import {{package_name}}
from {{package_name}}.graph import build_graph


class SmokeTest(unittest.TestCase):
    def test_package_imports(self) -> None:
        self.assertTrue(hasattr({{package_name}}, "run"))

    def test_run_returns_message(self) -> None:
        self.assertIn("{{project_name}}", {{package_name}}.run())

    def test_graph_builder_returns_template_metadata(self) -> None:
        graph = build_graph()
        self.assertEqual(graph["template_id"], "{{template_id}}")


if __name__ == "__main__":
    unittest.main()
