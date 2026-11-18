# Posto Certo — Assistente de Saúde Pública com IA

**GS2026.2 · CitizenTech · Prompt and Artificial Intelligence
Frente D — Serviço público essencial** · Turma 2CCPY-2026 · Modalidade: **Dupla**
Prof. Jorge Luiz Gomes

|Integrante|RM|
|-|-|
|Lucas Andrade Souza|564066|
|Luis Otavio Santini Feitosa|563556|

> \\\*\\\*Problema:\\\*\\\* o cidadão perde tempo e viagens indo a um posto de saúde fechado, que não oferece o serviço ou que exige documentos que ele não levou.
> \\\*\\\*Solução:\\\*\\\* uma API que informa postos, horários e exigências, com um assistente de IA protegido por guardrails, em que o modelo de IA pode ser trocado sem reescrever o serviço.

\---

## Índice do dossiê

|#|Arquivo|Conteúdo|Critério|
|-|-|-|-|
|1|[`1\\\_visao\\\_produto.md`](1_visao_produto.md)|Persona, problema, 7 RF, 6 RNF mensuráveis, 7 critérios de aceite, fora de escopo, riscos|2|
|2|[`2\\\_contrato\\\_api.yaml`](2_contrato_api.yaml)|OpenAPI 3.0.3: 4 endpoints, schemas, erros 400/404/422/503|3|
|3|[`3\\\_arquitetura.md`](3_arquitetura.md)|Diagramas, portas/adaptadores, 3 ADRs, observabilidade, segurança|4|
|4|[`4\\\_slice/`](4_slice)|Código FastAPI + 26 testes + CI|5|
|5|[`5\\\_evals\\\_de\\\_ia.md`](5_evals_de_ia.md)|10 casos, métrica com meta, 4 guardrails, regressão, rollout|6|
|6|`6\\\_README.md`|Este arquivo|7|
|7|`7\\\_demo\\\_video\\\_url.txt`|Link do vídeo (≤ 3 min)|1|
|8|`8\\\_certificacao.txt`|Resumo + links + nomes/RMs|1|
|9|`9\\\_Chat\\\_Log.txt`|Registro do uso de IA|1|

**Repositório:** `https://github.com/<lucasouza06>/<gs-posto-certo>`

## Rastreabilidade: a mesma história em todas as peças

|Requisito|Contrato|Código|Teste|Eval|
|-|-|-|-|-|
|RF-02 / CA-02: posto inexistente|`GET /postos/{id}` → 404 `Erro`|`PostoNaoEncontrado` → handler 404|`test\\\_ca02\\\_...`|—|
|RF-04 / CA-05: recusa clínica|`Resposta.motivo = FORA\\\_DO\\\_ESCOPO`|`guardrails.classificar()`|`test\\\_ca05\\\_...`|EV-05|
|RF-05 / CA-06: emergência|`Resposta.motivo = EMERGENCIA`|`guardrails.classificar()`|`test\\\_ca06\\\_...`|EV-06|
|RF-07 / CA-07: IA fora|`POST /ask` → 503 `IA\\\_INDISPONIVEL`|`IAIndisponivel` → handler 503|`test\\\_ca07\\\_...`|—|
|Risco: alucinação|`Resposta.fontes` (required)|`guardrails.fontes\\\_citadas()`|`test\\\_alucinacao\\\_...`|EV-07, EV-08|

## Como executar

### Opção A — Local (Python 3.11+)

```bash
cd 4\\\_slice
pip install -r requirements-dev.txt
pytest --cov=src                         # 26 testes, sem LLM real
uvicorn src.api.main:app --reload        # API em http://localhost:8000/docs
```

### Opção B — GitHub Codespaces (sem instalar nada)

Abra o repositório no GitHub e clique em **Code → Codespaces → Create codespace**. As dependências são instaladas automaticamente (`.devcontainer/`). No terminal, rode os mesmos comandos da opção A.

### Validar o contrato OpenAPI

```bash
openapi-spec-validator 2\\\_contrato\\\_api.yaml
# saída: 2\\\_contrato\\\_api.yaml: OK
```

