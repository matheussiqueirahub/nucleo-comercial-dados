import pytest

from api.main import app
from infra.forja_persistencia import ForjaDePersistencia
from services import relatorios as rel
from services.servicos import OrquestradorDeFluxoComercial

def test_smoke_flow():
    # Banco local (cria data/) - garantir que diretório data existe se necessario
    # A classe ForjaDePersistencia provavelmente lida com isso se for sqlite
    
    f = ForjaDePersistencia()
    f.criar_esquema()
    conn = f.conectar()
    try:
        svc = OrquestradorDeFluxoComercial(conn)
        prods = svc.listar_produtos()
        if not prods:
            p = svc.cadastrar_produto('CI Produto', 'Smoke', 3, 10.0)
            svc.registrar_venda(p.id, 1)
        receita = rel.receita_total(conn)
        assert receita >= 10.0, f"Receita esperada >= 10.0, mas obteve {receita}"
    finally:
        conn.close()

def test_api_status():
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    c = TestClient(app)
    r = c.get('/produtos')
    assert r.status_code == 200, r.text
