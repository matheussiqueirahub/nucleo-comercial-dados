from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field, PositiveInt

from infra.forja_persistencia import ForjaDePersistencia
from services.servicos import OrquestradorDeFluxoComercial
from services import relatorios as rel


app = FastAPI(title="Núcleo Comercial de Dados", version="1.0.0")
forja = ForjaDePersistencia()
forja.criar_esquema()


def get_conn():
    conn = forja.conectar(check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def get_service(conn=Depends(get_conn)):
    return OrquestradorDeFluxoComercial(conn)


class ProdutoIn(BaseModel):
    nome: str = Field(..., min_length=1)
    descricao: str = ""
    quantidade_disponivel: int = Field(0, ge=0)
    preco: float = Field(..., ge=0)


class ProdutoOut(BaseModel):
    id: int
    nome: str
    descricao: str
    quantidade_disponivel: int
    preco: float


class VendaIn(BaseModel):
    produto_id: int
    quantidade: PositiveInt


class VendaOut(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    data_venda: str


@app.get("/produtos", response_model=list[ProdutoOut])
def listar_produtos(svc: OrquestradorDeFluxoComercial = Depends(get_service)):
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "descricao": p.descricao,
            "quantidade_disponivel": p.quantidade_disponivel,
            "preco": p.preco,
        }
        for p in svc.listar_produtos()
    ]


@app.post("/produtos", response_model=ProdutoOut, status_code=201)
def criar_produto(
    payload: ProdutoIn, svc: OrquestradorDeFluxoComercial = Depends(get_service)
):
    prod = svc.cadastrar_produto(
        nome=payload.nome,
        descricao=payload.descricao,
        quantidade=payload.quantidade_disponivel,
        preco=payload.preco,
    )
    return {
        "id": prod.id,
        "nome": prod.nome,
        "descricao": prod.descricao,
        "quantidade_disponivel": prod.quantidade_disponivel,
        "preco": prod.preco,
    }


@app.get("/vendas", response_model=list[VendaOut])
def listar_vendas(svc: OrquestradorDeFluxoComercial = Depends(get_service)):
    vendas = svc.listar_vendas()
    return [
        {
            "id": v.id,
            "produto_id": v.produto_id,
            "quantidade": v.quantidade,
            "data_venda": v.data_venda.isoformat(),
        }
        for v in vendas
    ]


@app.post("/vendas", response_model=VendaOut, status_code=201)
def criar_venda(
    payload: VendaIn, svc: OrquestradorDeFluxoComercial = Depends(get_service)
):
    try:
        v = svc.registrar_venda(payload.produto_id, payload.quantidade)
        return {
            "id": v.id,
            "produto_id": v.produto_id,
            "quantidade": v.quantidade,
            "data_venda": v.data_venda.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ReceitaTotalOut(BaseModel):
    receita: float


@app.get("/relatorios/receita", response_model=ReceitaTotalOut)
def rel_receita_total(
    start: Optional[str] = None, end: Optional[str] = None, conn=Depends(get_conn)
):
    return {"receita": rel.receita_total(conn, start=start, end=end)}


@app.get("/relatorios/receita_por_dia")
def rel_receita_por_dia(
    start: Optional[str] = None, end: Optional[str] = None, conn=Depends(get_conn)
):
    return rel.receita_por_dia(conn, start=start, end=end)


@app.get("/relatorios/ranking")
def rel_ranking_produtos(
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 10,
    conn=Depends(get_conn),
):
    return rel.ranking_produtos(conn, start=start, end=end, limit=limit)


@app.get("/relatorios/giro")
def rel_giro(dias: int = 30, conn=Depends(get_conn)):
    return rel.giro_estoque(conn, dias=dias)
