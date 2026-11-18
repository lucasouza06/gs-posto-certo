"""Entidades do domínio. Sem dependência de framework nem de IA."""
from dataclasses import dataclass, field
from enum import Enum


class StatusPosto(str, Enum):
    ABERTO = "ABERTO"
    FECHADO = "FECHADO"
    FUNCIONAMENTO_PARCIAL = "FUNCIONAMENTO_PARCIAL"


class Servico(str, Enum):
    VACINACAO = "VACINACAO"
    CONSULTA_CLINICO = "CONSULTA_CLINICO"
    RENOVACAO_RECEITA = "RENOVACAO_RECEITA"
    EXAME_SANGUE = "EXAME_SANGUE"
    ODONTOLOGIA = "ODONTOLOGIA"
    PRE_NATAL = "PRE_NATAL"


class Motivo(str, Enum):
    OK = "OK"
    FORA_DO_ESCOPO = "FORA_DO_ESCOPO"
    EMERGENCIA = "EMERGENCIA"
    SEM_DADOS = "SEM_DADOS"


@dataclass(frozen=True)
class Horario:
    dia_semana: str
    abre: str
    fecha: str


@dataclass(frozen=True)
class Posto:
    id: str
    nome: str
    endereco: str
    bairro: str
    status: StatusPosto
    horarios: list[Horario]
    servicos: list[Servico]
    documentos_exigidos: list[str]
    atualizado_em: str


@dataclass(frozen=True)
class Pagina:
    itens: list[Posto]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class RespostaAssistente:
    resposta: str
    recusada: bool
    motivo: Motivo
    fontes: list[str] = field(default_factory=list)
