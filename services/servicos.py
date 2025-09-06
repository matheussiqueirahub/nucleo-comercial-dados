from __future__ import annotations

import sqlite3
from typing import List

from domain.modelos import Produto, Venda
from infra.repositorios import RepositorioProdutoSQL, RepositorioVendaSQL


class OrquestradorDeFluxoComercial:
    """Camada de aplicação que orquestra operações de estoque e vendas.

    Garante consistência transacional ao baixar estoque e registrar vendas.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.repo_prod = RepositorioProdutoSQL(conn)
        self.repo_venda = RepositorioVendaSQL(conn)

    # Catálogo / Estoque
    def cadastrar_produto(
        self, nome: str, descricao: str, quantidade: int, preco: float
    ) -> Produto:
        produto = Produto(
            nome=nome,
            descricao=descricao,
            quantidade_disponivel=quantidade,
            preco=preco,
        )
        with self.conn:
            self.repo_prod.inserir(produto)
        return produto

    def listar_produtos(self) -> List[Produto]:
        return self.repo_prod.listar()

    # Vendas
    def registrar_venda(self, produto_id: int, quantidade: int) -> Venda:
        venda = Venda(produto_id=produto_id, quantidade=quantidade)
        with self.conn:
            # Captura preço no momento da venda e garante consistência atômica
            produto = self.repo_prod.obter_por_id(produto_id)
            if not produto:
                raise ValueError("Produto inexistente")
            self.repo_prod.ajustar_estoque(produto_id, -quantidade)
            self.repo_venda.inserir(venda, preco_unitario=produto.preco)
        return venda

    def listar_vendas(self) -> List[Venda]:
        return self.repo_venda.listar()
