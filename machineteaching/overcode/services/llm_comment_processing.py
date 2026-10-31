import ast
import re
import unicodedata
from typing import Optional


EMPTY_COMMENT_MESSAGE = "Sem resposta da IA."
NO_STRENGTHS_BULLET = (
    "- Não foi possível destacar um acerto específico com segurança."
)
DEFAULT_IMPROVEMENT_TEXT = (
    "Não foram identificados problemas lógicos relevantes na solução."
)
DEFAULT_IMPROVEMENT_BULLET = f"- {DEFAULT_IMPROVEMENT_TEXT}"
FAILED_IMPROVEMENT_TEXT = (
    "As verificações automáticas indicam que a solução ainda não passou. "
    "Vale comparar o resultado produzido com o esperado no enunciado e "
    "localizar em qual parte do raciocínio essa diferença aparece."
)
FAILED_IMPROVEMENT_BULLET = f"- {FAILED_IMPROVEMENT_TEXT}"
SKIPPED_IMPROVEMENT_TEXT = (
    "A submissão foi marcada como pulada. Vale conferir se há código suficiente "
    "para avaliar a estratégia antes de usar um comentário automático."
)
SKIPPED_IMPROVEMENT_BULLET = f"- {SKIPPED_IMPROVEMENT_TEXT}"
INSUFFICIENT_CODE_MESSAGE = (
    "Não foi possível gerar comentário: o código disponível está vazio, "
    "incompleto ou contém apenas o modelo inicial da resposta."
)
MIN_MEANINGFUL_CODE_CHARS = 8
NON_PASSING_GRADING_STATUSES = ("failed", "skipped")

PLACEHOLDER_CODE_PATTERNS = (
    r"\bstart your python function here\b",
    r"\bcoloque um coment[aá]rio dizendo o que a fun[cç][aã]o faz\b",
    r"\bescolha nomes elucidativos para suas vari[aá]veis\b",
)

INCOMPLETE_CODE_PATTERNS = (
    r"^(?:def|return|pass|none|\.\.\.)$",
)

BLOCKED_NAMING_PATTERNS = (
    r"\b(?:nome|identificador|vari[aá]ve(?:l|is)|par[aâ]metros?|fun[cç][aã]o).{0,70}\b(?:claro|clara|descritivo|adequado|confus\w*|represent\w*|portugu[eê]s|ingl[eê]s)\b",
    r"\b(?:claro|clara|descritivo|adequado|confus\w*|represent\w*|portugu[eê]s|ingl[eê]s).{0,70}\b(?:nome|identificador|vari[aá]ve(?:l|is)|par[aâ]metros?|fun[cç][aã]o)\b",
    r"\bnome (?:da|do) fun[cç][aã]o\b",
    r"\bfun[cç][aã]o.{0,60}\bnome\b",
    r"\bfun[cç][aã]o.{0,60}\brenome",
    r"\brenome.{0,60}\bfun[cç][aã]o\b",
    r"\brenome(?:ar|ie|a[cç][aã]o)\b",
    r"\bingl[eê]s\b",
)

BLOCKED_STYLE_PATTERNS = (
    r"\bdocstring\b",
    r"\b(?:adicione|crie|escreva|implemente).{0,50}\btest\w*\b",
    r"\btestes? unit[aá]rios?\b",
    r"\bunit tests?\b",
    r"\bdocumenta[cç][aã]o\b",
)

INDENTATION_COMPARISON_PATTERNS = (
    r"\btabs?.{0,50}\bespa[cç]os?\b",
    r"\bespa[cç]os?.{0,50}\btabs?\b",
)

INDENTATION_ISSUE_WORDS = (
    "incorret",
    "erro",
    "problema",
    "falha",
    "quebra",
    "desalinh",
    "fora",
    "afeta",
    "prejudic",
    "dificult",
    "execu",
)

MISSING_COMMENTS_PATTERNS = (
    r"\b(?:falt|aus[eê]ncia|sem|n[aã]o h[aá]|n[aã]o possui|n[aã]o tem).{0,60}\bcoment[aá]rios?\b",
    r"\bcoment[aá]rios?.{0,60}\b(?:falt|ausent|necess[aá]ri|deveria)\b",
)