### Rodar a suíte de evals de IA

```bash
cd 4\\\_slice
python -m evals.run\\\_evals                       # com o fake
LLM\\\_PROVIDER=ollama python -m evals.run\\\_evals   # com modelo real (Ollama)
```

### Trocar o modelo de IA (1 linha de configuração)

```bash
cp 4\\\_slice/.env.example 4\\\_slice/.env
# LLM\\\_PROVIDER=fake    → LLM\\\_PROVIDER=ollama
```

## Requisições reais

```bash
curl http://localhost:8000/postos/ubs-001
# 200 {"id":"ubs-001","nome":"UBS Vila Nova","status":"ABERTO", ...}

curl http://localhost:8000/postos/ubs-999
# 404 {"codigo":"POSTO\\\_NAO\\\_ENCONTRADO","mensagem":"Posto ubs-999 não existe","trace\\\_id":"..."}

curl "http://localhost:8000/postos?limit=500"
# 422 {"codigo":"VALIDACAO","detalhes":\\\[{"campo":"limit", ...}], ...}

curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" \\\\
     -d '{"pergunta":"Onde vacino meu neto?"}'
# 200 {"resposta":"Procure a UBS Vila Nova \\\[ubs-001]. Leve: Cartão SUS, ...",
#      "recusada":false,"motivo":"OK","fontes":\\\["ubs-001"],"trace\\\_id":"..."}

curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" \\\\
     -d '{"pergunta":"meu pai está com dor no peito"}'
# 200 {"resposta":"... Ligue agora para o SAMU no 192 ...","recusada":true,"motivo":"EMERGENCIA", ...}
```

## Evidências

### CI do GitHub Actions (verde)

<img src="prints/ci\_verde.png" alt="CI verde" width="800">

&#x20;

<img src="prints/ci\_testes.png" alt="Resultado dos testes no CI" width="800">



Link da execução: https://github.com/lucasouza06/gs-posto-certo/actions/runs/44407059766



O pipeline executa: **lint (ruff) → validação do OpenAPI → varredura de segredos → pytest com cobertura ≥ 70 %**.

### pytest local



<img src="prints/pytest.png" alt="pytest local" width="800">



## Estrutura do slice

```
4\\\_slice/
├── src/
│   ├── domain/     # regras puras: modelos, portas, serviços, guardrails (sem lib de IA)
│   ├── infra/      # adaptadores: repositório JSON, FakeLLM, OllamaLLM, config
│   └── api/        # FastAPI: rotas, schemas espelhando o contrato, erros padronizados
├── tests/          # 26 testes — todos com FakeLLM (determinísticos)
│   ├── test\\\_postos.py      # caminho feliz e erros (CA-01..03)
│   ├── test\\\_ask.py         # assistente, guardrails e 503 (CA-04..07)
│   ├── test\\\_contrato.py    # resposta real x schema do YAML (teste de contrato)
│   └── test\\\_fronteira.py   # domínio não importa lib de LLM; troca por config
├── evals/          # suíte de qualidade da IA (roda contra o modelo real)
└── .github/workflows/ci.yml
```

## Decisões e observações

* **O contrato foi escrito antes do código.** Os schemas Pydantic em `src/api/schemas.py` espelham o YAML, e o `test\\\_contrato.py` falha se divergirem.
* **O `ci.yml` existe em dois lugares.** O GitHub Actions só executa workflows na raiz do repositório (`/.github/workflows/`). A cópia em `4\\\_slice/.github/workflows/ci.yml` atende à estrutura pedida no briefing. As duas são idênticas.
* **O LLM padrão é o `FakeLLM`.** O `POST /ask` funciona sem modelo instalado. Para usar um modelo real, basta `LLM\\\_PROVIDER=ollama` (ver ADR-03).
* **Nenhuma chave no repositório.** Segredos vêm só de variáveis de ambiente, o `.env` está no `.gitignore` e o CI faz uma varredura.
* **Bônus:** teste de contrato automatizado (schema × resposta) em `tests/test\\\_contrato.py`.

