# Guia de Verificação de Notas - Turma B

Este guia descreve como utilizar a ferramenta automática para verificar discrepâncias de notas entre a sua Planilha de Controle e o AVAMEC.

## Pré-requisitos

- Python instalado.
- Biblioteca `pandas` instalada.
- Arquivo da Planilha de Controle (formato Excel ou CSV).
- Arquivo exportado do AVAMEC (formato Excel ou CSV).

## Preparação dos Arquivos

Certifique-se de que os arquivos tenham as seguintes colunas (o script tentará identificar automaticamente, mas manter o padrão ajuda):

1.  **Planilha de Controle**: Deve ter uma coluna `Nome` e uma coluna `Nota Final`.
2.  **AVAMEC**: Deve ter uma coluna `Nome` e uma coluna `Nota`.

> **Nota**: Se os nomes das colunas forem diferentes, você pode editar as variáveis `COL_NOME_PLANILHA`, `COL_NOTA_PLANILHA`, etc., no início do arquivo `verify_grades.py`.

## Como Executar

1.  Abra o terminal.
2.  Navegue até a pasta onde está o script e os arquivos.
3.  Execute o comando:

```bash
python3 verify_grades.py "caminho/para/planilha_controle.xlsx" "caminho/para/export_avamec.csv"
```

Exemplo:
```bash
python3 verify_grades.py notas_turma_b.xlsx notas_avamec.csv
```

## Interpretando os Resultados

O script irá gerar no terminal um resumo e criar um arquivo `relatorio_divergencias.csv` se encontrar inconsistências.

Os tipos de divergências reportadas são:
- **Faltando na Planilha de Controle**: O aluno está no AVAMEC mas não na sua planilha.
- **Faltando no AVAMEC**: O aluno está na sua planilha mas não no AVAMEC.
- **Divergência de Nota**: As notas são diferentes (considerando uma tolerância de 0.05 pontos).

## Próximos Passos

1.  Abra o arquivo `relatorio_divergencias.csv`.
2.  Para cada aluno listado, verifique manualmente no AVAMEC.
3.  Se a nota foi atualizada recentemente (última atualização/quinzena), corrija na sua planilha.
4.  Rode o script novamente para garantir que todas as divergências foram sanadas.