CODE_EXAMPLE_PATTERNS = (
    r"\b(?:def|return|print|elif|else|for|while)\b",
    r"(?:==|!=|<=|>=|//|\+=|-=|\*=|/=)",
    r"\boperador\s*[+\-*/%]\b",
    r"(?<!\w)\+(?!\w)",
)

LOW_VALUE_OPTIMIZATION_PATTERNS = (
    r"\b(?:eficiente|efici[eê]ncia|otimiza[cç][aã]o|otimizar)\b",
    r"\bn[aã]o [eé] (?:a )?mais eficiente\b",
    r"\bjoin[aá]?(?:-?l[oa]s?)?\b",
)

JARGON_OR_BROKEN_LANGUAGE_PATTERNS = (
    r"\bbuilt-?in\b",
    r"\bslicing\b",
    r"\ba conta usada\b",
    r"\b(?:na|da|pela|essa|uma) texto\b",
)

PASSED_SPECULATIVE_IMPROVEMENT_PATTERNS = (
    r"\bpode(?:ria)?\b.{0,90}\b(?:dar|gerar|causar|retornar|produzir|ficar|falhar|quebrar|errar|descartar|perder|n[aã]o funcionar|n[aã]o atender|n[aã]o passar|negativ\w*|zero|incorret\w*|problem\w*)\b",
    r"\b(?:talvez|nem sempre|dependendo|eventualmente|em alguns casos|casos? especiais?|casos? limites?)\b",
    r"\b(?:entrada|valor|resultado|n[uú]mero|divis[aã]o|c[aá]lculo|opera[cç][aã]o|condi[cç][aã]o).{0,90}\b(?:negativ\w*|zero|limite|especial|inesperad\w*|inv[aá]lid\w*)\b",
    r"\b(?:cuidado|aten[cç][aã]o).{0,80}\b(?:caso|entrada|valor|resultado|divis[aã]o|c[aá]lculo|opera[cç][aã]o)\b",
    r"\bn[aã]o\b.{0,80}\b(?:garante|funciona|passa|atende|resolve)\b",
    r"\b(?:seria interessante|seria bom|vale).{0,80}\b(?:testar|tratar|validar|garantir|considerar)\b",
    r"\b(?:em vez disso|voc[eê] pode|um pr[oó]ximo passo|vale observar|vale pensar)\b",
)

RESIDUAL_CODE_PATTERNS = (
    r"(?:==|!=|<=|>=|//|\+=|-=|\*=|/=)",
    r"\b[A-Za-z_][A-Za-z0-9_]*\s*(?:\[[^\]]+\]|\([^)]*\))",
    r"(?<!\w)\+(?!\w)",
)

PROMPT_MARKER_PATTERNS = (
    r"^<{2,}.*>{2,}$",
    r"\b(?:in[ií]cio|fim).{0,50}resposta(?: corrigida| inv[aá]lida)?\b",
)

DROP_BULLET_PATTERNS = (
    r"\b(?:docstring|unit tests?|documenta[cç][aã]o)\b",
    r"\b(?:adicione|crie|escreva|implemente).{0,50}\btest\w*\b",
    r"\b(?:adicione|crie|escreva|implemente|inclua|prepare|fa[cç]a|vale|poderia|seria bom).{0,80}\b(?:test\w*|casos? de teste)\b",
    r"\b(?:reescreva|refa[cç]a|troque|substitua|use|usar|utilize|utilizar|adote|prefira|vale).{0,80}\b(?:for|while|la[cç]o|compreens[aã]o|fun[cç][aã]o pronta|biblioteca)\b",
    r"\b(?:for|while|la[cç]o|compreens[aã]o de lista|fun[cç][aã]o pronta|biblioteca).{0,80}\b(?:mais simples|mais claro|mais eficiente|melhor|otimizad[ao])\b",
    r"\b(?:otimiz|eficient|concis).{0,80}\b(?:for|while|la[cç]o|compreens[aã]o|fun[cç][aã]o pronta|biblioteca)\b",
    r"\bcondi[cç][aã]o.{0,80}\b(?:pode|poderia|deve|deveria|vale).{0,40}\bsimplificad[ao]\b",
    r"\b(?:adicione|crie|implemente|inclua|fa[cç]a|vale|poderia|seria bom|importante).{0,80}\b(?:validar|valida[cç][aã]o|entrada inv[aá]lida|tratamento de exce[cç][oõ]es?|exce[cç][aã]o|try|except)\b",
    r"\b(?:validar|valida[cç][aã]o|entrada inv[aá]lida|tratamento de exce[cç][oõ]es?|exce[cç][aã]o|try|except).{0,80}\b(?:seria bom|importante|necess[aá]rio|melhor|mais seguro)\b",
)

