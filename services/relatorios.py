from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Tuple


def _intervalo_sql(start: Optional[str], end: Optional[str]) -> Tuple[str, list]:
    conds = []
    params: list[Any] = []
    if start:
        conds.append("datetime(data_venda) >= datetime(?)")
        params.append(start)
    if end:
        conds.append("datetime(data_venda) <= datetime(?)")
        params.append(end)
    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    return where, params


def receita_total(
    conn: sqlite3.Connection, *, start: Optional[str] = None, end: Optional[str] = None
) -> float:
    where, params = _intervalo_sql(start, end)
    q = f"""
        SELECT SUM(v.quantidade * COALESCE(v.preco_unitario, p.preco)) AS receita
        FROM vendas v
        JOIN produtos p ON p.id = v.produto_id
        {where}
    """
    row = conn.execute(q, params).fetchone()
    return float(row[0]) if row and row[0] is not None else 0.0


def receita_por_dia(
    conn: sqlite3.Connection, *, start: Optional[str] = None, end: Optional[str] = None
) -> List[Dict[str, Any]]:
    where, params = _intervalo_sql(start, end)
    q = f"""
        SELECT DATE(v.data_venda) AS dia,
               SUM(v.quantidade * COALESCE(v.preco_unitario, p.preco)) AS receita
        FROM vendas v
        JOIN produtos p ON p.id = v.produto_id
        {where}
        GROUP BY dia
        ORDER BY dia ASC
    """
    return [
        {
            "dia": r["dia"],
            "receita": float(r["receita"]) if r["receita"] is not None else 0.0,
        }
        for r in conn.execute(q, params).fetchall()
    ]


def ranking_produtos(
    conn: sqlite3.Connection,
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    where, params = _intervalo_sql(start, end)
    q = f"""
        SELECT p.id AS produto_id, p.nome,
               SUM(v.quantidade) AS total_vendido,
               SUM(v.quantidade * COALESCE(v.preco_unitario, p.preco)) AS receita
        FROM vendas v
        JOIN produtos p ON p.id = v.produto_id
        {where}
        GROUP BY p.id, p.nome
        ORDER BY receita DESC NULLS LAST, total_vendido DESC
        LIMIT ?
    """
    params_l = [*params, int(limit)]
    return [
        {
            "produto_id": int(r["produto_id"]),
            "nome": r["nome"],
            "total_vendido": (
                int(r["total_vendido"]) if r["total_vendido"] is not None else 0
            ),
            "receita": float(r["receita"]) if r["receita"] is not None else 0.0,
        }
        for r in conn.execute(q, params_l).fetchall()
    ]


def giro_estoque(conn: sqlite3.Connection, *, dias: int = 30) -> List[Dict[str, Any]]:
    # Média diária vendida em N dias e cobertura em dias
    q = """
        WITH periodo AS (
            SELECT DATE('now', ? || ' days') AS inicio, DATE('now') AS fim
        ),
        vendas_periodo AS (
            SELECT v.produto_id, SUM(v.quantidade) AS total_vendido
            FROM vendas v, periodo p
            WHERE DATE(v.data_venda) BETWEEN p.inicio AND p.fim
            GROUP BY v.produto_id
        )
        SELECT p.id AS produto_id,
               p.nome,
               p.quantidade_disponivel AS estoque_atual,
               COALESCE(vp.total_vendido, 0) AS total_vendido_periodo,
               (COALESCE(vp.total_vendido, 0) * 1.0 / NULLIF(ABS(?), 0)) AS media_diaria
        FROM produtos p
        LEFT JOIN vendas_periodo vp ON vp.produto_id = p.id
        ORDER BY p.nome ASC
    """
    params = (-abs(dias) * -1, dias)  # truque para DATE('now', '-30 days') via concat
    rows = conn.execute(q, params).fetchall()
    resultado: List[Dict[str, Any]] = []
    for r in rows:
        media = float(r["media_diaria"]) if r["media_diaria"] is not None else 0.0
        estoque = int(r["estoque_atual"])
        cobertura = (estoque / media) if media > 0 else None
        resultado.append(
            {
                "produto_id": int(r["produto_id"]),
                "nome": r["nome"],
                "estoque_atual": estoque,
                "total_vendido_periodo": int(r["total_vendido_periodo"]),
                "media_diaria_vendida": round(media, 4),
                "cobertura_dias": (
                    round(cobertura, 2) if cobertura is not None else None
                ),
            }
        )
    return resultado
