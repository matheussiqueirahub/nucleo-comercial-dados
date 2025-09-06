from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import List, Optional

from domain.modelos import Produto, Venda


class RepositorioProdutoSQL:
    """Repositório relacional de Produtos (SQLite)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def inserir(self, produto: Produto) -> Produto:
        q = (
            "INSERT INTO produtos (nome, descricao, quantidade_disponivel, preco) "
            "VALUES (?, ?, ?, ?)"
        )
        cur = self.conn.execute(
            q,
            (
                produto.nome.strip(),
                produto.descricao or "",
                int(produto.quantidade_disponivel),
                float(produto.preco),
            ),
        )
        produto.id = int(cur.lastrowid)
        return produto

    def atualizar(self, produto: Produto) -> None:
        if produto.id is None:
            raise ValueError("Produto sem ID para atualização")
        q = (
            "UPDATE produtos SET nome=?, descricao=?, quantidade_disponivel=?, preco=? "
            "WHERE id=?"
        )
        self.conn.execute(
            q,
            (
                produto.nome.strip(),
                produto.descricao or "",
                int(produto.quantidade_disponivel),
                float(produto.preco),
                int(produto.id),
            ),
        )

    def obter_por_id(self, produto_id: int) -> Optional[Produto]:
        q = "SELECT id, nome, descricao, quantidade_disponivel, preco FROM produtos WHERE id=?"
        row = self.conn.execute(q, (int(produto_id),)).fetchone()
        if not row:
            return None
        return Produto(
            id=int(row["id"]),
            nome=row["nome"],
            descricao=row["descricao"],
            quantidade_disponivel=int(row["quantidade_disponivel"]),
            preco=float(row["preco"]),
        )

    def listar(self) -> List[Produto]:
        q = (
            "SELECT id, nome, descricao, quantidade_disponivel, preco "
            "FROM produtos ORDER BY nome ASC"
        )
        cur = self.conn.execute(q)
        return [
            Produto(
                id=int(r["id"]),
                nome=r["nome"],
                descricao=r["descricao"],
                quantidade_disponivel=int(r["quantidade_disponivel"]),
                preco=float(r["preco"]),
            )
            for r in cur.fetchall()
        ]

    def ajustar_estoque(self, produto_id: int, delta: int) -> None:
        # Garante que não fique negativo
        atual = self.obter_por_id(produto_id)
        if not atual:
            raise ValueError("Produto inexistente")
        nova_qtd = atual.quantidade_disponivel + int(delta)
        if nova_qtd < 0:
            raise ValueError("Estoque insuficiente para a operação")
        self.conn.execute(
            "UPDATE produtos SET quantidade_disponivel=? WHERE id=?",
            (nova_qtd, int(produto_id)),
        )


class RepositorioVendaSQL:
    """Repositório relacional de Vendas (SQLite)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def inserir(self, venda: Venda, *, preco_unitario: float | None = None) -> Venda:
        q = (
            "INSERT INTO vendas (produto_id, quantidade, data_venda, preco_unitario) "
            "VALUES (?, ?, ?, ?)"
        )
        # Persistimos datas como ISO 8601 para compatibilidade
        dt = venda.data_venda.isoformat()
        cur = self.conn.execute(
            q,
            (
                int(venda.produto_id),
                int(venda.quantidade),
                dt,
                None if preco_unitario is None else float(preco_unitario),
            ),
        )
        venda.id = int(cur.lastrowid)
        return venda

    def listar(self) -> List[Venda]:
        q = (
            "SELECT id, produto_id, quantidade, data_venda FROM vendas "
            "ORDER BY datetime(data_venda) DESC, id DESC"
        )
        cur = self.conn.execute(q)
        vendas: List[Venda] = []
        for r in cur.fetchall():
            vendas.append(
                Venda(
                    id=int(r["id"]),
                    produto_id=int(r["produto_id"]),
                    quantidade=int(r["quantidade"]),
                    data_venda=datetime.fromisoformat(r["data_venda"]),
                )
            )
        return vendas

    def listar_por_produto(self, produto_id: int) -> List[Venda]:
        q = (
            "SELECT id, produto_id, quantidade, data_venda FROM vendas "
            "WHERE produto_id=? ORDER BY datetime(data_venda) DESC, id DESC"
        )
        cur = self.conn.execute(q, (int(produto_id),))
        vendas: List[Venda] = []
        for r in cur.fetchall():
            vendas.append(
                Venda(
                    id=int(r["id"]),
                    produto_id=int(r["produto_id"]),
                    quantidade=int(r["quantidade"]),
                    data_venda=datetime.fromisoformat(r["data_venda"]),
                )
            )
        return vendas
