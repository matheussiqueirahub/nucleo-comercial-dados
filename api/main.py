from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, PositiveInt

from infra.forja_persistencia import ForjaDePersistencia
from services.servicos import OrquestradorDeFluxoComercial
from services import relatorios as rel


app = FastAPI(title="Núcleo Comercial de Dados", version="1.0.0")
forja = ForjaDePersistencia()
forja.criar_esquema()
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def get_conn():
    conn = forja.conectar(check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def get_service(conn=Depends(get_conn)):
    return OrquestradorDeFluxoComercial(conn)


def _map_service_error(exc: Exception) -> HTTPException:
    message = str(exc)
    if "inexistente" in message:
        return HTTPException(status_code=404, detail=message)
    return HTTPException(status_code=400, detail=message)


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
    ativo: bool


class ProdutoDetalheOut(ProdutoOut):
    pass


class VendaIn(BaseModel):
    produto_id: int
    quantidade: PositiveInt


class VendaOut(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    data_venda: str


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1)
    descricao: Optional[str] = None
    quantidade_disponivel: Optional[int] = Field(None, ge=0)
    preco: Optional[float] = Field(None, ge=0)


class AjusteEstoqueIn(BaseModel):
    delta: int


@app.get("/produtos", response_model=list[ProdutoOut])
def listar_produtos(
    q: Optional[str] = None,
    incluir_inativos: bool = False,
    svc: OrquestradorDeFluxoComercial = Depends(get_service),
):
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "descricao": p.descricao,
            "quantidade_disponivel": p.quantidade_disponivel,
            "preco": p.preco,
            "ativo": p.ativo,
        }
        for p in svc.listar_produtos(
            consulta=q, include_inativos=incluir_inativos
        )
    ]


@app.get("/")
def frontend_home():
    return FileResponse(FRONTEND_DIR / "index.html")


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
        "ativo": prod.ativo,
    }


@app.get("/produtos/{produto_id}", response_model=ProdutoDetalheOut)
def obter_produto(
    produto_id: int, svc: OrquestradorDeFluxoComercial = Depends(get_service)
):
    try:
        prod = svc.obter_produto(produto_id, include_inativos=True)
    except Exception as e:
        raise _map_service_error(e)
    return {
        "id": prod.id,
        "nome": prod.nome,
        "descricao": prod.descricao,
        "quantidade_disponivel": prod.quantidade_disponivel,
        "preco": prod.preco,
        "ativo": prod.ativo,
    }


@app.patch("/produtos/{produto_id}", response_model=ProdutoDetalheOut)
def atualizar_produto(
    produto_id: int,
    payload: ProdutoUpdate,
    svc: OrquestradorDeFluxoComercial = Depends(get_service),
):
    try:
        prod = svc.atualizar_produto(
            produto_id,
            nome=payload.nome,
            descricao=payload.descricao,
            quantidade_disponivel=payload.quantidade_disponivel,
            preco=payload.preco,
        )
    except Exception as e:
        raise _map_service_error(e)
    return {
        "id": prod.id,
        "nome": prod.nome,
        "descricao": prod.descricao,
        "quantidade_disponivel": prod.quantidade_disponivel,
        "preco": prod.preco,
        "ativo": prod.ativo,
    }


@app.post("/produtos/{produto_id}/estoque", status_code=204)
def ajustar_estoque(
    produto_id: int,
    payload: AjusteEstoqueIn,
    svc: OrquestradorDeFluxoComercial = Depends(get_service),
):
    try:
        svc.ajustar_estoque(produto_id, payload.delta)
    except Exception as e:
        raise _map_service_error(e)


@app.delete("/produtos/{produto_id}", status_code=204)
def inativar_produto(
    produto_id: int, svc: OrquestradorDeFluxoComercial = Depends(get_service)
):
    try:
        svc.inativar_produto(produto_id)
    except Exception as e:
        raise _map_service_error(e)


@app.get("/vendas", response_model=list[VendaOut])
def listar_vendas(
    produto_id: Optional[int] = None,
    svc: OrquestradorDeFluxoComercial = Depends(get_service),
):
    vendas = (
        svc.listar_vendas_por_produto(produto_id)
        if produto_id is not None
        else svc.listar_vendas()
    )
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
        raise _map_service_error(e)


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


@app.get("/relatorios/estoque_baixo")
def rel_estoque_baixo(limite: int = 5, conn=Depends(get_conn)):
    return rel.estoque_baixo(conn, limite=limite)
