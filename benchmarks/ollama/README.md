# Benchmark local de LLMs com Ollama

Esta pasta isola um experimento para comparar modelos locais usados na geração de feedback pedagógico. Ela não altera o fluxo principal do Django e não salva resultados no Git por padrão.

## Estrutura

- `benchmark_ollama.py`: executa os testes via API do Ollama.
- `prepare_ollama_models.py`: baixa modelos usando a API local do Ollama.
- `config.example.json`: lista modelos, parâmetros e quantidade de repetições.
- `prompts.example.json`: casos provisórios de feedback. O prompt final é montado pela mesma função `_build_prompt` usada no OverCode.
- `requirements.txt`: dependências opcionais para monitoramento e gráficos.
- `results/`: saída dos experimentos, ignorada pelo Git.

## Preparação

1. Suba o Ollama local. Neste projeto ele já existe no `docker-compose.yml`.

```bash
docker compose up -d ollama
```

Se o comando `docker` não estiver acessível no WSL, abra o Docker Desktop e habilite a integração com a distribuição WSL usada no projeto. Como alternativa temporária no Windows, é possível chamar o binário do Docker Desktop diretamente.

2. Baixe os modelos que deseja testar.

```bash
python3 benchmarks/ollama/prepare_ollama_models.py --model llama3.2:1b
python3 benchmarks/ollama/prepare_ollama_models.py --model qwen2.5:1.5b
python3 benchmarks/ollama/prepare_ollama_models.py --model tinyllama:1.1b
```

Confira os nomes disponíveis com:

```bash
python3 benchmarks/ollama/benchmark_ollama.py --dry-run
```

Para baixar todos os modelos configurados:

```bash
python3 benchmarks/ollama/prepare_ollama_models.py
```

Os nomes em `config.example.json` podem precisar de ajuste conforme os tags disponíveis na instalação local.

3. Opcionalmente, instale as dependências do benchmark.

```bash
python3 -m pip install -r benchmarks/ollama/requirements.txt
```

Sem `psutil`, o benchmark continua funcionando, mas CPU/RAM ficam como `null`. Sem `nvidia-smi`, as métricas de GPU também ficam como `null`.

## Execução

Valide a configuração e a disponibilidade dos modelos:

```bash
python3 benchmarks/ollama/benchmark_ollama.py --dry-run
```

Execute o benchmark completo configurado:

```bash
python3 benchmarks/ollama/benchmark_ollama.py
```

Execute apenas um modelo ou prompt:

```bash
python3 benchmarks/ollama/benchmark_ollama.py --model llama3.2:1b
python3 benchmarks/ollama/benchmark_ollama.py --prompt-id feedback_exemplo_solucao_incorreta
```

Sobrescreva a quantidade de repetições:

```bash
python3 benchmarks/ollama/benchmark_ollama.py --repetitions 2
```

## Saídas

Cada execução cria uma pasta em `benchmarks/ollama/results/<timestamp>/` com:

- `metadata.json`: hardware, versão do Ollama, parâmetros e modelos ausentes.
- `built_prompts.json`: prompts finais enviados ao Ollama, já montados a partir dos casos de feedback.
- `partial_results.*` e `partial_summary.*`: checkpoints atualizados a cada execução concluída.
- `raw_results.csv` e `raw_results.json`: uma linha por execução.
- `summary.csv` e `summary.json`: médias, mediana, desvio-padrão e percentil 95.
- `quality_review_template.csv`: planilha para avaliação manual da qualidade.
- `report.md`: resumo comparativo inicial.
- `charts/`: gráficos quando `matplotlib` estiver disponível.

## Métricas

O script mede:

- tempo total local da requisição;
- tempo até o primeiro token, usando streaming;
- tokens por segundo, quando o Ollama informa `eval_count` e `eval_duration`;
- texto bruto retornado pelo modelo e texto pós-processado pela metodologia atual do OverCode;
- erros de validação antes e depois do pós-processamento;
- taxa de sucesso;
- metadados do modelo, incluindo quantização quando o Ollama informar;
- CPU/RAM quando `psutil` estiver instalado;
- GPU NVIDIA quando `nvidia-smi` estiver disponível.

Métricas indisponíveis são registradas como `null`.

Para gerar sem timeout, configure `"timeout_seconds": 0` no arquivo de configuração.
Na aplicação, `OLLAMA_TIMEOUT=0` desativa o timeout da chamada ao modelo e
`GUNICORN_TIMEOUT=0` desativa o timeout do worker em produção.

O teto de saída é independente do timeout: `generation_options.num_predict` no
benchmark e `OLLAMA_NUM_PREDICT` na aplicação controlam o máximo de tokens
gerados. O padrão do projeto é 1024 tokens; os dois modelos devem usar o mesmo
valor em uma comparação. Um teto maior permite respostas completas, mas não
garante correção nem impede repetições. Nas medições, `done_reason="length"`
indica que a geração atingiu o teto de saída.

## Qualidade das respostas

Enquanto o prompt final de feedback ainda estiver em construção, use `prompts.example.json` apenas para validar a ferramenta. O arquivo agora aceita casos no formato:

```json
{
  "id": "caso_exemplo",
  "type": "overcode_feedback_case",
  "mode": "student",
  "exercise_statement": "Enunciado do exercício.",
  "correction_evidence": "Resultado dos testes automáticos.",
  "code": "codigo_do_aluno()"
}
```

O benchmark chama a função `_build_prompt` do projeto para montar o prompt completo. Isso mantém o teste próximo do fluxo real de geração de feedback.

Antes de comparar modelos de verdade, crie um arquivo local, por exemplo:

```bash
cp benchmarks/ollama/prompts.example.json benchmarks/ollama/prompts.local.json
cp benchmarks/ollama/config.example.json benchmarks/ollama/config.local.json
```

Depois altere `prompt_file` em `config.local.json` para `benchmarks/ollama/prompts.local.json` e substitua os exemplos por casos reais do sistema.

Sugestão de avaliação manual em escala de 1 a 5:

- correção conceitual;
- clareza;
- utilidade pedagógica;
- completude;
- risco de alucinação.

Não use resultados dos prompts provisórios como evidência científica; eles servem apenas para testar a automação.
