# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

O formato segue uma adaptação do Keep a Changelog, e as versões usam SemVer.

## [0.1.0] - 2025-08-31

- Primeira versão pública do Núcleo Comercial de Dados
- Persistência em SQLite com DDL automática (`produtos`, `vendas` + índices)
- Entidades de domínio: `Produto`, `Venda` (POO com validações)
- Repositórios SQL para Produtos e Vendas (consultas parametrizadas)
- Serviços transacionais para cadastro e registro de vendas (baixa de estoque atômica)
- Relatórios: receita total/por dia, ranking de produtos e giro de estoque
- API HTTP (FastAPI): `/produtos`, `/vendas`, `/relatorios/*`
- CLI de demonstração para operações básicas
- CI (lint + format + smoke) e Release automático por tag

[0.1.0]: https://github.com/matheussiqueirahub/nucleo-comercial-dados/releases/tag/v0.1.0

