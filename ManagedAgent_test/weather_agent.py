"""
Agente meteorológico con Managed Agents API.
Consulta el tiempo real de cualquier localidad vía wttr.in.

Requiere haber ejecutado setup.py primero.

Uso:
    python weather_agent.py Madrid
    python weather_agent.py "Buenos Aires"
    python weather_agent.py "¿Qué tiempo hace en Tokio?"
    python weather_agent.py          # modo interactivo
"""

import json
import sys
from pathlib import Path
from urllib.parse import quote as url_quote

import requests
from anthropic import Anthropic

CONFIG_PATH = Path(__file__).parent / "config.json"


# ---------------------------------------------------------------------------
# Lógica de la herramienta get_weather
# ---------------------------------------------------------------------------


def fetch_weather(location: str) -> dict:
    """Consulta wttr.in y devuelve los datos del tiempo actuales."""
    url = f"https://wttr.in/{url_quote(location, safe='')}?format=j1"
    respuesta = requests.get(url, timeout=10)
    respuesta.raise_for_status()

    datos = respuesta.json()
    if not datos.get("current_condition"):
        raise ValueError(f"No se encontraron datos para '{location}'")

    actual = datos["current_condition"][0]
    area_info = datos.get("nearest_area", [{}])[0]
    nombre_area = area_info.get("areaName", [{}])[0].get("value", location)
    pais = area_info.get("country", [{}])[0].get("value", "")

    return {
        "localidad": f"{nombre_area}, {pais}" if pais else nombre_area,
        "temperatura_c": actual["temp_C"],
        "sensacion_termica_c": actual["FeelsLikeC"],
        "descripcion": actual["weatherDesc"][0]["value"],
        "humedad_pct": actual["humidity"],
        "viento_kmh": actual["windspeedKmph"],
        "direccion_viento": actual["winddir16Point"],
        "visibilidad_km": actual["visibility"],
        "precipitacion_mm": actual["precipMM"],
        "presion_hpa": actual["pressure"],
    }


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Ejecuta la herramienta solicitada por el agente. Devuelve (resultado, es_error)."""
    if name != "get_weather":
        return f"Herramienta desconocida: {name}", True

    location = tool_input.get("location", "")
    print(f"\n  [Consultando clima para: {location}]", flush=True)

    try:
        datos = fetch_weather(location)
        return json.dumps(datos, ensure_ascii=False, indent=2), False
    except requests.HTTPError as exc:
        return f"Error HTTP al consultar '{location}': {exc}", True
    except requests.Timeout:
        return f"Tiempo de espera agotado al consultar '{location}'", True
    except Exception as exc:
        return f"Error: {exc}", True


# ---------------------------------------------------------------------------
# Bucle principal de la sesión
# ---------------------------------------------------------------------------


def run_session(client: Anthropic, session_id: str, question: str) -> None:
    """
    Abre el stream, envía la pregunta y gestiona el bucle de herramientas
    hasta que el agente termine (session.status_idle con end_turn).
    """
    is_first = True

    while True:
        with client.beta.sessions.events.stream(session_id) as stream:
            # En la primera iteración enviamos el mensaje dentro del stream (stream-first).
            # En iteraciones siguientes los tool results ya fueron enviados antes.
            if is_first:
                client.beta.sessions.events.send(
                    session_id,
                    events=[
                        {
                            "type": "user.message",
                            "content": [{"type": "text", "text": question}],
                        }
                    ],
                )
                is_first = False

            tool_calls: list = []
            terminated = False

            for event in stream:
                match event.type:
                    case "agent.message":
                        for block in event.content:
                            if block.type == "text":
                                print(block.text, end="", flush=True)
                    case "agent.custom_tool_use":
                        tool_calls.append(event)
                    case "session.status_idle":
                        # Salir del for: si hay tool_calls el outer-while enviará resultados.
                        # Si no, outer-while romperá.
                        break
                    case "session.status_terminated":
                        terminated = True
                        break
                    case "session.error":
                        print(f"\n[Error de sesión: {event}]", file=sys.stderr)
                        terminated = True
                        break

        if terminated or not tool_calls:
            break

        # Procesar todas las llamadas y enviar resultados en un solo evento.
        # El stream estará cerrado aquí; el agente reanudará cuando reciba los resultados.
        results = []
        for call in tool_calls:
            resultado, es_error = run_tool(call.name, call.input)
            results.append(
                {
                    "type": "user.custom_tool_result",
                    "custom_tool_use_id": call.id,
                    "content": [{"type": "text", "text": resultado}],
                    "is_error": es_error,
                }
            )

        client.beta.sessions.events.send(session_id, events=results)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------


def ask_weather(question: str) -> None:
    if not CONFIG_PATH.exists():
        print(
            "Error: config.json no encontrado.\n"
            "Ejecuta primero: python setup.py",
            file=sys.stderr,
        )
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    client = Anthropic()

    print("Iniciando sesión...", flush=True)
    session = client.beta.sessions.create(
        agent={
            "type": "agent",
            "id": config["agent_id"],
            "version": config["agent_version"],
        },
        environment_id=config["environment_id"],
        title=f"Clima: {question[:60]}",
    )
    print(f"Sesión: {session.id}\n", flush=True)

    try:
        run_session(client, session.id, question)
    finally:
        print("\n", flush=True)
        client.beta.sessions.archive(session.id)


def main() -> None:
    if len(sys.argv) > 1:
        raw = " ".join(sys.argv[1:])
        # Si parece un nombre de ciudad (sin signos de pregunta ni palabras clave),
        # reformular como pregunta.
        keywords = {"?", "tiempo", "clima", "weather", "lluev", "niev", "sol", "calor", "frío"}
        question = (
            raw
            if any(k in raw.lower() for k in keywords)
            else f"¿Qué tiempo hace en {raw}?"
        )
    else:
        localidad = input("¿Para qué localidad quieres saber el tiempo? ").strip()
        if not localidad:
            print("No se indicó ninguna localidad.", file=sys.stderr)
            sys.exit(1)
        question = f"¿Qué tiempo hace en {localidad}?"

    ask_weather(question)


if __name__ == "__main__":
    main()
