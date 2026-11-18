import json
from pathlib import Path

from src.domain.models import Horario, Posto, Servico, StatusPosto

ARQUIVO_PADRAO = Path(__file__).parent / "data" / "postos.json"


class RepositorioJSON:
    """Adaptador de PostoRepository lendo a base oficial em JSON."""

    def __init__(self, caminho: Path = ARQUIVO_PADRAO):
        bruto = json.loads(Path(caminho).read_text(encoding="utf-8"))
        self._postos = [self._converter(p) for p in bruto]

    @staticmethod
    def _converter(p: dict) -> Posto:
        return Posto(
            id=p["id"], nome=p["nome"], endereco=p["endereco"], bairro=p["bairro"],
            status=StatusPosto(p["status"]),
            horarios=[Horario(**h) for h in p["horarios"]],
            servicos=[Servico(s) for s in p["servicos"]],
            documentos_exigidos=p["documentos_exigidos"],
            atualizado_em=p["atualizado_em"],
        )

    def listar(self, servico=None, bairro=None) -> list[Posto]:
        r = self._postos
        if servico:
            r = [p for p in r if servico in p.servicos]
        if bairro:
            r = [p for p in r if p.bairro.lower() == bairro.lower()]
        return list(r)

    def obter(self, posto_id: str) -> Posto | None:
        return next((p for p in self._postos if p.id == posto_id), None)
