from infra.forja_persistencia import ForjaDePersistencia
from services.servicos import OrquestradorDeFluxoComercial
from services import relatorios as rel
from api.main import app
from fastapi.testclient import TestClient

f = ForjaDePersistencia()
f.criar_esquema()
with f.conectar() as conn:
    svc = OrquestradorDeFluxoComercial(conn)
    prods = svc.listar_produtos()
    if not prods:
        p = svc.cadastrar_produto("CI Produto", "Smoke", 3, 10.0)
        svc.registrar_venda(p.id, 1)
    receita = rel.receita_total(conn)
    assert receita >= 10.0

c = TestClient(app)
assert c.get("/produtos").status_code == 200
print("ruff+black ok; smoke ok")
