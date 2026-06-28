"""
Configuración inicial del agente meteorológico (ejecutar una sola vez).

Crea el agente y el entorno en Managed Agents API y guarda los IDs en config.json.

Uso:
    python setup.py
"""

import json
import sys
from pathlib import Path

from anthropic import Anthropic

CONFIG_PATH = Path(__file__).parent / "config.json"


def main() -> None:
    if CONFIG_PATH.exists():
        print(f"Ya existe configuración en {CONFIG_PATH}. Elimínala para recrear.")
        sys.exit(0)

    client = Anthropic()

    print("Creando agente...")
    agent = client.beta.agents.create(
        name="Agente del Clima",
        model="claude-opus-4-7",
        system=(
            "Eres un asistente meteorológico. Cuando el usuario pregunte por el "
            "tiempo o clima de una localidad, usa la herramienta get_weather para "
            "obtener datos actuales. Responde de forma clara, amigable y en el "
            "idioma del usuario. Incluye temperatura, sensación térmica, descripción "
            "del cielo, humedad y viento en tu respuesta."
        ),
        tools=[
            {
                "type": "custom",
                "name": "get_weather",
                "description": (
                    "Obtiene el tiempo actual para una localidad. "
                    "Úsala siempre que el usuario pregunte por el clima o el tiempo."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": (
                                "Nombre de la ciudad o localidad, "
                                "por ejemplo: 'Madrid', 'Buenos Aires', 'New York'."
                            ),
                        }
                    },
                    "required": ["location"],
                },
            }
        ],
    )
    print(f"  Agente creado: {agent.id} (versión {agent.version})")

    print("Creando entorno...")
    environment = client.beta.environments.create(
        name="weather-agent-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"  Entorno creado: {environment.id}")

    config = {
        "agent_id": agent.id,
        "agent_version": agent.version,
        "environment_id": environment.id,
    }
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    print(f"\nConfiguración guardada en {CONFIG_PATH}")
    print("\nSetup completado. Ahora puedes ejecutar:")
    print("  python weather_agent.py Madrid")
    print("  python weather_agent.py '¿Qué tiempo hace en Tokio?'")


if __name__ == "__main__":
    main()
