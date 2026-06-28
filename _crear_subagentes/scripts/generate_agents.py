#!/usr/bin/env python3
"""Generate tool-specific coding agents from common YAML files."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


NOTICE = (
    "AUTO-GENERATED FILE. DO NOT EDIT.\n"
    "Edit _contexto_agente_codificador/agents/common/{agent}.yaml instead."
)

GLOBAL_RULES_REMINDER = (
    "Las reglas globales del framework viven en "
    "`_contexto_agente_codificador/AGENTS.md`, `CHECKPOINTS.md` y "
    "`memory/*.md`. El harness debe "
    "cargarlas via `CLAUDE.md` / `AGENTS.md` global. Si detectas que faltan, "
    "leelas directamente desde la ruta del framework antes de actuar."
)

REQUIRED_FIELDS = {"name", "description", "instructions"}
CONTEXT_REPO_NAME = "_contexto_agente_codificador"
DEFAULT_OUTPUT_ROOT = Path("output") / "generated_agents"
DEFAULT_MODELS_FILE = Path("modelos.json")
MODEL_TARGETS = ("claude", "codex")

CLAUDE_TOOL_MAP = {
    "read": "Read",
    "search": "Grep",
    "list": "Glob",
    "shell": "Bash",
    "delegate": "Agent",
    "edit": "Edit",
    "write_progress": "Write",
    "update_progress": "Edit",
}


@dataclass(frozen=True)
class AgentDefinition:
    """Common agent definition loaded from agents/common."""

    name: str
    description: str
    role: str
    tools: list[str]
    instructions: str
    source_path: Path


@dataclass(frozen=True)
class ToolModelConfig:
    """Model defaults and per-agent overrides for one generated tool."""

    default: str
    agents: dict[str, str]


@dataclass(frozen=True)
class ModelConfig:
    """Models used when rendering tool-specific agents."""

    tools: dict[str, ToolModelConfig]

    def model_for(self, tool: str, agent_name: str) -> str:
        tool_config = self.tools[tool]
        return tool_config.agents.get(agent_name, tool_config.default)


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    common_dir = resolve_common_dir(args.common_dir, project_root)
    output_root = resolve_output_root(args.output_root, project_root)
    models_file = resolve_models_file(args.models_file, project_root)
    definitions = load_agent_definitions(common_dir)
    model_config = load_model_config(models_file)
    validate_model_config(model_config, definitions)

    generated_files: list[Path] = []
    for definition in definitions:
        generated_files.extend(
            generate_claude_agent(definition, output_root, model_config)
        )
        generated_files.extend(
            generate_codex_agent(definition, output_root, model_config)
        )
        generated_files.extend(generate_devin_agent(definition, output_root))

    print(f"Source common agents: {common_dir}")
    print(f"Models config: {models_file}")
    print(f"Output root: {output_root}")
    print("Generated files:")
    for path in generated_files:
        print(f"- {path}")
    print(f"Total: {len(generated_files)} files")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Claude, Codex and Devin agents from common YAML files."
    )
    parser.add_argument(
        "--common-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing common YAML agents. Defaults to "
            f"../{CONTEXT_REPO_NAME}/agents/common from this repo."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=(
            "Root where generated tool directories are written. "
            f"Defaults to {DEFAULT_OUTPUT_ROOT} in this repo."
        ),
    )
    parser.add_argument(
        "--models-file",
        type=Path,
        default=None,
        help=(
            "JSON file with Claude and Codex model defaults and agent overrides. "
            f"Defaults to {DEFAULT_MODELS_FILE} in this repo."
        ),
    )
    return parser.parse_args()


def resolve_common_dir(common_dir: Path | None, project_root: Path) -> Path:
    if common_dir is not None:
        return common_dir.expanduser().resolve()
    return (project_root.parent / CONTEXT_REPO_NAME / "agents" / "common").resolve()


def resolve_output_root(output_root: Path | None, project_root: Path) -> Path:
    if output_root is not None:
        return output_root.expanduser().resolve()
    return (project_root / DEFAULT_OUTPUT_ROOT).resolve()


def resolve_models_file(models_file: Path | None, project_root: Path) -> Path:
    if models_file is not None:
        return models_file.expanduser().resolve()
    return (project_root / DEFAULT_MODELS_FILE).resolve()


def load_model_config(models_file: Path) -> ModelConfig:
    if not models_file.exists():
        raise SystemExit(f"ERROR: models config file not found: {models_file}")

    try:
        raw_config = json.loads(models_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"ERROR: invalid JSON in models config: {models_file}"
        ) from error

    if not isinstance(raw_config, dict):
        raise SystemExit(
            f"ERROR: models config must be a JSON object: {models_file}"
        )

    tool_configs: dict[str, ToolModelConfig] = {}
    for tool in MODEL_TARGETS:
        raw_tool_config = raw_config.get(tool)
        if not isinstance(raw_tool_config, dict):
            raise SystemExit(f"ERROR: models config must define object '{tool}'")

        default_model = require_model_string(
            models_file,
            raw_tool_config,
            tool,
            "default",
        )
        raw_agents = raw_tool_config.get("agents", {})
        if not isinstance(raw_agents, dict):
            raise SystemExit(
                f"ERROR: models config '{tool}.agents' must be an object"
            )

        agent_models: dict[str, str] = {}
        for agent_name, model in raw_agents.items():
            if not isinstance(agent_name, str) or not agent_name.strip():
                raise SystemExit(
                    f"ERROR: models config '{tool}.agents' has an invalid agent name"
                )
            if not isinstance(model, str) or not model.strip():
                raise SystemExit(
                    f"ERROR: models config '{tool}.agents.{agent_name}' "
                    "must be a non-empty string"
                )
            agent_models[agent_name] = model

        tool_configs[tool] = ToolModelConfig(
            default=default_model,
            agents=agent_models,
        )

    return ModelConfig(tools=tool_configs)


def validate_model_config(
    model_config: ModelConfig,
    definitions: list[AgentDefinition],
) -> None:
    valid_agent_names = {definition.name for definition in definitions}
    for tool, tool_config in model_config.tools.items():
        unknown_agents = sorted(set(tool_config.agents) - valid_agent_names)
        if unknown_agents:
            raise SystemExit(
                f"ERROR: models config '{tool}.agents' references unknown agents: "
                f"{', '.join(unknown_agents)}"
            )


def require_model_string(
    path: Path,
    data: dict[str, object],
    tool: str,
    key: str,
) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(
            f"ERROR: models config '{tool}.{key}' must be a non-empty string: "
            f"{path}"
        )
    return value


def load_agent_definitions(common_dir: Path) -> list[AgentDefinition]:
    if not common_dir.exists():
        raise SystemExit(f"ERROR: common agents directory not found: {common_dir}")

    yaml_paths = sorted(common_dir.glob("*.yaml"))
    if not yaml_paths:
        raise SystemExit(f"ERROR: no YAML agent files found in {common_dir}")

    definitions = [parse_agent_yaml(path) for path in yaml_paths]
    names = [definition.name for definition in definitions]
    duplicated_names = sorted({name for name in names if names.count(name) > 1})
    if duplicated_names:
        raise SystemExit(f"ERROR: duplicated agent names: {', '.join(duplicated_names)}")

    return definitions


def parse_agent_yaml(path: Path) -> AgentDefinition:
    """Parse the small YAML subset used by agents/common/*.yaml.

    The parser intentionally avoids external dependencies. It supports:
    top-level scalar keys, top-level lists using ``- item`` and one literal
    block field using ``instructions: |``.
    """

    data: dict[str, str | list[str]] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        index += 1

        if not stripped or stripped.startswith("#"):
            continue

        if line.startswith(" ") or ":" not in line:
            raise ValueError(f"{path}: unexpected line: {line}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value == "|":
            block_lines: list[str] = []
            while index < len(lines):
                block_line = lines[index]
                index += 1
                if block_line.startswith("  "):
                    block_lines.append(block_line[2:])
                elif block_line == "":
                    block_lines.append("")
                else:
                    raise ValueError(
                        f"{path}: only one literal block is supported and it must be last"
                    )
            data[key] = "\n".join(block_lines).rstrip() + "\n"
            continue

        if value == "":
            items: list[str] = []
            while index < len(lines):
                item_line = lines[index]
                item_stripped = item_line.strip()
                if not item_stripped:
                    index += 1
                    continue
                if item_line.startswith("  - "):
                    items.append(unquote(item_line[4:].strip()))
                    index += 1
                    continue
                break
            data[key] = items
            continue

        data[key] = unquote(value)

    missing_fields = sorted(REQUIRED_FIELDS - data.keys())
    if missing_fields:
        raise ValueError(f"{path}: missing required fields: {', '.join(missing_fields)}")

    tools = data.get("tools", [])
    if not isinstance(tools, list):
        raise ValueError(f"{path}: tools must be a list")

    return AgentDefinition(
        name=require_string(path, data, "name"),
        description=require_string(path, data, "description"),
        role=str(data.get("role", "")),
        tools=tools,
        instructions=require_string(path, data, "instructions"),
        source_path=path,
    )


def require_string(path: Path, data: dict[str, str | list[str]], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}: {key} must be a non-empty string")
    return value


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def generate_claude_agent(
    definition: AgentDefinition,
    output_root: Path,
    model_config: ModelConfig,
) -> list[Path]:
    destination = output_root / ".claude" / "agents" / f"{definition.name}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    model = model_config.model_for("claude", definition.name)
    destination.write_text(render_claude_agent(definition, model), encoding="utf-8")
    return [destination]


def generate_codex_agent(
    definition: AgentDefinition,
    output_root: Path,
    model_config: ModelConfig,
) -> list[Path]:
    destination = output_root / ".codex" / "agents" / f"{definition.name}.toml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    model = model_config.model_for("codex", definition.name)
    destination.write_text(render_codex_agent(definition, model), encoding="utf-8")
    return [destination]


def generate_devin_agent(
    definition: AgentDefinition,
    output_root: Path,
) -> list[Path]:
    destination = output_root / ".devin" / "agents" / definition.name / "AGENT.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_devin_agent(definition), encoding="utf-8")
    return [destination]


def render_claude_agent(definition: AgentDefinition, model: str) -> str:
    tools = map_claude_tools(definition.tools)
    notice_lines = NOTICE.format(agent=definition.name).splitlines()
    frontmatter = [
        "---",
        f"# {notice_lines[0]}",
        f"# {notice_lines[1]}",
        f"name: {definition.name}",
        f"description: {definition.description}",
        f"model: {model}",
    ]
    if tools:
        frontmatter.append("tools:")
        frontmatter.extend(f"  - {tool}" for tool in tools)
    frontmatter.append("---")

    return "\n".join(
        [
            *frontmatter,
            "",
            f"# {definition.name}",
            "",
            "## Reglas globales",
            "",
            f"> {GLOBAL_RULES_REMINDER}",
            "",
            "## Instrucciones del rol",
            "",
            definition.instructions.rstrip(),
            "",
        ]
    )


def render_codex_agent(definition: AgentDefinition, model: str) -> str:
    notice_lines = NOTICE.format(agent=definition.name).splitlines()
    instructions = render_combined_instructions(definition)
    return "\n".join(
        [
            f"# {notice_lines[0]}",
            f"# {notice_lines[1]}",
            f'name = "{toml_escape(definition.name)}"',
            f'description = "{toml_escape(definition.description)}"',
            f'model = "{toml_escape(model)}"',
            'developer_instructions = """',
            instructions.replace('"""', '\\"\\"\\"'),
            '"""',
            "",
        ]
    )


def render_devin_agent(definition: AgentDefinition) -> str:
    notice_lines = NOTICE.format(agent=definition.name).splitlines()
    tools = ", ".join(definition.tools) if definition.tools else "none"
    return "\n".join(
        [
            f"<!-- {notice_lines[0]} -->",
            f"<!-- {notice_lines[1]} -->",
            "",
            f"# {definition.name}",
            "",
            f"**Description:** {definition.description}",
            "",
            f"**Role:** {definition.role or 'general'}",
            "",
            f"**Tools:** {tools}",
            "",
            "## Reglas globales",
            "",
            f"> {GLOBAL_RULES_REMINDER}",
            "",
            "## Instrucciones del rol",
            "",
            definition.instructions.rstrip(),
            "",
        ]
    )


def map_claude_tools(tools: Iterable[str]) -> list[str]:
    mapped_tools: list[str] = []
    for tool in tools:
        mapped_tool = CLAUDE_TOOL_MAP.get(tool, tool)
        if mapped_tool not in mapped_tools:
            mapped_tools.append(mapped_tool)
    return mapped_tools


def render_combined_instructions(definition: AgentDefinition) -> str:
    return "\n\n".join(
        [
            "## Reglas globales",
            f"> {GLOBAL_RULES_REMINDER}",
            "## Instrucciones del rol",
            definition.instructions.rstrip(),
        ]
    )


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    raise SystemExit(main())
