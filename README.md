# FLEXT DB Oracle

Biblioteca de acesso Oracle para leitura, escrita e suporte de persistencia em pipelines de dados.

Descricao oficial atual: "FLEXT DB Oracle - Enterprise Oracle Database Operations Library".

## O que este projeto entrega

- Centraliza conectividade Oracle para servicos e conectores.
- Padroniza operacoes SQL para carga e consulta.
- Apoia fluxo de dados com destino/origem Oracle no ecossistema.

## Contexto operacional

- Entrada: comandos de leitura/escrita Oracle.
- Saida: dados persistidos ou retornados para pipeline.
- Dependencias: credenciais Oracle e modulos consumidores (tap/target/dbt).

## Estado atual e risco de adocao

- Qualidade: **Alpha**
- Uso recomendado: **Nao produtivo**
- Nivel de estabilidade: em maturacao funcional e tecnica, sujeito a mudancas de contrato sem garantia de retrocompatibilidade.

## Diretriz para uso nesta fase

Aplicar este projeto somente em desenvolvimento, prova de conceito e homologacao controlada, com expectativa de ajustes frequentes ate maturidade de release.
