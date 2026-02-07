# Núcleo Comercial de Dados — Frontend & API

O Núcleo Comercial de Dados oferece uma experiência web moderna para gestão de produtos, vendas e indicadores comerciais. O frontend entrega um painel responsivo, com acessibilidade e fluxo orientado a operação, enquanto a API em FastAPI mantém regras de negócio consistentes.

## Visão geral do frontend
A interface web foi desenhada para equipes que precisam acompanhar estoque, receita e performance em um único painel. O fluxo prioriza leitura rápida, ações de cadastro e relatórios críticos.

**Público-alvo**
- Times comerciais e operações de pequenas empresas.
- Projetos educacionais que precisam de um painel completo para dados de vendas.

## Stack e tecnologias
- HTML, CSS e JavaScript moderno (frontend estático)
- FastAPI (API HTTP)
- SQLite (persistência local)

## Funcionalidades principais
- Dashboard com métricas de receita, vendas e estoque.
- Cadastro rápido, atualização e ajuste de produtos.
- Registro de vendas e histórico recente.
- Relatórios analíticos (ranking, giro, estoque baixo).
- Alternância de tema claro/escuro.

## Estrutura do projeto
```
frontend/            # Interface web estática
api/                 # API HTTP (FastAPI)
domain/              # Entidades de domínio
infra/               # Persistência, schema e repositórios
services/            # Regras de negócio e relatórios
tests/               # Testes automatizados
main.py              # CLI principal
```

## Setup e execução

### 1) Ambiente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Executar a aplicação web
```bash
uvicorn api.main:app --reload
```

Abra a UI em: http://127.0.0.1:8000/

### 3) Executar a CLI (opcional)
```bash
python main.py
```

## Boas práticas adotadas
- Design responsivo com tokens e hierarquia visual consistente.
- Acessibilidade com labels, contraste e foco em legibilidade.
- Separação clara entre UI, domínio e persistência.
- Transações atômicas para operações de estoque e venda.

## Melhorias futuras
- Autenticação e perfis de usuário.
- Exportação de relatórios em CSV/Excel.
- Dashboard com gráficos e filtros avançados.
- Cache para relatórios de alta demanda.

## Status do CI
[![CI](https://github.com/matheussiqueirahub/nucleo-comercial-dados/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/matheussiqueirahub/nucleo-comercial-dados/actions/workflows/ci.yml)

Autoria: Matheus Siqueira  
Website: https://www.matheussiqueira.dev/
