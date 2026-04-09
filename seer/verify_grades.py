
import pandas as pd
import unicodedata
import os
import argparse

# --- CONFIGURAÇÃO ---
# Nomes das colunas esperadas (ajuste conforme necessário)
COL_NOME_PLANILHA = 'Nome'  # Coluna de nome na Planilha de Controle
COL_NOTA_PLANILHA = 'Nota Final'  # Coluna de nota na Planilha de Controle
COL_NOME_AVAMEC = 'Nome'    # Coluna de nome no export do AVAMEC
COL_NOTA_AVAMEC = 'Nota'    # Coluna de nota no export do AVAMEC

# Tolerância para diferença de notas (para ignorar arredondamentos pequenos)
TOLERANCIA = 0.05 
# --------------------

def normalize_name(name):
    """Normaliza o nome para comparação: minúsculas, remove acentos e espaços extras."""
    if not isinstance(name, str):
        return str(name)
    name = name.lower().strip()
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return name

def verify_grades(planilha_path, avamec_path):
    print(f"Lendo planilha de controle: {planilha_path}")
    print(f"Lendo export do AVAMEC: {avamec_path}")

    # Carregar arquivos (tenta detectar se é CSV ou Excel)
    try:
        if planilha_path.endswith('.csv'):
            df_planilha = pd.read_csv(planilha_path)
        else:
            df_planilha = pd.read_excel(planilha_path)
            
        if avamec_path.endswith('.csv'):
            df_avamec = pd.read_csv(avamec_path)
        else:
            df_avamec = pd.read_excel(avamec_path)
    except Exception as e:
        print(f"Erro ao ler arquivos: {e}")
        return

    # Verificar colunas
    if COL_NOME_PLANILHA not in df_planilha.columns or COL_NOTA_PLANILHA not in df_planilha.columns:
        print(f"ERRO: Colunas não encontradas na Planilha de Controle. Esperado: '{COL_NOME_PLANILHA}', '{COL_NOTA_PLANILHA}'")
        print(f"Colunas encontradas: {df_planilha.columns.tolist()}")
        return

    if COL_NOME_AVAMEC not in df_avamec.columns or COL_NOTA_AVAMEC not in df_avamec.columns:
        print(f"ERRO: Colunas não encontradas no AVAMEC. Esperado: '{COL_NOME_AVAMEC}', '{COL_NOTA_AVAMEC}'")
        print(f"Colunas encontradas: {df_avamec.columns.tolist()}")
        return

    # Normalizar nomes para chave de junção
    df_planilha['nome_norm'] = df_planilha[COL_NOME_PLANILHA].apply(normalize_name)
    df_avamec['nome_norm'] = df_avamec[COL_NOME_AVAMEC].apply(normalize_name)

    # Converter notas para numérico
    df_planilha[COL_NOTA_PLANILHA] = pd.to_numeric(df_planilha[COL_NOTA_PLANILHA], errors='coerce').fillna(0)
    df_avamec[COL_NOTA_AVAMEC] = pd.to_numeric(df_avamec[COL_NOTA_AVAMEC], errors='coerce').fillna(0)

    # Realizar o Merge (Join)
    merged = pd.merge(df_planilha, df_avamec, on='nome_norm', how='outer', suffixes=('_planilha', '_avamec'))

    divergencias = []

    # Analisar cada linha
    for index, row in merged.iterrows():
        nome = row[COL_NOME_PLANILHA] if pd.notna(row[COL_NOME_PLANILHA]) else row[COL_NOME_AVAMEC]
        nota_planilha = row[COL_NOTA_PLANILHA]
        nota_avamec = row[COL_NOTA_AVAMEC]
        
        status = ""
        
        if pd.isna(row[COL_NOME_PLANILHA]):
            status = "Faltando na Planilha de Controle"
        elif pd.isna(row[COL_NOME_AVAMEC]):
            status = "Faltando no AVAMEC"
        elif abs(nota_planilha - nota_avamec) > TOLERANCIA:
            status = f"Divergência de Nota (Planilha: {nota_planilha} vs AVAMEC: {nota_avamec})"
        
        if status:
            divergencias.append({
                'Nome': nome,
                'Status': status,
                'Nota Planilha': nota_planilha,
                'Nota AVAMEC': nota_avamec
            })

    # Gerar Relatório
    if divergencias:
        df_div = pd.DataFrame(divergencias)
        output_file = 'relatorio_divergencias.csv'
        df_div.to_csv(output_file, index=False)
        print(f"\nVerificação concluída. {len(divergencias)} divergências encontradas.")
        print(f"Detalhes salvos em: {output_file}")
        print("\n--- Resumo das primeiras 5 divergências ---")
        print(df_div.head().to_string(index=False))
    else:
        print("\nVerificação concluída. Nenhuma divergência encontrada! Tudo correto.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verificar notas entre planilha de controle e AVAMEC')
    parser.add_argument('planilha', help='Caminho para arquivo da Planilha de Controle (Excel/CSV)')
    parser.add_argument('avamec', help='Caminho para arquivo exportado do AVAMEC (Excel/CSV)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.planilha):
        print(f"Arquivo não encontrado: {args.planilha}")
    elif not os.path.exists(args.avamec):
        print(f"Arquivo não encontrado: {args.avamec}")
    else:
        verify_grades(args.planilha, args.avamec)
