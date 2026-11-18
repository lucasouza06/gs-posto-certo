"""Portas: o domínio define O QUE precisa; a infra decide COMO."""
from typing import Protocol

from src.domain.models import Posto, Servico


class PostoRepository(Protocol):
    def listar(self, servico: Servico | None = None, bairro: str | None = None) -> list[Posto]: ...

    def obter(self, posto_id: str) -> Posto | None: ...


class LLMPort(Protocol):
    """Qualquer modelo (fake, Ollama, GPT, RAG...) implementa só isto.

    Deve levantar IAIndisponivel em timeout ou falha.
    """

    def gerar(self, prompt: str) -> str: ...