GENERIC_PATTERNS = (
    r"\b(?:pense melhor|preste mais aten[cç][aã]o|continue praticando|mais tradicional)\b",
    r"\b(?:revise|reveja|verifique).{0,50}\b(?:l[oó]gica|correto|c[oó]digo)\b",
    r"\bverifique.{0,30}\bresultado\b",
    r"\bcompare.{0,30}\benunciado\b",
    r"\bsua l[oó]gica est[aá] errad[ao]\b",
    r"\b(?:tente melhorar|pode ser melhorad[oa])\b",
)

UNSUPPORTED_CORRECTNESS_PATTERNS = (
    r"\b(?:l[oó]gica|solu[cç][aã]o|c[oó]digo).{0,40}\bcorret[ao]\b",
    r"\b(?:implementou|resolve).{0,40}\bcorretamente\b",
)

OVERALL_CORRECTNESS_CLAIM_PATTERNS = (
    r"\bsolu[cç][aã]o.{0,80}\b(?:est[aá]|parece|foi|ficou|segue|continua).{0,30}\bcorret",
    r"\bcorret[ao].{0,80}\b(?:em termos de|estrutura|objetivo|l[oó]gica|solu[cç][aã]o|c[oó]digo)\b",
    r"\b(?:resolveu?|atendeu|cumpriu).{0,50}\b(?:exerc[ií]cio|objetivo|proposta|enunciado)\b",
    r"\b(?:implementou|resolve).{0,40}\bcorretamente\b",
)


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    normalized = " ".join(text.casefold().split())
    return any(re.search(pattern, normalized) for pattern in patterns)


def _plain_text(text: str) -> str:
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFD", text.casefold())
        if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"\s+", " ", without_accents).strip()


def _is_empty_ast_statement(statement: ast.AST) -> bool:
    if isinstance(statement, ast.Pass):
        return True
    if (
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Constant)
        and isinstance(statement.value.value, str)
    ):
        return True
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return all(_is_empty_ast_statement(child) for child in statement.body)
    return False


