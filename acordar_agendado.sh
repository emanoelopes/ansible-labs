#!/bin/bash
# Wake-on-LAN diário às 7:55 para todos os labs (chamado pelo cron).
# Log em logs/acordar-AAAA-MM-DD.log. Instalado com 'crontab -e'.
cd /home/emanoel/ansible-labs || exit 1
export ANSIBLE_VAULT_PASSWORD_FILE=$HOME/.ansible_vault_pass
for lab in lab1 lab2 lab3 lab4 lab5 lab6; do
  echo "=== $lab $(date '+%F %T') ==="
  ansible-playbook acordar.yml -e "alvo=$lab"
done >> "logs/acordar-$(date +%F).log" 2>&1
