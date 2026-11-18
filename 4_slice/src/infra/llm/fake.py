import re

from src.domain.erros import IAIndisponivel


class FakeLLM:
    """Adaptador determinístico de LLMPort para testes, CI e demo sem modelo.

    modo="normal"   -> responde citando o primeiro posto do contexto
    modo="falha"    -> simula provedor fora do ar (503)
    modo="alucina"  -> responde sem citar fonte válida
    """

    def __init__(self, modo: str = "normal"):
        self.modo = modo
        self.chamadas: list[str] = []

    def gerar(self, prompt: str) -> str:
        self.chamadas.append(prompt)
        if self.modo == "falha":
            raise IAIndisponivel("fake configurado para falhar")
        if self.modo == "alucina":
            return "A UBS Central [ubs-777] abre 24h e não exige documentos."
        m = re.search(r'"id": "(ubs-\d{3})", "nome": "([^"]+)"', prompt)
        docs = re.search(r'"documentos_exigidos": \[([^\]]*)\]', prompt)
        if not m:
            return "SEM_DADOS"
        levar = docs.group(1).replace('"', "") if docs else "documento com foto"
        return f"Procure a {m.group(2)} [{m.group(1)}]. Leve: {levar}."
