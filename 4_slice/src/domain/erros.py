class PostoNaoEncontrado(Exception):
    def __init__(self, posto_id: str):
        super().__init__(f"Posto {posto_id} não existe")
        self.posto_id = posto_id


class IAIndisponivel(Exception):
    """Provedor de IA fora do ar ou em timeout (RF-07)."""
