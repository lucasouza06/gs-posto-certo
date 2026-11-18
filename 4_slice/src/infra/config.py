"""Composição: o ÚNICO lugar que decide qual LLM está embaixo.

Trocar o modelo = trocar LLM_PROVIDER (e OLLAMA_MODEL). Nada no domínio muda.
Segredos vêm só de variáveis de ambiente — nunca do código.
"""
import os

from src.domain.ports import LLMPort
from src.infra.llm.fake import FakeLLM
from src.infra.llm.ollama import OllamaLLM


def criar_llm() -> LLMPort:
    provedor = os.getenv("LLM_PROVIDER", "fake")
    if provedor == "fake":
        return FakeLLM()
    if provedor == "ollama":
        return OllamaLLM(
            url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            modelo=os.getenv("OLLAMA_MODEL", "llama3.2"),
            timeout_s=float(os.getenv("LLM_TIMEOUT_S", "8")),
            api_key=os.getenv("OLLAMA_API_KEY"),
        )
    raise ValueError(f"LLM_PROVIDER desconhecido: {provedor}")
