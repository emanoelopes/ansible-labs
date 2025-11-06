#!/bin/bash
# Script para configurar ambiente virtual e instalar dependências

set -e

echo "=== Configurando ambiente virtual para Ansible Labs ==="

# Criar venv se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar venv
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "=== Ambiente configurado com sucesso! ==="
echo ""
echo "Para usar o ambiente virtual:"
echo "  source venv/bin/activate"
echo ""
echo "Para executar as interfaces:"
echo "  python run_web.py    # Interface Web"
echo "  python run_tui.py    # Interface TUI"
echo ""