def _has_executable_code(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return True

    return any(not _is_empty_ast_statement(statement) for statement in tree.body)


def invalid_code_reason(code: Optional[str]) -> Optional[str]:
    if not isinstance(code, str):
        return INSUFFICIENT_CODE_MESSAGE

    normalized_code = code.replace("\xa0", " ").strip()
    if not normalized_code:
        return INSUFFICIENT_CODE_MESSAGE

    visible_code_lines = [
        line
        for line in normalized_code.splitlines()
        if line.strip()
    ]
    non_comment_code_lines = [
        line
        for line in visible_code_lines
        if not line.lstrip().startswith("#")
    ]
    meaningful_code = "\n".join(non_comment_code_lines).strip()
    plain_code = _plain_text(meaningful_code)

    if not meaningful_code:
        return INSUFFICIENT_CODE_MESSAGE
    if (
        _contains_any(meaningful_code, PLACEHOLDER_CODE_PATTERNS)
        and not _has_executable_code(meaningful_code)
    ):
        return INSUFFICIENT_CODE_MESSAGE
    if len(plain_code) < MIN_MEANINGFUL_CODE_CHARS:
        return INSUFFICIENT_CODE_MESSAGE
    if _contains_any(plain_code, INCOMPLETE_CODE_PATTERNS):
        return INSUFFICIENT_CODE_MESSAGE
    if not _has_executable_code(meaningful_code):
        return INSUFFICIENT_CODE_MESSAGE

    return None


def grading_status_from_evidence(correction_evidence: Optional[str]) -> Optional[str]:
    if not correction_evidence:
        return None

    text = _plain_text(correction_evidence)
    if "nao passou" in text or "failed" in text or "falhou" in text:
        return "failed"
    if "foi pulada" in text or "skipped" in text:
        return "skipped"
    if "passou" in text or "passed" in text:
        return "passed"

    return None


def _normalize_bullet(line: str) -> str:
    stripped = line.strip()
    if re.match(r"^[-*•]\s+", stripped):
        return "- " + re.sub(r"^[-*•]\s+", "", stripped).strip()
    if re.match(r"^\d+[\.)]\s+", stripped):
        return "- " + re.sub(r"^\d+[\.)]\s+", "", stripped).strip()
    return stripped


def _is_default_improvement_bullet(bullet: str) -> bool:
    text = _plain_text(_normalize_bullet(bullet).removeprefix("- "))
    return bool(
        re.search(
            r"\bnao foram identificados\b.{0,40}\bproblemas\b.{0,40}\b"
            r"(?:logicos|logica|relevantes)\b",
            text,
        )
    )


def _is_prompt_marker_line(text: str) -> bool:
    return _contains_any(text.strip(), PROMPT_MARKER_PATTERNS)


def _normalize_heading(line: str) -> Optional[str]:
    normalized = line.strip().strip("*:# ").casefold()
    if normalized == "pontos fortes":
        return "### Pontos fortes"
    if normalized in ("melhorias", "pontos de melhoria"):
        return "### Melhorias"
    return None


def _normalize_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:markdown|md)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    sections: dict[str, list[str]] = {"Pontos fortes": [], "Melhorias": []}
    current_section: Optional[str] = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _is_prompt_marker_line(line):
            continue

        heading = _normalize_heading(line)
        if heading:
            current_section = heading.replace("### ", "")
            continue

        if current_section is None:
            continue

        normalized_bullet = _normalize_bullet(line)
        if normalized_bullet.startswith("- "):
            sections[current_section].append(normalized_bullet)
            continue

        sections[current_section].append("- " + normalized_bullet)

    output: list[str] = []
    for section in ("Pontos fortes", "Melhorias"):
        bullets = [bullet for bullet in sections[section] if bullet.strip() != "-"]
        if section == "Melhorias" and len(bullets) > 1:
            bullets = [
                bullet
                for bullet in bullets
                if not _is_default_improvement_bullet(bullet)
            ]
        if not bullets:
            continue
        if output:
            output.append("")
        output.append(f"### {section}")
        output.extend(bullets)

    return "\n".join(output).strip() or text


def _soften_direct_commands(text: str) -> str:
    replacements = (
        (
            r"\b[Ee]m vez disso,\s+voc[eê] pode usar\b",
            "Um próximo passo é observar",
        ),
        (r"\b[Ee]m Python,\s+voc[eê] pode usar\b", "Uma pista é observar"),
        (r"\b[Vv]oc[eê] pode considerar usar\b", "Vale pensar em"),
        (r"\b[Vv]oc[eê] pode simplesmente\b", "Um caminho mais simples pode ser"),
        (r"\b[Vv]oc[eê] pode usar\b", "Vale observar"),
        (r"\b[Vv]oc[eê] pode\b", "Vale"),
        (r"\b[Vv]oc[eê] deve\b", "Vale"),
        (r"\b[Cc]onsidere usar\b", "Vale pensar em"),
        (r"\b[Cc]onsidere\b", "Vale pensar em"),
        (
            r"^(?:[Uu]se|[Tt]roque|[Cc]orrija|[Aa]dicione|[Rr]emova|[Ii]mplemente|[Ff]a[cç]a)\b",
            "Vale revisar",
        ),
    )

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)

    return text


