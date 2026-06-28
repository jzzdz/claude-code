#!/usr/bin/env python3
"""Create a destination repo from a _template_repo template."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IGNORED_NAMES = {".DS_Store", "__pycache__", ".claude", ".codex", ".devin"}
GENERATED_METADATA_NAMES = {".git"}
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}]+\}\}")


class BootstrapError(Exception):
    """Raised when a repo cannot be generated from a template."""


@dataclass(frozen=True)
class BootstrapConfig:
    template_id: str
    project_name: str
    package_name: str
    destination_root: Path
    verify: bool
    init_git: bool


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def package_name_from_project(project_name: str) -> str:
    package_name = re.sub(r"\W+", "_", project_name).strip("_").lower()
    if not package_name:
        raise BootstrapError("project_name no genera un nombre de paquete valido")
    if package_name[0].isdigit():
        package_name = f"pkg_{package_name}"
    return package_name


def load_manifest(root: Path, template_id: str) -> dict[str, Any]:
    manifest_path = root / "templates" / "repo" / template_id / "template_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BootstrapError(f"no existe manifest para template: {template_id}") from exc
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"manifest JSON invalido: {manifest_path}") from exc

    if manifest.get("template_id") != template_id:
        raise BootstrapError(
            f"template_id incoherente en manifest: {manifest.get('template_id')!r}"
        )
    return manifest


def validate_template_source(root: Path, template_id: str, manifest: dict[str, Any]) -> None:
    template_dir = root / "templates" / "repo" / template_id
    files_dir = template_dir / "files"
    if not (template_dir / "TEMPLATE.md").is_file():
        raise BootstrapError(f"falta TEMPLATE.md en {template_id}")
    if not files_dir.is_dir():
        raise BootstrapError(f"falta directorio files/ en {template_id}")

    for required_file in manifest.get("required_files", []):
        if not (files_dir / required_file).is_file():
            raise BootstrapError(f"falta archivo requerido en template: {required_file}")

    for required_dir in manifest.get("required_directories", []):
        if not (files_dir / required_dir).is_dir():
            raise BootstrapError(f"falta directorio requerido en template: {required_dir}")

    forbidden_dirs = find_ignored_paths(files_dir)
    if forbidden_dirs:
        raise BootstrapError(
            f"la template contiene directorios o archivos ignorados: {forbidden_dirs}"
        )


def render(value: str, config: BootstrapConfig) -> str:
    replacements = {
        "{{project_name}}": config.project_name,
        "{{package_name}}": config.package_name,
        "{{template_id}}": config.template_id,
    }
    for placeholder, replacement in replacements.items():
        value = value.replace(placeholder, replacement)
    return value


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_NAMES for part in path.parts)


def is_generated_metadata(path: Path) -> bool:
    return any(part in GENERATED_METADATA_NAMES for part in path.parts)


def copy_template_files(root: Path, config: BootstrapConfig) -> Path:
    source_dir = root / "templates" / "repo" / config.template_id / "files"
    destination = config.destination_root / config.project_name
    if destination.exists():
        raise BootstrapError(f"el destino ya existe: {destination}")

    for source_path in sorted(source_dir.rglob("*")):
        relative_path = source_path.relative_to(source_dir)
        if should_skip(relative_path):
            continue

        rendered_parts = [render(part, config) for part in relative_path.parts]
        target_path = destination.joinpath(*rendered_parts)

        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(source_path, target_path)
        else:
            target_path.write_text(render(content, config), encoding="utf-8")

    init_path = destination / "init.sh"
    if init_path.exists():
        init_path.chmod(init_path.stat().st_mode | 0o111)
    return destination


def rendered_path(path: str, config: BootstrapConfig) -> str:
    return render(path, config)


def assert_generated_repo(
    destination: Path, config: BootstrapConfig, manifest: dict[str, Any]
) -> None:
    missing_files = [
        path
        for path in manifest.get("required_files", [])
        if not (destination / rendered_path(path, config)).is_file()
    ]
    missing_dirs = [
        path
        for path in manifest.get("required_directories", [])
        if not (destination / rendered_path(path, config)).is_dir()
    ]
    if missing_files:
        raise BootstrapError(f"faltan archivos generados: {missing_files}")
    if missing_dirs:
        raise BootstrapError(f"faltan directorios generados: {missing_dirs}")

    init_path = destination / "init.sh"
    if init_path.exists() and not init_path.stat().st_mode & 0o111:
        raise BootstrapError("init.sh existe pero no es ejecutable")

    unresolved = find_unresolved_placeholders(destination)
    if unresolved:
        raise BootstrapError(f"quedan placeholders sin resolver: {unresolved[:5]}")

    ignored_paths = find_ignored_paths(destination)
    if ignored_paths:
        raise BootstrapError(f"se copiaron archivos ignorados: {ignored_paths}")


def find_ignored_paths(root: Path) -> list[str]:
    return sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if should_skip(path.relative_to(root))
    )


def find_unresolved_placeholders(destination: Path) -> list[str]:
    matches: list[str] = []
    for path in destination.rglob("*"):
        relative = path.relative_to(destination)
        if is_generated_metadata(relative):
            continue
        relative_path = str(relative)
        if PLACEHOLDER_PATTERN.search(relative_path):
            matches.append(relative_path)
            continue
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if PLACEHOLDER_PATTERN.search(content):
            matches.append(relative_path)
    return matches


def run_verification(destination: Path, command: str) -> None:
    if not command:
        return
    subprocess.run(shlex.split(command), cwd=destination, check=True)


def initialize_git_repo(destination: Path) -> None:
    git = shutil.which("git")
    if git is None:
        raise BootstrapError("git no esta disponible para inicializar el repo destino")

    result = subprocess.run(
        [git, "init"],
        cwd=destination,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip()
        raise BootstrapError(f"git init fallo: {output}")

    top_level = subprocess.run(
        [git, "rev-parse", "--show-toplevel"],
        cwd=destination,
        text=True,
        capture_output=True,
        check=False,
    )
    if top_level.returncode != 0:
        output = top_level.stderr.strip() or top_level.stdout.strip()
        raise BootstrapError(f"no se pudo verificar el repo Git: {output}")
    if Path(top_level.stdout.strip()).resolve() != destination.resolve():
        raise BootstrapError("git init no dejo el destino como repo Git independiente")


def mark_bootstrap_done(destination: Path) -> None:
    feature_list_path = destination / "feature_list.json"
    try:
        feature_list = json.loads(feature_list_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return

    for feature in feature_list.get("features", []):
        if feature.get("id") == "F000":
            feature["status"] = "done"
            break
    feature_list_path.write_text(
        json.dumps(feature_list, indent=2) + "\n",
        encoding="utf-8",
    )

    current_path = destination / "progress" / "current.md"
    if current_path.exists():
        current = current_path.read_text(encoding="utf-8")
        current = current.replace(
            "- Pendiente ejecutar o registrar el resultado final de `./init.sh` si el agente\n"
            "  de bootstrap todavia no lo ha hecho.",
            "- `./init.sh` ejecutado correctamente durante el bootstrap.",
        )
        current_path.write_text(current, encoding="utf-8")

    history_path = destination / "progress" / "history.md"
    if history_path.exists():
        history = history_path.read_text(encoding="utf-8")
        verification_line = "- Verificacion ejecutada: `./init.sh` completado correctamente."
        if verification_line not in history:
            history = history.rstrip() + f"\n{verification_line}\n"
            history_path.write_text(history, encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a repo from templates/repo/<template_id>/files."
    )
    parser.add_argument("template_id", help="Template id, for example langgraph_agent")
    parser.add_argument("project_name", help="Destination repo name")
    parser.add_argument(
        "--package-name",
        help="Importable Python package name. Defaults to a normalized project name.",
    )
    parser.add_argument(
        "--destination-root",
        type=Path,
        default=Path(".."),
        help="Directory where the new repo directory is created. Defaults to the parent.",
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Generate the repo without running its verification command.",
    )
    parser.add_argument(
        "--skip-git-init",
        action="store_true",
        help="Generate the repo without running git init.",
    )
    return parser


def create_repo(config: BootstrapConfig) -> Path:
    root = repo_root()
    manifest = load_manifest(root, config.template_id)
    validate_template_source(root, config.template_id, manifest)
    destination = copy_template_files(root, config)
    assert_generated_repo(destination, config, manifest)
    if config.init_git:
        initialize_git_repo(destination)
    if config.verify:
        run_verification(destination, manifest.get("verification_command", ""))
        mark_bootstrap_done(destination)
        assert_generated_repo(destination, config, manifest)
    return destination


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    try:
        package_name = args.package_name or package_name_from_project(args.project_name)
        config = BootstrapConfig(
            template_id=args.template_id,
            project_name=args.project_name,
            package_name=package_name,
            destination_root=args.destination_root,
            verify=not args.skip_verification,
            init_git=not args.skip_git_init,
        )
        destination = create_repo(config)
    except (BootstrapError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"OK: repo creado en {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
