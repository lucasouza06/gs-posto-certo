"""Teste de contrato automatizado: resposta real x schema do 2_contrato_api.yaml."""
from pathlib import Path

import pytest
import yaml
from openapi_schema_validator import OAS30Validator

CONTRATO = Path(__file__).resolve().parents[2] / "2_contrato_api.yaml"
SPEC = yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def validar(instancia: dict, nome_schema: str) -> None:
    schema = {"$ref": f"#/components/schemas/{nome_schema}", "components": SPEC["components"]}
    OAS30Validator(schema).validate(instancia)


@pytest.mark.parametrize("metodo,url,corpo,status,schema", [
    ("get", "/postos", None, 200, "PaginaPostos"),
    ("get", "/postos/ubs-001", None, 200, "Posto"),
    ("get", "/postos/ubs-999", None, 404, "Erro"),
    ("get", "/postos?limit=0", None, 422, "Erro"),
    ("post", "/ask", {"pergunta": "Onde tem vacina?"}, 200, "Resposta"),
    ("post", "/ask", {"pergunta": "dor no peito"}, 200, "Resposta"),
])
def test_resposta_respeita_schema_do_contrato(client, metodo, url, corpo, status, schema):
    r = client.post(url, json=corpo) if metodo == "post" else client.get(url)
    assert r.status_code == status
    validar(r.json(), schema)


def test_503_respeita_schema_do_contrato(client_factory):
    client, _ = client_factory("falha")
    r = client.post("/ask", json={"pergunta": "Onde tem vacina?"})
    assert r.status_code == 503
    validar(r.json(), "Erro")


def test_todas_as_rotas_do_contrato_existem_no_codigo(client):
    rotas_codigo = {route.path for route in client.app.routes}
    for path in SPEC["paths"]:
        assert path in rotas_codigo, f"{path} está no contrato mas não no código"