def _replace_code_snippets(text: str) -> str:
    replacements = (
        (r"\blen\s*/\s*2\b", "metade do tamanho"),
        (
            r"\b(?:m[eé]todo|fun[cç][aã]o)\s+built-?in\s+len\s*\([^)]*\)",
            "a contagem de caracteres",
        ),
        (
            r"\b(?:m[eé]todo|fun[cç][aã]o)\s+built-?in\s+a conta usada\b",
            "a contagem de caracteres",
        ),
        (r"\blen\s*\([^)]*\)", "a contagem de caracteres"),
        (r"\b(?:m[eé]todo|fun[cç][aã]o)\s+built-?in\b", "recurso da linguagem"),
        (r"\b[A-Za-z_][A-Za-z0-9_]*\[[^\]]+\]", "uma parte do texto"),
        (r"\b[A-Za-z_][A-Za-z0-9_]*\([^)]*\)", "esse cálculo"),
        (r"\bjoin[aá]?(?:-?l[oa]s?)?\b", "juntar as partes"),
        (r"\breturn\b", "retorno"),
        (r"\bprint\b", "exibição"),
    )

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def _polish_portuguese(text: str) -> str:
    replacements = (
        (r"^[Ee]m vez disso,\s+[Vv]ale observar\b", "Um próximo passo é observar"),
        (r"(?<=[,;:])\s+Vale\b", " vale"),
        (r"\bna texto\b", "no texto"),
        (r"\bda texto\b", "do texto"),
        (r"\bpela texto\b", "pelo texto"),
        (r"\bessa texto\b", "esse texto"),
        (r"\buma texto\b", "um texto"),
        (r"\bo a contagem\b", "a contagem"),
        (r"\ba a contagem\b", "a contagem"),
        (
            r"\ba contagem de caracteres para obter a quantidade de caracteres\b",
            "a contagem de caracteres",
        ),
        (r"\ba quantidade de caracteres na texto\b", "a quantidade de caracteres no texto"),
        (r"\ba contagem de caracteres na texto\b", "a contagem de caracteres no texto"),
        (r"\bm[eé]todo\s+(?:built-?in\s+)?a contagem de caracteres\b", "contagem de caracteres"),
        (r"\bfun[cç][aã]o\s+(?:built-?in\s+)?a contagem de caracteres\b", "contagem de caracteres"),
        (r"\bbuilt-?in\b", "da linguagem"),
        (r"\bretorno\b", "resultado final"),
    )

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text.strip()


def _sanitize_bullet(
    bullet: str,
    *,
    grading_status: Optional[str] = None,
    current_section: Optional[str] = None,
) -> Optional[str]:
    bullet = re.sub(r"`([^`]+)`", r"\1", bullet)
    bullet = re.sub(
        r"<{2,}[^<>]*(?:in[ií]cio|fim)[^<>]*>{2,}",
        "",
        bullet,
        flags=re.IGNORECASE,
    ).strip()
    if _is_prompt_marker_line(bullet):
        return None
    if grading_status == "failed" and _is_default_improvement_bullet(bullet):
        return FAILED_IMPROVEMENT_TEXT
    if (
        grading_status in NON_PASSING_GRADING_STATUSES
        and _contains_any(bullet, OVERALL_CORRECTNESS_CLAIM_PATTERNS)
    ):
        return None
    if (
        grading_status == "passed"
        and current_section == "### Melhorias"
        and _contains_any(bullet, PASSED_SPECULATIVE_IMPROVEMENT_PATTERNS)
    ):
        return None
    if _contains_any(bullet, LOW_VALUE_OPTIMIZATION_PATTERNS):
        return None

    operator_match = re.search(
        r"\buso do operador\s*([+\-*/%])(?!\w)",
        bullet,
        flags=re.IGNORECASE,
    )
    if operator_match:
        operation_name = {
            "+": "soma",
            "-": "subtração",
            "*": "multiplicação",
            "/": "divisão",
            "%": "resto da divisão",
        }[operator_match.group(1)]
        return f"A escolha da operação de {operation_name} está alinhada ao objetivo do exercício."

    if _contains_any(bullet, BLOCKED_NAMING_PATTERNS):
        return None

    bullet = _soften_direct_commands(bullet)
    bullet = _replace_code_snippets(bullet)
    bullet = re.sub(
        r"\b[Aa] função\s+[A-Za-z_][A-Za-z0-9_]*\b",
        "A solução",
        bullet,
    )
    bullet = re.sub(
        r"\b[Oo] uso da vari[aá]vel\s+[A-Za-z_][A-Za-z0-9_]*\b",
        "Guardar esse valor separado",
        bullet,
    )
    bullet = re.sub(
        r"\b[Aa] vari[aá]vel\s+[A-Za-z_][A-Za-z0-9_]*\b",
        "Esse passo intermediário",
        bullet,
    )
    bullet = re.sub(
        r"\b[Oo] parâmetro\s+[A-Za-z_][A-Za-z0-9_]*\b",
        "A informação recebida",
        bullet,
    )
    bullet = re.sub(r"\boperador\s*[+\-*/%]\b", "operação", bullet)
    bullet = bullet.replace("operação de soma é correto", "operação de soma é correta")
    bullet = bullet.replace("operação é correto", "operação é correta")
    bullet = bullet.replace(
        "Esse passo intermediário não é necessária",
        "Esse passo intermediário não parece necessário",
    )
    bullet = bullet.replace(
        "Esse passo intermediário não é necessário",
        "Esse passo intermediário pode não ser necessário",
    )
    bullet = bullet.replace("concatenar as strings", "juntar as partes do texto")
    bullet = bullet.replace("concatenação de strings", "junção das partes do texto")
    bullet = re.sub(r"\bstrings\b", "textos", bullet, flags=re.IGNORECASE)
    bullet = re.sub(r"\bstring\b", "texto", bullet, flags=re.IGNORECASE)
    bullet = bullet.replace("; Um caminho", ". Um caminho")
    bullet = bullet.replace("na função retorno", "no retorno")
    bullet = bullet.replace("função retorno", "retorno")
    bullet = re.sub(r"\s+", " ", bullet).strip()
    bullet = _polish_portuguese(bullet)
    bullet = re.sub(r"\s+", " ", bullet).strip()

    if (
        not bullet
        or _contains_any(bullet, DROP_BULLET_PATTERNS)
        or _contains_any(bullet, JARGON_OR_BROKEN_LANGUAGE_PATTERNS)
        or _contains_any(bullet, GENERIC_PATTERNS)
        or _contains_any(bullet, RESIDUAL_CODE_PATTERNS)
    ):
        return None
    return bullet


