import pytest
from fastapi.testclient import TestClient

from src.api.main import criar_app
from src.infra.llm.fake import FakeLLM
from src.infra.repositorio_json import RepositorioJSON


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture
def client(fake_llm):
    """App montado com o FAKE: nenhum teste chama LLM real (determinismo)."""
    return TestClient(criar_app(RepositorioJSON(), fake_llm))


@pytest.fixture
def client_factory():
    def _criar(modo: str):
        llm = FakeLLM(modo)
        return TestClient(criar_app(RepositorioJSON(), llm)), llm
    return _criar
