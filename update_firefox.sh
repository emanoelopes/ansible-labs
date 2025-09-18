#!/bin/bash

# Script para atualizar Firefox usando Ansible
# Uso: ./update_firefox.sh [target_hosts] [os_type]

TARGET_HOSTS=${1:-"all"}
OS_TYPE=${2:-"linux"}

echo "=== Atualizando Firefox ==="
echo "Hosts alvo: $TARGET_HOSTS"
echo "Sistema operacional: $OS_TYPE"
echo "================================"

if [ "$OS_TYPE" = "windows" ]; then
    echo "Executando playbook para Windows..."
    ansible-playbook firefox_update_windows.yaml -e "target_hosts=$TARGET_HOSTS" -k
elif [ "$OS_TYPE" = "linux" ]; then
    echo "Executando playbook para Linux..."
    ansible-playbook firefox_update.yaml -e "target_hosts=$TARGET_HOSTS" -k
elif [ "$OS_TYPE" = "mac" ]; then
    echo "Executando playbook para macOS..."
    ansible-playbook firefox_update_mac.yaml -e "target_hosts=$TARGET_HOSTS" -k
else
    echo "Sistema operacional não suportado. Use 'linux', 'windows' ou 'mac'"
    exit 1
fi

echo "================================"
echo "Atualização do Firefox concluída!"
