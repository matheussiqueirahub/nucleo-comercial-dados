from __future__ import annotations

from typing import Callable

from infra.forja_persistencia import ForjaDePersistencia
from services.servicos import OrquestradorDeFluxoComercial


def _input_float(msg: str) -> float:
    while True:
        try:
            return float(input(msg).replace(",", "."))
        except ValueError:
            print("Valor inválido. Tente novamente.")


def _input_int(msg: str) -> int:
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Valor inválido. Tente novamente.")


def menu() -> None:
    print("\n=== Console Comercial · Cohorte de Dados ===")
    print("1) Cadastrar produto")
    print("2) Listar produtos")
    print("3) Registrar venda")
    print("4) Listar vendas")
    print("0) Sair")


def main() -> None:
    forja = ForjaDePersistencia()
    # Garante que o esquema exista
    forja.criar_esquema()
    conn = forja.conectar()
    try:
        svc = OrquestradorDeFluxoComercial(conn)

        acoes: dict[str, Callable[[], None]] = {}

        def acao_cadastrar() -> None:
            print("\n— Cadastro de Produto —")
            nome = input("Nome: ").strip()
            descricao = input("Descrição: ")
            quantidade = _input_int("Quantidade inicial: ")
            preco = _input_float("Preço (ex.: 19.90): ")
            try:
                prod = svc.cadastrar_produto(nome, descricao, quantidade, preco)
                print(f"Produto cadastrado (ID {prod.id})")
            except Exception as e:
                print(f"Erro ao cadastrar: {e}")

        def acao_listar_produtos() -> None:
            print("\n— Catálogo de Produtos —")
            produtos = svc.listar_produtos()
            if not produtos:
                print("(vazio)")
                return
            for p in produtos:
                print(
                    f"[{p.id}] {p.nome} | Estoque: {p.quantidade_disponivel} | Preço: R$ {p.preco:.2f}\n    {p.descricao}"
                )

        def acao_registrar_venda() -> None:
            print("\n— Registrar Venda —")
            produto_id = _input_int("ID do produto: ")
            quantidade = _input_int("Quantidade vendida: ")
            try:
                venda = svc.registrar_venda(produto_id, quantidade)
                print(f"Venda registrada (ID {venda.id})")
            except Exception as e:
                print(f"Erro ao vender: {e}")

        def acao_listar_vendas() -> None:
            print("\n— Vendas —")
            vendas = svc.listar_vendas()
            if not vendas:
                print("(vazio)")
                return
            for v in vendas:
                print(
                    f"[{v.id}] Produto {v.produto_id} | Qtde: {v.quantidade} | Data: {v.data_venda.isoformat()}"
                )

        acoes = {
            "1": acao_cadastrar,
            "2": acao_listar_produtos,
            "3": acao_registrar_venda,
            "4": acao_listar_vendas,
        }

        while True:
            menu()
            opcao = input("> ").strip()
            if opcao == "0":
                print("Tchau 👋")
                break
            func = acoes.get(opcao)
            if func:
                func()
            else:
                print("Opção inválida.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
