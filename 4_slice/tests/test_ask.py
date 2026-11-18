"""RF-03, RF-04, RF-05, RF-07 — CA-04 a CA-07. Sempre com FakeLLM."""


def test_ca04_pergunta_no_escopo_responde_com_fontes(client):
    r = client.post("/ask", json={"pergunta": "Onde vacino meu neto e o que preciso levar?"})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["recusada"] is False and corpo["motivo"] == "OK"
    assert "ubs-001" in corpo["fontes"]
    assert "Cartão SUS" in corpo["resposta"]


def test_ca05_pergunta_clinica_e_recusada_sem_chamar_llm(client, fake_llm):
    r = client.post("/ask", json={"pergunta": "Qual remédio tomo para pressão alta?"})
    corpo = r.json()
    assert corpo["recusada"] is True and corpo["motivo"] == "FORA_DO_ESCOPO"
    assert corpo["fontes"] == []
    assert fake_llm.chamadas == []


def test_ca06_emergencia_orienta_192(client, fake_llm):
    r = client.post("/ask", json={"pergunta": "meu pai está com dor no peito"})
    corpo = r.json()
    assert corpo["motivo"] == "EMERGENCIA" and "192" in corpo["resposta"]
    assert fake_llm.chamadas == []


def test_ca07_ia_fora_retorna_503_e_consulta_continua(client_factory):
    client, _ = client_factory("falha")
    r = client.post("/ask", json={"pergunta": "Onde tem vacina?"})
    assert r.status_code == 503
    assert r.json()["codigo"] == "IA_INDISPONIVEL"
    assert client.get("/postos").status_code == 200


def test_alucinacao_sem_fonte_valida_vira_sem_dados(client_factory):
    client, _ = client_factory("alucina")
    corpo = client.post("/ask", json={"pergunta": "Onde tem vacina?"}).json()
    assert corpo["recusada"] is True and corpo["motivo"] == "SEM_DADOS"
    assert "ubs-777" not in corpo["resposta"]


def test_dado_pessoal_e_mascarado_antes_do_llm(client, fake_llm):
    client.post("/ask", json={"pergunta": "Meu CPF é 123.456.789-00, onde vacino?"})
    assert "123.456.789-00" not in fake_llm.chamadas[0]
    assert "[CPF]" in fake_llm.chamadas[0]


def test_pergunta_vazia_retorna_422(client):
    assert client.post("/ask", json={"pergunta": ""}).status_code == 422


def test_json_malformado_retorna_400(client):
    r = client.post("/ask", content="{nao é json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    assert r.json()["codigo"] == "REQUISICAO_INVALIDA"


def test_idempotency_key_nao_chama_llm_duas_vezes(client, fake_llm):
    h = {"Idempotency-Key": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}
    r1 = client.post("/ask", json={"pergunta": "Onde tem vacina?"}, headers=h).json()
    r2 = client.post("/ask", json={"pergunta": "Onde tem vacina?"}, headers=h).json()
    assert r1 == r2 and len(fake_llm.chamadas) == 1
