from __future__ import annotations

from typing import Callable

from infra.forja_persistencia import ForjaDePersistencia
from services import relatorios as rel
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


def _input_int_optional(msg: str) -> int | None:
    valor = input(msg).strip()
    if not valor:
        return None
    try:
        return int(valor)
    except ValueError:
        print("Valor inválido. Tente novamente.")
        return _input_int_optional(msg)


def _input_float_optional(msg: str) -> float | None:
    valor = input(msg).strip()
    if not valor:
        return None
    try:
        return float(valor.replace(",", "."))
    except ValueError:
        print("Valor inválido. Tente novamente.")
        return _input_float_optional(msg)


def menu() -> None:
    print("\n=== Console Comercial · Núcleo de Dados ===")
    print("1) Cadastrar produto")
    print("2) Listar produtos")
    print("3) Registrar venda")
    print("4) Listar vendas")
    print("5) Ajustar estoque")
    print("6) Atualizar produto")
    print("7) Relatórios")
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
            termo = input("Filtro por nome (enter para listar todos): ").strip()
            produtos = svc.listar_produtos(consulta=termo if termo else None)
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
            produto_id = _input_int_optional("Filtrar por produto (enter para todos): ")
            vendas = (
                svc.listar_vendas_por_produto(produto_id)
                if produto_id
                else svc.listar_vendas()
            )
            if not vendas:
                print("(vazio)")
                return
            for v in vendas:
                print(
                    f"[{v.id}] Produto {v.produto_id} | Qtde: {v.quantidade} | Data: {v.data_venda.isoformat()}"
                )

        def acao_ajustar_estoque() -> None:
            print("\n— Ajuste de Estoque —")
            produto_id = _input_int("ID do produto: ")
            delta = _input_int("Delta (ex.: 5 para entrada, -2 para saída): ")
            try:
                svc.ajustar_estoque(produto_id, delta)
                print("Estoque atualizado com sucesso.")
            except Exception as e:
                print(f"Erro ao ajustar estoque: {e}")

        def acao_atualizar_produto() -> None:
            print("\n— Atualizar Produto —")
            produto_id = _input_int("ID do produto: ")
            try:
                atual = svc.obter_produto(produto_id, include_inativos=True)
            except Exception as e:
                print(f"Erro: {e}")
                return
            print(
                f"Atual ({atual.nome}) | Estoque: {atual.quantidade_disponivel} | Preço: R$ {atual.preco:.2f}"
            )
            nome = input("Novo nome (enter para manter): ").strip() or None
            descricao = input("Nova descrição (enter para manter): ").strip()
            descricao = descricao if descricao != "" else None
            quantidade = _input_int_optional("Nova quantidade (enter para manter): ")
            preco = _input_float_optional("Novo preço (enter para manter): ")
            try:
                svc.atualizar_produto(
                    produto_id,
                    nome=nome,
                    descricao=descricao,
                    quantidade_disponivel=quantidade,
                    preco=preco,
                )
                print("Produto atualizado com sucesso.")
            except Exception as e:
                print(f"Erro ao atualizar: {e}")

        def acao_relatorios() -> None:
            print("\n— Relatórios —")
            print("1) Receita total")
            print("2) Receita por dia")
            print("3) Ranking de produtos")
            print("4) Giro de estoque")
            print("5) Estoque baixo")
            opcao = input("> ").strip()
            if opcao == "1":
                receita = relatorios_receita_total()
                print(f"Receita total: R$ {receita:.2f}")
            elif opcao == "2":
                for item in relatorios_receita_por_dia():
                    print(f"{item['dia']}: R$ {item['receita']:.2f}")
            elif opcao == "3":
                for item in relatorios_ranking():
                    print(
                        f"{item['nome']} | Qtde: {item['total_vendido']} | Receita: R$ {item['receita']:.2f}"
                    )
            elif opcao == "4":
                for item in relatorios_giro():
                    cobertura = (
                        f"{item['cobertura_dias']} dias"
                        if item["cobertura_dias"] is not None
                        else "—"
                    )
                    print(
                        f"{item['nome']} | Estoque: {item['estoque_atual']} | Média diária: {item['media_diaria_vendida']} | Cobertura: {cobertura}"
                    )
            elif opcao == "5":
                for item in relatorios_estoque_baixo():
                    print(
                        f"{item['nome']} | Estoque: {item['quantidade_disponivel']} | Preço: R$ {item['preco']:.2f}"
                    )
            else:
                print("Opção inválida.")

        def relatorios_receita_total():
            return rel.receita_total(conn)

        def relatorios_receita_por_dia():
            return rel.receita_por_dia(conn)

        def relatorios_ranking():
            return rel.ranking_produtos(conn)

        def relatorios_giro():
            return rel.giro_estoque(conn)

        def relatorios_estoque_baixo():
            return rel.estoque_baixo(conn)

        acoes = {
            "1": acao_cadastrar,
            "2": acao_listar_produtos,
            "3": acao_registrar_venda,
            "4": acao_listar_vendas,
            "5": acao_ajustar_estoque,
            "6": acao_atualizar_produto,
            "7": acao_relatorios,
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
