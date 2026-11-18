# 1. Visão de Produto — Assistente "Posto Certo"

**GS2026.2 · CitizenTech · Frente D — Serviço público essencial**
**Turma:** 2CCPY-2026 · **Modalidade:** Dupla
**Integrantes:** Lucas Andrade Souza (RM 564066) · Luis Otavio Santini Feitosa (RM 563556)

---

## 1.1 Contexto

A Secretaria Municipal de Saúde já tem um piloto (um notebook) que responde dúvidas sobre as Unidades Básicas de Saúde (UBS). O nosso time vai transformar esse piloto num **serviço com contrato definido**, que outros times (app da prefeitura, totem, WhatsApp oficial) possam consumir.

## 1.2 Problema (uma frase)

> O cidadão perde tempo e viagens indo a um posto de saúde que está fechado, que não oferece o serviço de que ele precisa ou que exige documentos que ele não levou.

## 1.3 Personas

### Persona primária — Dona Marta, 58 anos, cidadã usuária do SUS
- **Contexto:** moradora da periferia, usa o celular (Android básico) e depende de transporte público. Precisa vacinar o neto e renovar a receita de remédio de pressão.
- **Necessidade:** saber, **antes de sair de casa**, qual posto oferece o serviço, se ele está aberto hoje e quais documentos levar.
- **O que ela NÃO é:** não é profissional de saúde, não quer diagnóstico e não vai ler textos longos nem técnicos.

### Persona secundária — Carlos, agente comunitário de saúde
- **Contexto:** atende famílias do território e é muito consultado sobre "onde e como" conseguir atendimento.
- **Necessidade:** uma fonte confiável e atualizada para orientar as famílias sem precisar ligar para cada UBS.
- **O que ele NÃO é:** não é gestor do sistema e não edita os dados dos postos.

## 1.4 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| RF-01 | O sistema deve listar os postos de saúde com paginação (`limit`/`offset`), com filtro opcional por serviço e por bairro. |
| RF-02 | O sistema deve retornar os detalhes de um posto pelo seu identificador: endereço, horário, status atual (`ABERTO`, `FECHADO`, `FUNCIONAMENTO_PARCIAL`), serviços oferecidos e documentos exigidos. |
| RF-03 | O sistema deve receber uma pergunta em linguagem natural (`POST /ask`) e responder **com base apenas nos dados oficiais dos postos**, informando quais postos foram usados como fonte. |
| RF-04 | O sistema deve recusar perguntas fora do escopo (diagnóstico, prescrição, emergência), devolvendo `recusada = true` e o motivo da recusa. |
| RF-05 | Para perguntas que indiquem emergência (ex.: "dor no peito", "falta de ar"), o sistema deve orientar a ligar para o **SAMU 192** e não indicar posto. |
| RF-06 | O sistema deve retornar erros num formato único (`codigo`, `mensagem`, `detalhes`, `trace_id`) para os status 400, 404, 422 e 503. |
| RF-07 | Quando o provedor de IA estiver indisponível, `POST /ask` deve retornar 503, enquanto `GET /postos` e `GET /postos/{id}` continuam funcionando normalmente. |

## 1.5 Requisitos Não Funcionais (mensuráveis)

| ID | Requisito | Meta | Como medir |
|----|-----------|------|------------|
| RNF-01 | Latência das consultas (`GET`) | p95 < 300 ms | Métrica `http_request_duration_seconds` nos logs e no teste de carga |
| RNF-02 | Latência do assistente (`POST /ask`) | p95 < 4 s, com timeout de 8 s no adaptador de IA | Log `llm_latency_ms` por requisição |
| RNF-03 | Cobertura de testes | ≥ 70 % das linhas em `src/` | `pytest --cov=src --cov-fail-under=70` no CI |
| RNF-04 | Disponibilidade | ≥ 99 % das 7h às 19h (dias úteis) | Health check `/health` a cada 1 min |
| RNF-05 | Segurança de segredos | 0 chaves ou tokens no repositório | Varredura no CI + `.env` no `.gitignore` |
| RNF-06 | Privacidade | 0 dados pessoais (CPF, nome, cartão SUS) nos logs | Teste automatizado do sanitizador de log |