def _sanitize_response(
    text: str,
    *,
    grading_status: Optional[str] = None,
) -> str:
    output: list[str] = []
    current_section: Optional[str] = None
    saw_supported_section = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading = _normalize_heading(line)
        if heading:
            current_section = heading
            saw_supported_section = True
            continue

        if current_section is None:
            continue

        bullet = _normalize_bullet(line)
        if not bullet.startswith("- "):
            continue

        sanitized = _sanitize_bullet(
            bullet[2:],
            grading_status=grading_status,
            current_section=current_section,
        )
        if sanitized is None:
            continue

        if not output or output[-1] != current_section:
            if output:
                output.append("")
            output.append(current_section)
        output.append("- " + sanitized)

    sanitized_text = "\n".join(output).strip()
    if sanitized_text or saw_supported_section:
        return sanitized_text

    return text


def _has_section(text: str, section: str) -> bool:
    return bool(re.search(rf"^### {section}$", text, flags=re.MULTILINE))


def _ensure_default_improvement(
    text: str,
    *,
    grading_status: Optional[str] = None,
    ensure_default: bool = True,
) -> str:
    if not ensure_default:
        return text

    if grading_status == "failed" and not _has_section(text, "Melhorias"):
        if text.strip():
            return (
                f"{text.rstrip()}\n\n"
                "### Melhorias\n"
                f"{FAILED_IMPROVEMENT_BULLET}"
            )
        return f"### Melhorias\n{FAILED_IMPROVEMENT_BULLET}"

    if grading_status == "skipped" and not _has_section(text, "Melhorias"):
        if text.strip():
            return (
                f"{text.rstrip()}\n\n"
                "### Melhorias\n"
                f"{SKIPPED_IMPROVEMENT_BULLET}"
            )
        return f"### Melhorias\n{SKIPPED_IMPROVEMENT_BULLET}"

    if grading_status == "passed" and not _has_section(text, "Melhorias"):
        if text.strip():
            return (
                f"{text.rstrip()}\n\n"
                "### Melhorias\n"
                f"{DEFAULT_IMPROVEMENT_BULLET}"
            )
        return f"### Melhorias\n{DEFAULT_IMPROVEMENT_BULLET}"

    if _has_section(text, "Pontos fortes") and not _has_section(text, "Melhorias"):
        return (
            f"{text.rstrip()}\n\n"
            "### Melhorias\n"
            f"{DEFAULT_IMPROVEMENT_BULLET}"
        )
    return text


def _ensure_strengths_section(text: str) -> str:
    if _has_section(text, "Melhorias") and not _has_section(text, "Pontos fortes"):
        return f"### Pontos fortes\n{NO_STRENGTHS_BULLET}\n\n{text}"
    return text


