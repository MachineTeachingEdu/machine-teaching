from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import platform
import shutil
import statistics
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import requests

try:
    import psutil
except ImportError:  # pragma: no cover - optional runtime dependency
    psutil = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_PACKAGE_ROOT = PROJECT_ROOT / "machineteaching"


def ensure_project_import_path() -> None:
    package_path = str(PROJECT_PACKAGE_ROOT)
    if package_path not in sys.path:
        sys.path.insert(0, package_path)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def api_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def now_timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def ns_to_seconds(value: Any) -> float | None:
    if not isinstance(value, (int, float)) or value <= 0:
        return None
    return value / 1_000_000_000


def bytes_to_mb(value: int | float | None) -> float | None:
    if value is None:
        return None
    return round(value / (1024 * 1024), 3)


def compact_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {error}"


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil((percent / 100) * len(ordered)) - 1)
    return ordered[index]


def numeric_stats(values: list[float]) -> dict[str, float | int | None]:
    cleaned = [value for value in values if isinstance(value, (int, float))]
    if not cleaned:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "stdev": None,
            "p95": None,
            "min": None,
            "max": None,
        }

    return {
        "count": len(cleaned),
        "mean": round(statistics.mean(cleaned), 6),
        "median": round(statistics.median(cleaned), 6),
        "stdev": round(statistics.stdev(cleaned), 6) if len(cleaned) > 1 else 0.0,
        "p95": round(percentile(cleaned, 95), 6),
        "min": round(min(cleaned), 6),
        "max": round(max(cleaned), 6),
    }


def build_overcode_feedback_prompt(item: dict[str, Any]) -> dict[str, Any]:
    ensure_project_import_path()
    try:
        from overcode.services.llm_service import _build_prompt
    except ImportError as exc:
        raise RuntimeError(
            "Não foi possível importar o construtor de prompt do OverCode."
        ) from exc

    code = item.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Casos de feedback precisam conter o campo 'code'.")

    mode = item.get("mode") or "student"
    if mode not in ("student", "group"):
        raise ValueError("O campo 'mode' deve ser 'student' ou 'group'.")

    prompt, has_statement, has_grading_context, grading_status = _build_prompt(
        code,
        exercise_statement=item.get("exercise_statement"),
        correction_evidence=item.get("correction_evidence"),
        mode=mode,
        ignored=bool(item.get("ignored", False)),
    )
    return {
        "prompt": prompt,
        "prompt_builder": "overcode.services.llm_service._build_prompt",
        "postprocess": "overcode_feedback",
        "mode": mode,
        "ignored": bool(item.get("ignored", False)),
        "has_statement": has_statement,
        "has_grading_context": has_grading_context,
        "grading_status": grading_status,
    }


def normalize_prompt_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError(f"Prompt inválido na posição {index}.")

    source_type = item.get("type") or "raw_prompt"
    prompt_data: dict[str, Any]
    if source_type == "overcode_feedback_case" or item.get("code"):
        prompt_data = build_overcode_feedback_prompt(item)
        source_type = "overcode_feedback_case"
    elif item.get("prompt"):
        prompt_data = {
            "prompt": item["prompt"],
            "prompt_builder": item.get("prompt_builder") or "raw",
            "postprocess": item.get("postprocess"),
            "mode": item.get("mode"),
            "ignored": bool(item.get("ignored", False)),
            "has_statement": item.get("has_statement"),
            "has_grading_context": item.get("has_grading_context"),
            "grading_status": item.get("grading_status"),
        }
    else:
        raise ValueError(
            f"Prompt inválido na posição {index}: informe 'prompt' ou um caso com 'code'."
        )

    prompt = prompt_data["prompt"]
    return {
        "id": item.get("id") or f"prompt_{index}",
        "category": item.get("category") or "feedback",
        "source_type": source_type,
        "prompt": prompt,
        "prompt_chars": len(prompt),
        "options": item.get("options") or {},
        "expected_focus": item.get("expected_focus") or [],
        **{key: value for key, value in prompt_data.items() if key != "prompt"},
    }


