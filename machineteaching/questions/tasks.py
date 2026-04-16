import os
import sys
import json
import threading
from pathlib import Path

from django.conf import settings
from django.db import close_old_connections

from .models import (
    SolutionGroup,
    IgnoredSolution,
    Problem,
    OnlineClass
)

# ===============================
# PATHS
# ===============================

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root_dir, 'overcode_core'))
sys.path.append(os.path.join(root_dir, 'scripts'))

from .scripts.get_function_name import get_function_name
from .overcode_core.run_pipeline import run_pipeline
from .scripts.replace_output_data import replace_output_data
from .scripts.get_problem_data import get_problem_data

# ==========================================================
# GERA CÓDIGO REPRESENTATIVO DOS GRUPOS
# ==========================================================

def gerar_codigo_representativo(caminho_output):

    caminho_output = Path(caminho_output)

    with open(caminho_output / "phrases.json", encoding="utf-8") as f:
        phrases = json.load(f)

    with open(caminho_output / "solutions.json", encoding="utf-8") as f:
        solutions = json.load(f)

    phrases_by_id = {p["id"]: p["code"] for p in phrases}

    grupos_codigo = {}

    for cluster in solutions:

        linhas = []

        for line in cluster["lines"]:
            indent = " " * line["indent"]
            phrase = phrases_by_id[line["phraseID"]]
            linhas.append(f"{indent}{phrase}")

        grupos_codigo[cluster["id"]] = {
            "code": "\n".join(linhas),
            "correct": cluster["correct"],
            "members": cluster["members"],
            "count": cluster["count"],
        }

    return grupos_codigo


# ==========================================================
# PROCESSAMENTO OVERCODE
# ==========================================================

def iniciar_processamento_overcode(turma_id, problem_id, interface=True):

    def processar():

        close_old_connections()

        print(f"[Overcode] Iniciando processamento para turma {turma_id}, problema {problem_id}")

        # ===============================
        # DIRETÓRIOS
        # ===============================

        statics_dir = os.path.join(settings.BASE_DIR, 'questions', 'statics')
        problems_dir = os.path.join(statics_dir, "problems_data")
        problem_dir = os.path.join(problems_dir, f"turma_{turma_id}_problem_{problem_id}")
        data_dir = os.path.join(problem_dir, "data")
        output_dir = os.path.join(problem_dir, "output")

        # ===============================
        # PIPELINE
        # ===============================

        if not os.path.exists(output_dir):

            if not os.path.exists(data_dir):
                get_problem_data(turma_id, problem_id, problem_dir)

            funcname = get_function_name(os.path.join(data_dir, "answer.py"))
            run_pipeline(problem_dir, funcname)

        problem = Problem.objects.get(id=problem_id)
        turma = OnlineClass.objects.get(id=turma_id)

        # ===============================
        # IMPORTAÇÃO DOS GRUPOS
        # ===============================

        solutions_json_path = os.path.join(output_dir, "solutions.json")

        processed_ids = set()

        grupos_codigo = gerar_codigo_representativo(output_dir)

        if os.path.exists(solutions_json_path):

            with open(solutions_json_path, "r", encoding="utf-8") as f:
                solutions_data = json.load(f)

            for group in solutions_data:

                codigo_representativo = grupos_codigo[group["id"]]["code"]

                SolutionGroup.objects.update_or_create(
                    problem=problem,
                    turma=turma,
                    group_index=group["id"],
                    defaults={
                        "correct": group["correct"],
                        "members": group["members"],
                        "count": group["count"],
                        "representative_code": codigo_representativo,
                    }
                )

                for member in group.get("members", []):
                    processed_ids.add(str(member))

        # ===============================
        # SOLUÇÕES PROCESSADAS PELO OVERCODE
        # ===============================

        all_solution_ids = set()

        if os.path.exists(data_dir):

            for filename in os.listdir(data_dir):

                if not filename.endswith(".py"):
                    continue

                if filename == "answer.py":
                    continue

                user_id = os.path.splitext(filename)[0]

                all_solution_ids.add(user_id)

        # ===============================
        # SOLUÇÕES IGNORADAS
        # ===============================

        missing_ids = all_solution_ids - processed_ids

        # limpa ignoradas antigas
        IgnoredSolution.objects.filter(problem_id=problem.id).delete()

        for solution_id in missing_ids:

            IgnoredSolution.objects.create(
                problem_id=problem.id,
                solution_id=solution_id,
                reason="Ignorada pelo Overcode (não entrou em nenhum grupo)"
            )

        print("[Overcode] TOTAL PROCESSADAS:", len(all_solution_ids))
        print("[Overcode] EM GRUPOS:", len(processed_ids))
        print("[Overcode] LISTA EM GRUPOS:", processed_ids)
        print("[Overcode] IGNORADAS:", len(missing_ids))
        print("[Overcode] LISTA IGNORADAS:", missing_ids)

        # ===============================
        # INTERFACE
        # ===============================

        if interface:

            interface_output_dir = os.path.join(problems_dir, "output")

            replace_output_data(
                problem_id,
                output_dir,
                interface_output_dir
            )

        print(f"[Overcode] Processamento concluído para turma {turma_id}, problema {problem_id}.")

    threading.Thread(target=processar).start()
