import json
import urllib.error
import urllib.request

from src.domain.erros import IAIndisponivel


class OllamaLLM:
    """Adaptador de LLMPort para Ollama (local ou cloud). Só biblioteca padrão."""

    def __init__(self, url: str, modelo: str, timeout_s: float = 8.0, api_key: str | None = None):
        self.url = url.rstrip("/")
        self.modelo = modelo
        self.timeout_s = timeout_s
        self.api_key = api_key

    def gerar(self, prompt: str) -> str:
        corpo = json.dumps({"model": self.modelo, "prompt": prompt, "stream": False,
                            "options": {"temperature": 0}}).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(f"{self.url}/api/generate", data=corpo, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as r:  # noqa: S310
                return json.loads(r.read())["response"]
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
            raise IAIndisponivel(str(e)) from e
