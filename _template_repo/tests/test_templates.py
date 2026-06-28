from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_ROOT = ROOT / "templates" / "repo"


def template_ids() -> list[str]:
    return sorted(path.name for path in TEMPLATES_ROOT.iterdir() if path.is_dir())


class TemplateManifestTest(unittest.TestCase):
    def test_templates_have_manifest_and_required_paths(self) -> None:
        for template_id in template_ids():
            with self.subTest(template_id=template_id):
                template_dir = TEMPLATES_ROOT / template_id
                manifest_path = template_dir / "template_manifest.json"
                self.assertTrue((template_dir / "TEMPLATE.md").is_file())
                self.assertTrue(manifest_path.is_file())

                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(manifest["template_id"], template_id)

                files_dir = template_dir / "files"
                for required_file in manifest["required_files"]:
                    self.assertTrue(
                        (files_dir / required_file).is_file(),
                        f"{template_id}: missing file {required_file}",
                    )
                for required_dir in manifest["required_directories"]:
                    self.assertTrue(
                        (files_dir / required_dir).is_dir(),
                        f"{template_id}: missing dir {required_dir}",
                    )

    def test_templates_do_not_contain_ds_store_files(self) -> None:
        ds_store_files = sorted(
            str(path.relative_to(ROOT)) for path in TEMPLATES_ROOT.rglob(".DS_Store")
        )
        self.assertEqual(ds_store_files, [])


class BootstrapScriptTest(unittest.TestCase):
    def test_bootstrap_script_generates_verifiable_repos(self) -> None:
        for template_id in template_ids():
            with self.subTest(template_id=template_id):
                with tempfile.TemporaryDirectory() as tmpdir:
                    project_name = f"sample_{template_id}"
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "scripts" / "bootstrap_repo.py"),
                            template_id,
                            project_name,
                            "--destination-root",
                            tmpdir,
                        ],
                        cwd=ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(
                        result.returncode,
                        0,
                        msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
                    )

                    destination = Path(tmpdir) / project_name
                    self.assertTrue((destination / "init.sh").is_file())
                    self.assertTrue((destination / ".gitignore").is_file())
                    self.assertTrue((destination / ".git").is_dir())
                    self.assertTrue((destination / "historico_versiones.md").is_file())
                    self.assertEqual(
                        (destination / "historico_versiones.md").read_text(
                            encoding="utf-8"
                        ),
                        "",
                    )
                    self.assertFalse((destination / ".claude").exists())
                    self.assertFalse((destination / ".codex").exists())
                    self.assertFalse((destination / ".devin").exists())
                    self.assert_git_root(destination)
                    self.assert_no_unresolved_placeholders(destination)

                    feature_list = json.loads(
                        (destination / "feature_list.json").read_text(encoding="utf-8")
                    )
                    bootstrap = next(
                        feature
                        for feature in feature_list["features"]
                        if feature["id"] == "F000"
                    )
                    self.assertEqual(bootstrap["status"], "done")

    def assert_no_unresolved_placeholders(self, destination: Path) -> None:
        unresolved: list[str] = []
        for path in destination.rglob("*"):
            relative = path.relative_to(destination)
            if ".git" in relative.parts:
                continue
            relative_path = str(relative)
            if "{{" in relative_path or "}}" in relative_path:
                unresolved.append(relative_path)
                continue
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "{{" in content or "}}" in content:
                unresolved.append(relative_path)
        self.assertEqual(unresolved, [])

    def assert_git_root(self, destination: Path) -> None:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=destination,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertEqual(Path(result.stdout.strip()).resolve(), destination.resolve())


if __name__ == "__main__":
    unittest.main()