def prepare_response(
    text: str,
    *,
    grading_status: Optional[str] = None,
    ensure_default: bool = True,
) -> str:
    prepared = _ensure_default_improvement(
        _normalize_response(
            _sanitize_response(
                text,
                grading_status=grading_status,
            )
        ),
        grading_status=grading_status,
        ensure_default=ensure_default,
    )
    return _ensure_strengths_section(prepared) if ensure_default else prepared


def correctness_conflict_fallback(grading_status: Optional[str]) -> str:
    if grading_status == "skipped":
        return _ensure_strengths_section(f"### Melhorias\n{SKIPPED_IMPROVEMENT_BULLET}")
    return _ensure_strengths_section(f"### Melhorias\n{FAILED_IMPROVEMENT_BULLET}")


def has_correctness_conflict(
    errors: list[str],
    *,
    grading_status: Optional[str] = None,
) -> bool:
    if grading_status not in NON_PASSING_GRADING_STATUSES:
        return False
    return any("afirma correção geral" in error for error in errors)


def _format_errors(text: str) -> list[str]:
    if not text.strip():
        return ["A resposta está vazia."]

    errors: list[str] = []
    allowed_heading_pattern = r"^### (Pontos fortes|Melhorias)$"

    if not re.search(allowed_heading_pattern, text, flags=re.MULTILINE):
        errors.append("A resposta não contém uma seção permitida.")
    if not re.search(r"^- .+", text, flags=re.MULTILINE):
        errors.append("A resposta não contém bullets válidos.")
    if re.search(r"^### (?!Pontos fortes$|Melhorias$).+", text, flags=re.MULTILINE):
        errors.append("A resposta usa títulos fora do formato permitido.")
    if "`" in text:
        errors.append("A resposta contém crases ou bloco de código.")

    return errors


def _mentions_indentation(text: str) -> bool:
    return bool(re.search(r"\bindenta[cç][aã]o\b", text.casefold()))


def _indentation_has_issue_context(text: str) -> bool:
    for line in text.casefold().splitlines():
        if re.search(r"\bindenta[cç][aã]o\b", line):
            return any(word in line for word in INDENTATION_ISSUE_WORDS)
    return False


def validation_errors(
    text: str,
    *,
    has_statement: bool,
    has_grading_context: bool = False,
    grading_status: Optional[str] = None,
    mode: Optional[str] = None,
) -> list[str]:
    errors = _format_errors(text)

    if _contains_any(text, BLOCKED_NAMING_PATTERNS):
        errors.append("A resposta comenta nomes, idioma dos nomes ou renomeação.")
    if _contains_any(text, BLOCKED_STYLE_PATTERNS):
        errors.append("A resposta comenta testes unitários, docstrings ou documentação.")
    if _contains_any(text, INDENTATION_COMPARISON_PATTERNS):
        errors.append("A resposta compara tabs com espaços.")
    if _mentions_indentation(text) and not _indentation_has_issue_context(text):
        errors.append("A resposta comenta indentação sem indicar problema concreto.")
    if mode == "group" and _contains_any(text, MISSING_COMMENTS_PATTERNS):
        errors.append("A resposta comenta ausência de comentários para um grupo.")
    if _contains_any(text, CODE_EXAMPLE_PATTERNS):
        errors.append("A resposta contém trecho, símbolo ou exemplo de código.")
    if _contains_any(text, JARGON_OR_BROKEN_LANGUAGE_PATTERNS):
        errors.append("A resposta contém jargão ou português quebrado.")
    if _contains_any(text, GENERIC_PATTERNS):
        errors.append("A resposta contém orientação genérica.")
    if (
        grading_status in NON_PASSING_GRADING_STATUSES
        and _contains_any(text, OVERALL_CORRECTNESS_CLAIM_PATTERNS)
    ):
        errors.append("A resposta afirma correção geral apesar de reprovação ou submissão pulada.")
    if (
        grading_status == "passed"
        and _contains_any(text, PASSED_SPECULATIVE_IMPROVEMENT_PATTERNS)
    ):
        errors.append("A resposta sugere melhoria especulativa apesar de aprovação.")
    if (
        not has_statement
        and not has_grading_context
        and _contains_any(text, UNSUPPORTED_CORRECTNESS_PATTERNS)
    ):
        errors.append("A resposta afirma correção sem acesso ao enunciado.")

    return errors
