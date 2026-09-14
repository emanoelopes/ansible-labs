# Managing Windows and macOS physicals machines hosts with Ansible

This repository contains Ansible playbooks, roles and tasks to manage on-premises Windows 10/11, Linux and macOS machines on computer labs. 

Created to support mantaining daily techinical routines like: 
- Install apps;
- Users management;
- Scheduled tasks management;
- Change power plan on Windows 10;
- Windows updates: drivers, definitions updates etc.
- and much more.

## Operação no dia a dia

**[docs/operacao.md](docs/operacao.md) — o que rodar quando.** Guia por
situação: ligar e desligar laboratório, aplicar o estado declarado,
diagnosticar máquina que não responde, auditoria semanal, inventário,
Wake-on-LAN e as armadilhas que já custaram caro.

Comece por ele. Cada playbook tem no próprio cabeçalho a explicação detalhada
e o histórico das decisões — inclusive dos erros, que estão registrados de
propósito para não se repetirem.

Example:

```shell
$ ansible-playbook site.yaml -e "local=lab4" -k -t apache_netbeans
```
```
ansible-playbook -------  Using a playbook file;
site.yaml --------------  Playbook file;
-e "local=lab4" --------  Especify local variable (lab1..lab6);
-k ---------------------  Ask admin user password;
-t ---------------------  Call a especific tag.
```

Quase tudo hoje passa pelo **estado declarado**, e não por tags avulsas:

```shell
$ export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
$ ansible-playbook estado.yml -e alvo=lab4 --check --diff   # o que mudaria
$ ansible-playbook estado.yml -e alvo=lab4                  # aplica
```

O que cada laboratório deve ter está em `group_vars/<lab>.yml`, e o comum aos
cinco em `group_vars/windows.yml`.

# History

This project started 2022 after 3 years Alex's Ramos and [Davi's](https://github.com/manelv8) advices to automate MS Windows® applications installs and at computer laboratories. Since 2023 is open under GPL v3.


# License

gpl-3.0

# Author Information

Created in 2022 by [Emanoel Lopes](http://emanoel.pro.br).

# Cite As

```BibTex
@misc{lopes2024ansiblelabs,
    title = {{Managing Windows and macOS physicals machines hosts with Ansible}},
    author = {Lopes, Emanoel Carvalho},
    howpublished = {GitHub Repo},
    url = {https://github.com/emanoelopes/ansible-labs},
    year = {2024}
}
```

