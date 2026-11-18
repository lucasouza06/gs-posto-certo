"""Schemas Pydantic espelhando 2_contrato_api.yaml (mesmos campos, enums e required)."""
from pydantic import BaseModel, ConfigDict, Field

from src.domain.models import Motivo, Servico, StatusPosto


class HorarioOut(BaseModel):
    dia_semana: str
    abre: str
    fecha: str


class PostoOut(BaseModel):
    id: str
    nome: str
    endereco: str
    bairro: str
    status: StatusPosto
    horarios: list[HorarioOut]
    servicos: list[Servico]
    documentos_exigidos: list[str]
    atualizado_em: str


class PaginaOut(BaseModel):
    itens: list[PostoOut]
    total: int
    limit: int
    offset: int
    next: str | None


class PerguntaIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pergunta: str = Field(min_length=3, max_length=500)
    bairro: str | None = Field(default=None, min_length=2, max_length=80)


class RespostaOut(BaseModel):
    resposta: str
    recusada: bool
    motivo: Motivo
    fontes: list[str]
    trace_id: str
