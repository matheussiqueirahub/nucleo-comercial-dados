# Sistema Comercial – Persistência de Produtos e Vendas

Este projeto implementa a persistência de dados para Produtos e Vendas usando SQLite, com uma arquitetura simples baseada em POO, Repositórios e Serviços de Negócio. Os nomes foram escolhidos para refletir boas práticas da área de dados.

- Banco: SQLite (arquivo local `data/mercado.sqlite3`)
- Tabelas mínimas: `produtos`, `vendas`
- Extras: controle transacional simples e validações de estoque

## Requisitos

- Python 3.9+
- Sem dependências externas (usa apenas a biblioteca padrão)

## Como executar

1. Execute o CLI:

```
python main.py
```

2. Opções disponíveis (menu interativo):
- Cadastrar produto
- Listar produtos
- Registrar venda
- Listar vendas
- Sair

O banco e o esquema são criados automaticamente no primeiro uso.

## Estrutura

- `infra/forja_persistencia.py`: conexão e DDL (criação de tabelas)
- `domain/modelos.py`: classes de domínio (`Produto`, `Venda`)
- `infra/repositorios.py`: repositórios SQL (Produto/Venda)
- `services/servicos.py`: regras de negócio (estoque e vendas)
- `main.py`: CLI de demonstração

## Observações de projeto

- Camada de persistência isolada: `RepositorioProdutoSQL` e `RepositorioVendaSQL` usam consultas parametrizadas para evitar SQL injection.
- Transações: operações de venda usam uma única transação para garantir consistência entre baixa de estoque e registro de venda.
- Índices: índices criados para acelerar pesquisas por nome de produto e data de venda.
- Tipos e validações: uso de `dataclasses` e validações de domínio nas entidades e serviços.

## API HTTP (FastAPI)

Opcionalmente, você pode expor uma API:

1. Instale dependências:

```
pip install fastapi uvicorn
```

2. Rode o servidor:

```
uvicorn api.main:app --reload
```

3. Explore a documentação interativa em:
- Swagger UI: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

### Endpoints principais
- `GET /produtos` | `POST /produtos`
- `GET /vendas` | `POST /vendas`
- `GET /relatorios/receita?start=&end=`
- `GET /relatorios/receita_por_dia?start=&end=`
- `GET /relatorios/ranking?start=&end=&limit=`
- `GET /relatorios/giro?dias=30`

Observação: as datas `start/end` aceitam formatos ISO como `2025-01-01`.

## Relatórios inclusos

- Receita total com intervalo opcional (usa preço no momento da venda)
- Receita agregada por dia (série temporal)
- Ranking de produtos por receita e volume
- Giro de estoque: média diária vendida (N dias) e cobertura em dias