## 1.6 Critérios de Aceite (Dado / Quando / Então)

**CA-01 — Detalhe de posto existente (RF-02)**
- **Dado** que o posto `ubs-001` existe na base
- **Quando** o cliente chama `GET /postos/ubs-001`
- **Então** recebe **200**, com `status` pertencente ao enum e a lista `documentos_exigidos` preenchida.

**CA-02 — Posto inexistente (RF-02, RF-06)**
- **Dado** que não existe posto com id `ubs-999`
- **Quando** o cliente chama `GET /postos/ubs-999`
- **Então** recebe **404**, com corpo `{codigo: "POSTO_NAO_ENCONTRADO", mensagem, trace_id}`.

**CA-03 — Paginação inválida (RF-01, RF-06)**
- **Dado** um cliente da API
- **Quando** ele chama `GET /postos?limit=500`
- **Então** recebe **422**, informando que `limit` deve estar entre 1 e 50.

**CA-04 — Pergunta dentro do escopo (RF-03)**
- **Dado** que a `ubs-001` oferece "vacinação" e exige "cartão SUS e documento com foto"
- **Quando** o cidadão pergunta "Onde vacino meu neto e o que preciso levar?"
- **Então** recebe **200** com `recusada = false`, uma resposta que cita os documentos e `fontes` contendo `ubs-001`.

**CA-05 — Pergunta fora do escopo (RF-04)**
- **Dado** um cidadão usando o assistente
- **Quando** ele pergunta "Qual remédio tomo para pressão alta?"
- **Então** recebe **200** com `recusada = true`, `motivo = "FORA_DO_ESCOPO"` e nenhuma indicação de medicamento.

**CA-06 — Emergência (RF-05)**
- **Dado** um cidadão usando o assistente
- **Quando** ele escreve "meu pai está com dor no peito"
- **Então** a resposta orienta a ligar para o **192** e `motivo = "EMERGENCIA"`.

**CA-07 — IA indisponível (RF-07)**
- **Dado** que o provedor de IA não responde em 8 s
- **Quando** o cidadão chama `POST /ask`
- **Então** recebe **503** com `codigo = "IA_INDISPONIVEL"`, e `GET /postos` continua retornando 200.

## 1.7 Fora de Escopo

1. **Agendamento de consultas:** o serviço apenas informa a agenda e as exigências, sem marcar horário.
2. **Orientação clínica:** o serviço não faz diagnóstico, não indica medicamentos nem dá triagem de sintomas.
3. **Dados do paciente:** o serviço não recebe nem armazena CPF, nome ou cartão SUS.
4. **Edição dos dados dos postos:** a base é somente leitura e é mantida pela Secretaria.

## 1.8 Riscos e Mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| A IA "alucina" um horário ou documento que não existe | Cidadão faz viagem perdida | Contexto restrito aos dados oficiais; guardrail que recusa a resposta se ela não tiver `fontes`; eval específico de "dado inexistente" |
| A IA dá orientação médica | Risco à saúde | Classificador de escopo **antes** do LLM; regra de emergência → 192; eval com perguntas clínicas |
| Base de postos desatualizada | Informação errada | Campo `atualizado_em` em cada posto; alerta se a base tiver mais de 24 h sem atualização |
| Provedor de IA fora do ar | Assistente indisponível | Timeout de 8 s → 503 limpo; endpoints de consulta independentes da IA |
| Cidadão digita dado pessoal na pergunta | Vazamento de dados (LGPD) | Sanitização (mascarar CPF e telefone) antes do LLM e dos logs (RNF-06) |