def read_prompts(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if isinstance(data, dict) and "feedback_cases" in data:
        prompt_items = data["feedback_cases"]
    elif isinstance(data, dict):
        prompt_items = data.get("prompts", data)
    else:
        prompt_items = data

    if not isinstance(prompt_items, list):
        raise ValueError(
            "O arquivo de prompts deve conter uma lista, 'prompts' ou 'feedback_cases'."
        )

    return [
        normalize_prompt_item(item, index)
        for index, item in enumerate(prompt_items, start=1)
    ]


def configured_models(config: dict[str, Any]) -> list[dict[str, Any]]:
    models = []
    for item in config.get("models", []):
        if isinstance(item, str):
            models.append({"name": item, "label": item, "options": {}})
            continue
        if isinstance(item, dict) and item.get("name"):
            models.append(
                {
                    "name": item["name"],
                    "label": item.get("label") or item["name"],
                    "options": item.get("options") or {},
                }
            )
    if not models:
        raise ValueError("Nenhum modelo configurado.")
    return models


def get_ollama_version(base_url: str, timeout: int) -> dict[str, Any] | None:
    try:
        response = requests.get(api_url(base_url, "/api/version"), timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def get_available_models(base_url: str, timeout: int) -> dict[str, dict[str, Any]]:
    response = requests.get(api_url(base_url, "/api/tags"), timeout=timeout)
    response.raise_for_status()
    models = response.json().get("models", [])
    available = {}
    for model in models:
        name = model.get("name") or model.get("model")
        if name:
            available[name] = model
    return available


def get_nvidia_gpu_info() -> list[dict[str, Any]]:
    if not shutil.which("nvidia-smi"):
        return []

    command = [
        "nvidia-smi",
        "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.SubprocessError, OSError):
        return []

    gpus = []
    for line in result.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) >= 3:
            gpus.append(
                {
                    "name": parts[0],
                    "memory_total_mb": parts[1],
                    "driver_version": parts[2],
                }
            )
    return gpus


def sample_nvidia_gpu() -> dict[str, float | None]:
    if not shutil.which("nvidia-smi"):
        return {}

    command = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.SubprocessError, OSError):
        return {}

    gpu_utils = []
    gpu_memory = []
    for line in result.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) >= 2:
            try:
                gpu_utils.append(float(parts[0]))
                gpu_memory.append(float(parts[1]))
            except ValueError:
                continue

    if not gpu_utils:
        return {}

    return {
        "gpu_util_percent_avg_visible": statistics.mean(gpu_utils),
        "gpu_util_percent_max_visible": max(gpu_utils),
        "gpu_memory_used_mb_total": sum(gpu_memory),
        "gpu_count_visible": len(gpu_utils),
    }


class ResourceMonitor:
    def __init__(self, interval_seconds: float) -> None:
        self.interval_seconds = max(interval_seconds, 0.1)
        self.samples: list[dict[str, Any]] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if psutil:
            psutil.cpu_percent(interval=None)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, float | int | None]:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval_seconds * 2)
        return self.summary()

    def _run(self) -> None:
        while not self._stop.is_set():
            self.samples.append(self._sample())
            self._stop.wait(self.interval_seconds)

    def _sample(self) -> dict[str, Any]:
        sample: dict[str, Any] = {"sample_time": time.time()}
        if psutil:
            memory = psutil.virtual_memory()
            sample.update(
                {
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "ram_used_mb": bytes_to_mb(memory.used),
                    "ram_percent": memory.percent,
                    "ollama_rss_mb": self._ollama_rss_mb(),
                }
            )
        sample.update(sample_nvidia_gpu())
        return sample

    def _ollama_rss_mb(self) -> float | None:
        if not psutil:
            return None

        total_rss = 0
        found = False
        for process in psutil.process_iter(["name", "cmdline", "memory_info"]):
            try:
                info = process.info
                name = (info.get("name") or "").lower()
                cmdline = " ".join(info.get("cmdline") or []).lower()
                if "ollama" not in name and "ollama" not in cmdline:
                    continue
                memory_info = info.get("memory_info")
                if memory_info:
                    total_rss += memory_info.rss
                    found = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return bytes_to_mb(total_rss) if found else None

    def summary(self) -> dict[str, float | int | None]:
        keys = [
            "cpu_percent",
            "ram_used_mb",
            "ram_percent",
            "ollama_rss_mb",
            "gpu_util_percent_avg_visible",
            "gpu_util_percent_max_visible",
            "gpu_memory_used_mb_total",
        ]
        summary: dict[str, float | int | None] = {
            "resource_sample_count": len(self.samples)
        }
        for key in keys:
            values = [
                sample[key]
                for sample in self.samples
                if isinstance(sample.get(key), (int, float))
            ]
            summary[f"{key}_avg"] = round(statistics.mean(values), 6) if values else None
            summary[f"{key}_max"] = round(max(values), 6) if values else None
        return summary


