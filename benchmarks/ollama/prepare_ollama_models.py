from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

from benchmark_ollama import (
    api_url,
    compact_error,
    configured_models,
    get_available_models,
    load_json,
)


def pull_model(base_url: str, model_name: str, timeout: int) -> None:
    print(f"Baixando {model_name}...")
    payload = {"name": model_name, "stream": True}
    with requests.post(
        api_url(base_url, "/api/pull"),
        json=payload,
        timeout=timeout,
        stream=True,
    ) as response:
        response.raise_for_status()
        last_status = None
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            event: dict[str, Any] = json.loads(line)
            if event.get("error"):
                raise RuntimeError(event["error"])

            status = event.get("status")
            completed = event.get("completed")
            total = event.get("total")
            if completed and total:
                percent = (completed / total) * 100
                message = f"{status}: {percent:.1f}%"
            else:
                message = status

            if message and message != last_status:
                print(f"  {message}")
                last_status = message


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa modelos configurados usando a API local do Ollama."
    )
    parser.add_argument(
        "--config",
        default="benchmarks/ollama/config.example.json",
        help="Caminho para o arquivo JSON de configuração.",
    )
    parser.add_argument(
        "--model",
        action="append",
        help="Baixa apenas o modelo informado. Pode ser usado mais de uma vez.",
    )
    parser.add_argument(
        "--pull-all",
        action="store_true",
        help="Baixa todos os modelos configurados, mesmo que já apareçam no /api/tags.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Timeout por requisição de download, em segundos.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_json(Path(args.config))
    base_url = config.get("ollama_base_url", "http://localhost:11434")
    models = configured_models(config)

    if args.model:
        selected = set(args.model)
        models = [model for model in models if model["name"] in selected]
    if not models:
        print("Nenhum modelo selecionado.", file=sys.stderr)
        return 1

    try:
        available_models = get_available_models(base_url, timeout=30)
    except requests.RequestException as exc:
        print(
            f"Não foi possível conectar ao Ollama em {base_url}: {compact_error(exc)}",
            file=sys.stderr,
        )
        print("Inicie o Ollama antes de baixar os modelos.", file=sys.stderr)
        return 1

    for model in models:
        model_name = model["name"]
        if model_name in available_models and not args.pull_all:
            print(f"{model_name} já está disponível.")
            continue
        try:
            pull_model(base_url, model_name, args.timeout)
        except Exception as exc:  # noqa: BLE001 - downloads should continue
            print(f"Erro ao baixar {model_name}: {compact_error(exc)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
