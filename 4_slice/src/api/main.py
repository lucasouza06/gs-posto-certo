"""Camada HTTP: traduz o contrato OpenAPI para chamadas ao domínio."""
import json
import logging
import time
import uuid
from dataclasses import asdict
from typing import Annotated

from fastapi import FastAPI, Header, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.schemas import PaginaOut, PerguntaIn, PostoOut, RespostaOut
from src.domain.erros import IAIndisponivel, PostoNaoEncontrado
from src.domain.models import Servico
from src.domain.ports import LLMPort, PostoRepository
from src.domain.servicos import ServicoAssistente, ServicoPostos

log = logging.getLogger("posto_certo")


def _erro(status: int, codigo: str, mensagem: str, trace_id: str, detalhes=None) -> JSONResponse:
    corpo = {"codigo": codigo, "mensagem": mensagem, "trace_id": trace_id}
    if detalhes:
        corpo["detalhes"] = detalhes
    return JSONResponse(status_code=status, content=corpo)


def criar_app(repo: PostoRepository, llm: LLMPort) -> FastAPI:
    app = FastAPI(title="Posto Certo API", version="1.0.0")
    postos = ServicoPostos(repo)
    assistente = ServicoAssistente(repo, llm)
    cache_idempotencia: dict[str, dict] = {}

    @app.middleware("http")
    async def observabilidade(request: Request, call_next):
        request.state.trace_id = uuid.uuid4().hex[:12]
        inicio = time.perf_counter()
        resposta = await call_next(request)
        log.info(json.dumps({
            "trace_id": request.state.trace_id, "rota": request.url.path,
            "metodo": request.method, "status": resposta.status_code,
            "latencia_ms": round((time.perf_counter() - inicio) * 1000, 1),
        }))
        return resposta

    @app.exception_handler(RequestValidationError)
    async def validacao(request: Request, exc: RequestValidationError):
        tid = request.state.trace_id
        if any(e.get("type") == "json_invalid" for e in exc.errors()):
            return _erro(400, "REQUISICAO_INVALIDA", "JSON malformado", tid)
        detalhes = [{"campo": str(e["loc"][-1]), "problema": e["msg"]} for e in exc.errors()]
        return _erro(422, "VALIDACAO", "Parâmetros inválidos", tid, detalhes)

    @app.exception_handler(PostoNaoEncontrado)
    async def nao_encontrado(request: Request, exc: PostoNaoEncontrado):
        return _erro(404, "POSTO_NAO_ENCONTRADO", str(exc), request.state.trace_id)

    @app.exception_handler(IAIndisponivel)
    async def ia_fora(request: Request, exc: IAIndisponivel):
        log.warning(json.dumps({"trace_id": request.state.trace_id, "evento": "llm_falha"}))
        return _erro(503, "IA_INDISPONIVEL", "Assistente temporariamente indisponível",
                     request.state.trace_id)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/postos", response_model=PaginaOut)
    def listar_postos(
        limit: Annotated[int, Query(ge=1, le=50)] = 10,
        offset: Annotated[int, Query(ge=0)] = 0,
        servico: Servico | None = None,
        bairro: Annotated[str | None, Query(min_length=2, max_length=80)] = None,
    ):
        pagina = postos.listar(limit, offset, servico, bairro)
        prox = offset + limit
        return {
            **asdict(pagina),
            "next": f"/postos?limit={limit}&offset={prox}" if prox < pagina.total else None,
        }

    @app.get("/postos/{id}", response_model=PostoOut)
    def obter_posto(id: Annotated[str, Path(pattern=r"^ubs-[0-9]{3}$")]):
        return asdict(postos.obter(id))

    @app.post("/ask", response_model=RespostaOut)
    def perguntar(
        corpo: PerguntaIn,
        request: Request,
        idempotency_key: Annotated[str | None, Header()] = None,
    ):
        if idempotency_key and idempotency_key in cache_idempotencia:
            return cache_idempotencia[idempotency_key]
        r = assistente.perguntar(corpo.pergunta, corpo.bairro)
        log.info(json.dumps({"trace_id": request.state.trace_id, "evento": "assistente",
                             "motivo": r.motivo.value, "recusada": r.recusada}))
        saida = {**asdict(r), "trace_id": request.state.trace_id}
        if idempotency_key:
            cache_idempotencia[idempotency_key] = saida
        return saida

    return app


def app_producao() -> FastAPI:
    """Ponto de entrada: uvicorn src.api.main:app"""
    from src.infra.config import criar_llm
    from src.infra.repositorio_json import RepositorioJSON

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    return criar_app(RepositorioJSON(), criar_llm())


app = app_producao()