def call_ollama_generate(
    *,
    base_url: str,
    model_name: str,
    prompt: str,
    options: dict[str, Any],
    keep_alive: str | None,
    timeout: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model_name,
        "prompt": prompt,
        "stream": True,
    }
    if options:
        payload["options"] = options
    if keep_alive:
        payload["keep_alive"] = keep_alive

    started_at = time.perf_counter()
    first_token_at = None
    response_parts = []
    final_chunk: dict[str, Any] = {}

    with requests.post(
        api_url(base_url, "/api/generate"),
        json=payload,
        timeout=timeout,
        stream=True,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            chunk = json.loads(line)
            if chunk.get("error"):
                raise RuntimeError(chunk["error"])

            text = chunk.get("response")
            if isinstance(text, str) and text:
                if first_token_at is None:
                    first_token_at = time.perf_counter()
                response_parts.append(text)

            if chunk.get("done"):
                final_chunk = chunk

    ended_at = time.perf_counter()
    eval_count = final_chunk.get("eval_count")
    eval_duration = final_chunk.get("eval_duration")
    eval_duration_seconds = ns_to_seconds(eval_duration)
    tokens_per_second = None
    if isinstance(eval_count, int) and eval_duration_seconds:
        tokens_per_second = round(eval_count / eval_duration_seconds, 6)

    raw_response_text = "".join(response_parts).strip()
    return {
        "raw_response_text": raw_response_text,
        "raw_response_chars": len(raw_response_text),
        "response_text": raw_response_text,
        "response_chars": len(raw_response_text),
        "wall_time_seconds": round(ended_at - started_at, 6),
        "ttft_seconds": round(first_token_at - started_at, 6)
        if first_token_at is not None
        else None,
        "ollama_total_duration_seconds": ns_to_seconds(final_chunk.get("total_duration")),
        "ollama_load_duration_seconds": ns_to_seconds(final_chunk.get("load_duration")),
        "ollama_prompt_eval_duration_seconds": ns_to_seconds(
            final_chunk.get("prompt_eval_duration")
        ),
        "ollama_eval_duration_seconds": eval_duration_seconds,
        "prompt_eval_count": final_chunk.get("prompt_eval_count"),
        "eval_count": eval_count,
        "tokens_per_second": tokens_per_second,
    }


def postprocess_overcode_feedback(
    raw_text: str,
    prompt: dict[str, Any],
) -> dict[str, Any]:
    ensure_project_import_path()
    try:
        from overcode.services.llm_comment_processing import (
            correctness_conflict_fallback,
            has_correctness_conflict,
            prepare_response,
            validation_errors,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Não foi possível importar o pós-processamento de feedback do OverCode."
        ) from exc

    has_statement = bool(prompt.get("has_statement"))
    has_grading_context = bool(prompt.get("has_grading_context"))
    grading_status = prompt.get("grading_status")
    mode = prompt.get("mode")

    raw_errors = validation_errors(
        raw_text,
        has_statement=has_statement,
        has_grading_context=has_grading_context,
        grading_status=grading_status,
        mode=mode,
    )
    processed_text = prepare_response(raw_text, grading_status=grading_status)
    fallback_applied = False

    if has_correctness_conflict(raw_errors, grading_status=grading_status):
        processed_text = correctness_conflict_fallback(grading_status)
        fallback_applied = True

    processed_errors = validation_errors(
        processed_text,
        has_statement=has_statement,
        has_grading_context=has_grading_context,
        grading_status=grading_status,
        mode=mode,
    )
    return {
        "response_text": processed_text or raw_text,
        "response_chars": len(processed_text or raw_text),
        "postprocessing_applied": True,
        "correctness_conflict_fallback_applied": fallback_applied,
        "validation_errors_before": json.dumps(raw_errors, ensure_ascii=False),
        "validation_errors_after": json.dumps(processed_errors, ensure_ascii=False),
        "validation_error_count_before": len(raw_errors),
        "validation_error_count_after": len(processed_errors),
    }


def run_single_test(
    *,
    run_id: str,
    base_url: str,
    model: dict[str, Any],
    model_metadata: dict[str, Any],
    prompt: dict[str, Any],
    repetition: int,
    global_options: dict[str, Any],
    keep_alive: str | None,
    timeout: int,
    resource_interval: float,
) -> dict[str, Any]:
    options = dict(global_options)
    options.update(model.get("options") or {})
    options.update(prompt.get("options") or {})

    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    monitor = ResourceMonitor(resource_interval)
    monitor.start()
    try:
        result = call_ollama_generate(
            base_url=base_url,
            model_name=model["name"],
            prompt=prompt["prompt"],
            options=options,
            keep_alive=keep_alive,
            timeout=timeout,
        )
        if prompt.get("postprocess") == "overcode_feedback":
            result.update(
                postprocess_overcode_feedback(
                    result.get("raw_response_text") or "",
                    prompt,
                )
            )
        else:
            result["postprocessing_applied"] = False
        success = True
        error = None
    except Exception as exc:  # noqa: BLE001 - benchmark rows should capture failures
        result = {}
        success = False
        error = compact_error(exc)
    finally:
        resources = monitor.stop()

    details = model_metadata.get("details") or {}
    return {
        "run_id": run_id,
        "started_at": started_at,
        "model": model["name"],
        "model_label": model["label"],
        "model_digest": model_metadata.get("digest"),
        "model_size_bytes": model_metadata.get("size"),
        "model_parameter_size": details.get("parameter_size"),
        "model_quantization_level": details.get("quantization_level"),
        "prompt_id": prompt["id"],
        "prompt_category": prompt["category"],
        "prompt_source_type": prompt.get("source_type"),
        "prompt_builder": prompt.get("prompt_builder"),
        "prompt_chars": prompt.get("prompt_chars"),
        "prompt_mode": prompt.get("mode"),
        "prompt_has_statement": prompt.get("has_statement"),
        "prompt_has_grading_context": prompt.get("has_grading_context"),
        "prompt_grading_status": prompt.get("grading_status"),
        "repetition": repetition,
        "success": success,
        "error": error,
        "generation_options": json.dumps(options, ensure_ascii=False, sort_keys=True),
        **result,
        **resources,
    }


def run_warmups(
    *,
    base_url: str,
    model: dict[str, Any],
    prompt: dict[str, Any],
    global_options: dict[str, Any],
    keep_alive: str | None,
    timeout: int,
    warmup_runs: int,
) -> list[str]:
    errors = []
    options = dict(global_options)
    options.update(model.get("options") or {})
    options.update(prompt.get("options") or {})
    for _ in range(warmup_runs):
        try:
            call_ollama_generate(
                base_url=base_url,
                model_name=model["name"],
                prompt=prompt["prompt"],
                options=options,
                keep_alive=keep_alive,
                timeout=timeout,
            )
        except Exception as exc:  # noqa: BLE001 - warmup errors are diagnostic
            errors.append(compact_error(exc))
    return errors


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def summarize_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((row["model"], row["prompt_id"]), []).append(row)
        groups.setdefault((row["model"], "__all__"), []).append(row)

    summary_rows = []
    for (model, prompt_id), group_rows in sorted(groups.items()):
        success_rows = [row for row in group_rows if row.get("success")]
        total = len(group_rows)
        successes = len(success_rows)

        wall = numeric_stats(
            [
                row.get("wall_time_seconds")
                for row in success_rows
                if isinstance(row.get("wall_time_seconds"), (int, float))
            ]
        )
        ttft = numeric_stats(
            [
                row.get("ttft_seconds")
                for row in success_rows
                if isinstance(row.get("ttft_seconds"), (int, float))
            ]
        )
        tps = numeric_stats(
            [
                row.get("tokens_per_second")
                for row in success_rows
                if isinstance(row.get("tokens_per_second"), (int, float))
            ]
        )
        ram = numeric_stats(
            [
                row.get("ram_used_mb_max")
                for row in success_rows
                if isinstance(row.get("ram_used_mb_max"), (int, float))
            ]
        )
        gpu = numeric_stats(
            [
                row.get("gpu_memory_used_mb_total_max")
                for row in success_rows
                if isinstance(row.get("gpu_memory_used_mb_total_max"), (int, float))
            ]
        )
        validation_errors_after = numeric_stats(
            [
                row.get("validation_error_count_after")
                for row in success_rows
                if isinstance(row.get("validation_error_count_after"), (int, float))
            ]
        )
        fallback_count = sum(
            1
            for row in success_rows
            if row.get("correctness_conflict_fallback_applied")
        )

        summary_rows.append(
            {
                "model": model,
                "prompt_id": prompt_id,
                "runs": total,
                "successes": successes,
                "success_rate": round(successes / total, 6) if total else None,
                "wall_time_mean": wall["mean"],
                "wall_time_median": wall["median"],
                "wall_time_stdev": wall["stdev"],
                "wall_time_p95": wall["p95"],
                "ttft_mean": ttft["mean"],
                "ttft_median": ttft["median"],
                "ttft_stdev": ttft["stdev"],
                "ttft_p95": ttft["p95"],
                "tokens_per_second_mean": tps["mean"],
                "tokens_per_second_median": tps["median"],
                "tokens_per_second_stdev": tps["stdev"],
                "tokens_per_second_p95": tps["p95"],
                "ram_used_mb_max_mean": ram["mean"],
                "ram_used_mb_max_p95": ram["p95"],
                "gpu_memory_used_mb_total_max_mean": gpu["mean"],
                "gpu_memory_used_mb_total_max_p95": gpu["p95"],
                "validation_error_count_after_mean": validation_errors_after["mean"],
                "validation_error_count_after_p95": validation_errors_after["p95"],
                "correctness_conflict_fallback_count": fallback_count,
            }
        )
    return summary_rows


def write_partial_results(run_dir: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    summary_rows = summarize_results(rows)
    write_json(run_dir / "partial_results.json", rows)
    write_csv(run_dir / "partial_results.csv", rows)
    write_json(run_dir / "partial_summary.json", summary_rows)
    write_csv(run_dir / "partial_summary.csv", summary_rows)


def write_quality_template(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "run_id",
        "model",
        "prompt_id",
        "repetition",
        "response_text",
        "raw_response_text",
        "validation_errors_after",
        "correcao_conceitual_1_5",
        "clareza_1_5",
        "utilidade_pedagogica_1_5",
        "completude_1_5",
        "risco_alucinacao_1_5",
        "observacoes",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            if not row.get("success"):
                continue
            writer.writerow(
                {
                    "run_id": row.get("run_id"),
                    "model": row.get("model"),
                    "prompt_id": row.get("prompt_id"),
                    "repetition": row.get("repetition"),
                    "response_text": row.get("response_text"),
                    "raw_response_text": row.get("raw_response_text"),
                    "validation_errors_after": row.get("validation_errors_after"),
                }
            )


def write_report(path: Path, metadata: dict[str, Any], summary_rows: list[dict[str, Any]]) -> None:
    overall = [row for row in summary_rows if row["prompt_id"] == "__all__"]
    lines = [
        "# Relatório do benchmark Ollama",
        "",
        f"- Run ID: `{metadata['run_id']}`",
        f"- Data: `{metadata['created_at']}`",
        f"- Base URL Ollama: `{metadata['ollama_base_url']}`",
        f"- Repetições configuradas: `{metadata['repetitions']}`",
        "",
        "## Resumo por modelo",
        "",
        "| Modelo | Sucesso | Tempo médio (s) | P95 tempo (s) | TTFT médio (s) | Tokens/s médio | Erros validação |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in sorted(overall, key=lambda item: item["model"]):
        lines.append(
            "| {model} | {success_rate} | {wall_mean} | {wall_p95} | {ttft_mean} | {tps_mean} | {validation_errors} |".format(
                model=row["model"],
                success_rate=row.get("success_rate"),
                wall_mean=row.get("wall_time_mean"),
                wall_p95=row.get("wall_time_p95"),
                ttft_mean=row.get("ttft_mean"),
                tps_mean=row.get("tokens_per_second_mean"),
                validation_errors=row.get("validation_error_count_after_mean"),
            )
        )

    lines.extend(
        [
            "",
            "## Observações",
            "",
            "- Métricas de CPU, RAM e GPU podem aparecer como `null` quando a ferramenta local não estiver disponível.",
            "- A avaliação de qualidade deve ser preenchida manualmente em `quality_review_template.csv`.",
            "- Não compare resultados de dispositivos diferentes sem registrar o hardware usado.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def try_write_charts(run_dir: Path, summary_rows: list[dict[str, Any]]) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    overall = [row for row in summary_rows if row["prompt_id"] == "__all__"]
    if not overall:
        return

    charts_dir = run_dir / "charts"
    charts_dir.mkdir(exist_ok=True)

    chart_specs = [
        ("wall_time_mean", "Tempo médio de resposta (s)", "tempo_medio_resposta.png"),
        ("tokens_per_second_mean", "Tokens por segundo", "tokens_por_segundo.png"),
        ("ram_used_mb_max_mean", "Pico médio de RAM usada (MB)", "ram_usada.png"),
    ]
    labels = [row["model"] for row in overall]

    for key, title, filename in chart_specs:
        values = [row.get(key) for row in overall]
        if not any(isinstance(value, (int, float)) for value in values):
            continue

        numeric_values = [value if isinstance(value, (int, float)) else 0 for value in values]
        plt.figure(figsize=(max(8, len(labels) * 1.2), 4.8))
        plt.bar(labels, numeric_values)
        plt.title(title)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(charts_dir / filename)
        plt.close()


def hardware_metadata() -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "cpu_count": None,
        "ram_total_mb": None,
        "nvidia_gpus": get_nvidia_gpu_info(),
    }
    if psutil:
        metadata["cpu_count"] = psutil.cpu_count(logical=True)
        metadata["ram_total_mb"] = bytes_to_mb(psutil.virtual_memory().total)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa benchmark de modelos locais via API do Ollama."
    )
    parser.add_argument(
        "--config",
        default="benchmarks/ollama/config.example.json",
        help="Caminho para o arquivo JSON de configuração.",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        help="Sobrescreve a quantidade de repetições definida na configuração.",
    )
    parser.add_argument(
        "--model",
        action="append",
        help="Executa apenas o modelo informado. Pode ser usado mais de uma vez.",
    )
    parser.add_argument(
        "--prompt-id",
        action="append",
        help="Executa apenas o prompt informado. Pode ser usado mais de uma vez.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida configuração e disponibilidade dos modelos sem gerar respostas.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    config = load_json(config_path)

    base_url = config.get("ollama_base_url", "http://localhost:11434")
    timeout = int(config.get("timeout_seconds", 180))
    repetitions = args.repetitions or int(config.get("repetitions", 5))
    warmup_runs = int(config.get("warmup_runs", 0))
    keep_alive = config.get("keep_alive")
    global_options = config.get("generation_options") or {}
    resource_interval = float(config.get("resource_sampling_interval_seconds", 0.5))

    prompt_path = Path(config.get("prompt_file", "benchmarks/ollama/prompts.example.json"))
    prompts = read_prompts(prompt_path)
    models = configured_models(config)

    if args.model:
        selected = set(args.model)
        models = [model for model in models if model["name"] in selected]
    if args.prompt_id:
        selected_prompts = set(args.prompt_id)
        prompts = [prompt for prompt in prompts if prompt["id"] in selected_prompts]

    if not models:
        raise ValueError("Nenhum modelo selecionado para executar.")
    if not prompts:
        raise ValueError("Nenhum prompt selecionado para executar.")

    try:
        available_models = get_available_models(base_url, timeout)
    except requests.RequestException as exc:
        print(
            f"Não foi possível conectar ao Ollama em {base_url}: {compact_error(exc)}",
            file=sys.stderr,
        )
        print("Verifique se o serviço está em execução e tente novamente.", file=sys.stderr)
        return 1
    runnable_models = []
    missing_models = []
    for model in models:
        if model["name"] in available_models:
            runnable_models.append(model)
        else:
            missing_models.append(model["name"])

    print(f"Ollama: {base_url}")
    print(f"Prompts: {len(prompts)}")
    print(f"Modelos disponíveis para execução: {len(runnable_models)}")
    if missing_models:
        print("Modelos ausentes no Ollama local:")
        for model_name in missing_models:
            print(f"  - {model_name}")

    if args.dry_run:
        return 0 if runnable_models else 1
    if not runnable_models:
        print("Nenhum modelo configurado está disponível. Use `ollama list` para conferir.")
        return 1

    run_id = str(uuid.uuid4())
    output_dir = Path(config.get("output_dir", "benchmarks/ollama/results"))
    run_dir = output_dir / now_timestamp()
    run_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "config_path": str(config_path),
        "prompt_path": str(prompt_path),
        "ollama_base_url": base_url,
        "ollama_version": get_ollama_version(base_url, timeout),
        "repetitions": repetitions,
        "warmup_runs": warmup_runs,
        "generation_options": global_options,
        "keep_alive": keep_alive,
        "missing_models": missing_models,
        "hardware": hardware_metadata(),
    }
    write_json(run_dir / "metadata.json", metadata)
    write_json(run_dir / "built_prompts.json", prompts)

    rows = []
    first_prompt = prompts[0]
    total_tests = len(runnable_models) * len(prompts) * repetitions
    completed = 0

    for model in runnable_models:
        if warmup_runs > 0:
            print(f"Aquecendo {model['name']} ({warmup_runs}x)...")
            warmup_errors = run_warmups(
                base_url=base_url,
                model=model,
                prompt=first_prompt,
                global_options=global_options,
                keep_alive=keep_alive,
                timeout=timeout,
                warmup_runs=warmup_runs,
            )
            if warmup_errors:
                print(f"  Aquecimento com erro: {warmup_errors[-1]}")

        for prompt in prompts:
            for repetition in range(1, repetitions + 1):
                completed += 1
                print(
                    f"[{completed}/{total_tests}] {model['name']} | "
                    f"{prompt['id']} | repetição {repetition}"
                )
                row = run_single_test(
                    run_id=run_id,
                    base_url=base_url,
                    model=model,
                    model_metadata=available_models.get(model["name"], {}),
                    prompt=prompt,
                    repetition=repetition,
                    global_options=global_options,
                    keep_alive=keep_alive,
                    timeout=timeout,
                    resource_interval=resource_interval,
                )
                rows.append(row)
                write_partial_results(run_dir, rows)
                if not row["success"]:
                    print(f"  Erro: {row['error']}")

    summary_rows = summarize_results(rows)

    write_json(run_dir / "raw_results.json", rows)
    write_csv(run_dir / "raw_results.csv", rows)
    write_json(run_dir / "summary.json", summary_rows)
    write_csv(run_dir / "summary.csv", summary_rows)
    write_quality_template(run_dir / "quality_review_template.csv", rows)
    write_report(run_dir / "report.md", metadata, summary_rows)
    try_write_charts(run_dir, summary_rows)

    print(f"Resultados salvos em: {run_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.", file=sys.stderr)
        raise SystemExit(130)
