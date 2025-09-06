from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Produto:
    """Entidade de domínio para o catálogo de produtos."""

    nome: str
    descricao: str = ""
    quantidade_disponivel: int = 0
    preco: float = 0.0
    id: int | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do produto é obrigatório")
        if self.quantidade_disponivel < 0:
            raise ValueError("Quantidade disponível não pode ser negativa")
        if self.preco < 0:
            raise ValueError("Preço não pode ser negativo")


@dataclass
class Venda:
    """Entidade de domínio para o registro de vendas."""

    produto_id: int
    quantidade: int
    data_venda: datetime = field(default_factory=datetime.utcnow)
    id: int | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if self.produto_id is None:
            raise ValueError("Venda deve referenciar um produto válido")
        if self.quantidade <= 0:
            raise ValueError("Quantidade vendida deve ser positiva")
