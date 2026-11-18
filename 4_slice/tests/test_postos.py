"""RF-01, RF-02, RF-06 — CA-01, CA-02, CA-03."""


def test_ca01_detalhe_posto_existente(client):
    r = client.get("/postos/ubs-001")
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["status"] in {"ABERTO", "FECHADO", "FUNCIONAMENTO_PARCIAL"}
    assert corpo["documentos_exigidos"]


def test_ca02_posto_inexistente_retorna_404_padronizado(client):
    r = client.get("/postos/ubs-999")
    assert r.status_code == 404
    corpo = r.json()
    assert corpo["codigo"] == "POSTO_NAO_ENCONTRADO"
    assert corpo["trace_id"]


def test_ca03_limit_acima_do_maximo_retorna_422(client):
    r = client.get("/postos?limit=500")
    assert r.status_code == 422
    corpo = r.json()
    assert corpo["codigo"] == "VALIDACAO"
    assert corpo["detalhes"][0]["campo"] == "limit"


def test_id_fora_do_padrao_retorna_422(client):
    assert client.get("/postos/abc").status_code == 422


def test_paginacao_com_next(client):
    p1 = client.get("/postos?limit=2&offset=0").json()
    assert len(p1["itens"]) == 2 and p1["total"] == 5
    assert p1["next"] == "/postos?limit=2&offset=2"
    ultima = client.get("/postos?limit=2&offset=4").json()
    assert ultima["next"] is None


def test_filtro_por_servico(client):
    itens = client.get("/postos?servico=ODONTOLOGIA").json()["itens"]
    assert [p["id"] for p in itens] == ["ubs-002"]
