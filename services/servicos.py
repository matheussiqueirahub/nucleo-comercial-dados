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
            ativo=True,
        )
        with self.conn:
            self.repo_prod.inserir(produto)
        return produto

    def listar_produtos(
        self, *, consulta: str | None = None, include_inativos: bool = False
    ) -> List[Produto]:
        if consulta:
            return self.repo_prod.buscar_por_nome(consulta)
        return self.repo_prod.listar(include_inativos=include_inativos)

    def obter_produto(
        self, produto_id: int, *, include_inativos: bool = False
    ) -> Produto:
        produto = self.repo_prod.obter_por_id(
            produto_id, include_inativos=include_inativos
        )
        if not produto:
            raise ValueError("Produto inexistente")
        return produto

    def atualizar_produto(
        self,
        produto_id: int,
        *,
        nome: str | None = None,
        descricao: str | None = None,
        quantidade_disponivel: int | None = None,
        preco: float | None = None,
    ) -> Produto:
        produto = self.obter_produto(produto_id, include_inativos=True)
        if nome is not None:
            produto.nome = nome
        if descricao is not None:
            produto.descricao = descricao
        if quantidade_disponivel is not None:
            produto.quantidade_disponivel = quantidade_disponivel
        if preco is not None:
            produto.preco = preco
        produto.__post_init__()
        with self.conn:
            self.repo_prod.atualizar(produto)
        return produto

    def ajustar_estoque(self, produto_id: int, delta: int) -> None:
        with self.conn:
            self.repo_prod.ajustar_estoque(produto_id, delta)

    def inativar_produto(self, produto_id: int) -> None:
        with self.conn:
            self.repo_prod.inativar(produto_id)

    # Vendas
    def registrar_venda(self, produto_id: int, quantidade: int) -> Venda:
        venda = Venda(produto_id=produto_id, quantidade=quantidade)
        with self.conn:
            # Captura preço no momento da venda e garante consistência atômica
            produto = self.repo_prod.obter_por_id(
                produto_id, include_inativos=True
            )
            if not produto:
                raise ValueError("Produto inexistente")
            if not produto.ativo:
                raise ValueError("Produto inativo")
            self.repo_prod.ajustar_estoque(produto_id, -quantidade)
            self.repo_venda.inserir(venda, preco_unitario=produto.preco)
        return venda

    def listar_vendas(self) -> List[Venda]:
        return self.repo_venda.listar()

    def listar_vendas_por_produto(self, produto_id: int) -> List[Venda]:
        _ = self.obter_produto(produto_id, include_inativos=True)
        return self.repo_venda.listar_por_produto(produto_id)
