"""Guardrails determinísticos: não dependem do modelo (ver 5_evals_de_ia.md)."""
import re

from src.domain.models import Motivo

_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_CARTAO_SUS = re.compile(r"\b\d{15}\b")
_TELEFONE = re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b")

TERMOS_EMERGENCIA = (
    "dor no peito", "falta de ar", "desmaiou", "desmaio", "convulsão", "convulsao",
    "sangramento", "infarto", "avc", "não respira", "nao respira", "engasgado",
)
TERMOS_CLINICOS = (
    "remédio", "remedio", "medicamento", "dose", "dosagem", "diagnóstico", "diagnostico",
    "tratamento", "o que eu tenho", "devo tomar", "posso tomar", "sintoma",
)

MSG_EMERGENCIA = (
    "Isso pode ser uma emergência. Ligue agora para o SAMU no 192 "
    "ou procure o pronto-socorro mais próximo. Não vá a uma UBS."
)
MSG_FORA_ESCOPO = (
    "Não posso dar orientação médica, indicar remédios ou diagnósticos. "
    "Posso ajudar a encontrar um posto de saúde, horários e documentos necessários."
)
MSG_SEM_DADOS = (
    "Não encontrei essa informação nos dados oficiais dos postos. "
    "Ligue para o 156 da prefeitura para confirmar."
)


def sanitizar(texto: str) -> str:
    """Mascara dados pessoais antes do LLM e dos logs (RNF-06)."""
    texto = _CPF.sub("[CPF]", texto)
    texto = _CARTAO_SUS.sub("[CARTAO_SUS]", texto)
    return _TELEFONE.sub("[TELEFONE]", texto)


def classificar(pergunta: str) -> Motivo:
    p = pergunta.lower()
    if any(t in p for t in TERMOS_EMERGENCIA):
        return Motivo.EMERGENCIA
    if any(t in p for t in TERMOS_CLINICOS):
        return Motivo.FORA_DO_ESCOPO
    return Motivo.OK


def fontes_citadas(resposta: str, ids_permitidos: set[str]) -> list[str]:
    """Retorna só os ids citados que estavam no contexto (anti-alucinação)."""
    citados = re.findall(r"ubs-\d{3}", resposta)
    return sorted({c for c in citados if c in ids_permitidos})
