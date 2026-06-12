import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def _generate_comment(prompt: str) -> str:
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            return f"Resposta inválida do modelo: {data}"

        return data["response"].strip()

    except Exception as e:
        return f"Erro ao gerar comentário: {str(e)}"


def _markdown_rules() -> str:
    return """
Responda em Markdown simples.
Use no máximo estes títulos:

### Pontos fortes
### Melhorias

Use listas com bullets curtos.
Não use bloco de código.
Não escreva uma solução completa.
Não inclua saudações, introduções ou conclusão genérica.
"""


def generate_group_comment(code: str) -> str:
    prompt = f"""
Você é professor de um curso de introdução à lógica de programação.
Você está analisando um código representativo de um grupo de soluções de alunos.

Avalie:
- legibilidade, incluindo indentação e nomes de variáveis/funções;
- estruturação da solução, incluindo uso de funções, parâmetros e return;
- corretude provável do código, considerando casos dentro do contexto de exercícios simples de Python.

Considere que os alunos não falam inglês e que a proposta é ensinar operações simples de lógica em Python.
Não recomende traduzir nomes de funções fornecidos pelo exercício.
Não recomende docstrings.
Faça recomendações objetivas e úteis para o professor comentar o grupo.
Se não houver informação suficiente para afirmar algo, diga isso de forma direta.

{_markdown_rules()}

Código:
{code}

Resposta:
"""

    return _generate_comment(prompt)


def generate_student_comment(code: str, ignored: bool = False) -> str:
    context = (
        "Esta solução foi ignorada pelo agrupamento do OverCode, então analise-a individualmente "
        "sem presumir que ela segue o padrão dos grupos."
        if ignored
        else "Esta solução pertence a um grupo do OverCode, mas o comentário deve ser individual."
    )

    prompt = f"""
Você é professor de um curso de introdução à lógica de programação.
Analise o código de um aluno individualmente.

Contexto:
{context}

Avalie apenas problemas reais observáveis no código.
Não invente erros.
Não escreva código.
Não entregue a resposta completa.
Se o código parecer adequado, destaque isso em pontos fortes e sugira melhorias pequenas, se existirem.
Se houver erro, explique o impacto de forma curta e didática.

{_markdown_rules()}

Código:
{code}

Resposta:
"""

    return _generate_comment(prompt)
