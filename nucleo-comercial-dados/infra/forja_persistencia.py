from __future__ import annotations

import os
import sqlite3
from pathlib import Path


class ForjaDePersistencia:
    """Responsável por prover conexões e materializar o esquema.

    Usa SQLite em arquivo local e ativa chaves estrangeiras.
    """

    def __init__(self, caminho_db: str | None = None) -> None:
        base = Path("data")
        base.mkdir(parents=True, exist_ok=True)
        self._caminho = Path(caminho_db) if caminho_db else base / "mercado.sqlite3"

    @property
    def caminho(self) -> Path:
        return self._caminho

    def conectar(self, *, check_same_thread: bool = True) -> sqlite3.Connection:
        conn = sqlite3.connect(self._caminho, check_same_thread=check_same_thread)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def criar_esquema(self) -> None:
        conn = self.conectar()
        try:
            ddl_produtos = """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT DEFAULT '',
                quantidade_disponivel INTEGER NOT NULL CHECK (quantidade_disponivel >= 0),
                preco REAL NOT NULL CHECK (preco >= 0)
            );
            """

            ddl_vendas = """
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                data_venda TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            );
            """

            idx = [
                "CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome);",
                "CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda);",
                "CREATE INDEX IF NOT EXISTS idx_vendas_produto ON vendas(produto_id);",
            ]

            with conn:
                conn.executescript(ddl_produtos)
                conn.executescript(ddl_vendas)
                for stmt in idx:
                    conn.execute(stmt)
                # Migração leve: garantir coluna de preço na venda para relatórios fiéis
                cols = conn.execute("PRAGMA table_info('vendas');").fetchall()
                nomes = {c[1] for c in cols}
                if "preco_unitario" not in nomes:
                    conn.execute("ALTER TABLE vendas ADD COLUMN preco_unitario REAL;")
        finally:
            conn.close()
