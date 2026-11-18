"""Prova da fronteira: o domínio não conhece nenhum LLM nem framework."""
import ast
from pathlib import Path

PROIBIDOS = {"fastapi", "httpx", "requests", "urllib", "ollama", "openai", "langchain", "anthropic"}
DOMINIO = Path(__file__).resolve().parents[1] / "src" / "domain"


def test_dominio_nao_importa_lib_de_llm_nem_infra():
    for arquivo in DOMINIO.glob("*.py"):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom):
                nomes = [no.module or ""]
            else:
                continue
            for nome in nomes:
                raiz = nome.split(".")[0]
                assert raiz not in PROIBIDOS, f"{arquivo.name} importa {nome}"
                assert not nome.startswith(("src.infra", "src.api")), f"{arquivo.name} importa {nome}"


def test_trocar_llm_e_so_configuracao(monkeypatch):
    from src.infra.config import criar_llm
    from src.infra.llm.fake import FakeLLM
    from src.infra.llm.ollama import OllamaLLM

    monkeypatch.setenv("LLM_PROVIDER", "fake")
    assert isinstance(criar_llm(), FakeLLM)
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    assert isinstance(criar_llm(), OllamaLLM)


def test_adaptador_ollama_fora_do_ar_vira_ia_indisponivel():
    import pytest

    from src.domain.erros import IAIndisponivel
    from src.infra.llm.ollama import OllamaLLM

    llm = OllamaLLM(url="http://127.0.0.1:9", modelo="x", timeout_s=0.5)
    with pytest.raises(IAIndisponivel):
        llm.gerar("oi")
