# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository overview
- Purpose: Manage on‑prem Windows, Linux, and macOS lab machines with Ansible (install apps, manage users/scheduled tasks, power plans, Windows updates, etc.). See README.md for context.

High‑level architecture
- Inventory: inventory.ini defines groups lab1–lab6 (Windows via WinRM) and avell/ppgte (SSH). Group vars set transport, ports, and authentication behavior. A global [all:vars] sets defaults like ansible_user and winrm cert validation.
- Ansible config (ansible.cfg):
  - inventory=inventory.ini, forks=10, host_key_checking=False, and useful timing/profile callbacks enabled.
  - Note on roles path: the file sets default_roles_path=/roles. When running locally (outside Docker), ensure Ansible can resolve the repo’s roles directory (see Commands → Environment note).
- Roles:
  - roles/biosupdate: Windows BIOS update role.
    - tasks/main.yml conditionally includes model‑specific task files using ansible_facts.product_name.
    - tasks/780.yml and tasks/7010.yml copy a model‑specific BIOS updater and run it with win_package when the current BIOS version differs (uses win_copy and win_package, silent args /s and /r where applicable).
- Docker runtime (Dockerfile):
  - Alpine base with python3, pywinrm, ansible installed. Working directory /ansible-labs. Designed to run Ansible inside a container with the repo mounted.
- Python project scaffold (pyproject.toml): Present but no dependencies defined; not used by Ansible flows.

Common commands
Environment note (roles path)
- If running Ansible locally (not in the provided Docker image), ensure roles are discoverable from ./roles:
  - Bash
    export ANSIBLE_ROLES_PATH="$PWD/roles"

Using Docker (recommended for a consistent Ansible environment)
- Build the image
  - Bash
    docker build -t ansible-labs:local .
- Verify Ansible inside the container
  - Bash
    docker run --rm ansible-labs:local ansible-playbook --version
- Run a playbook from the repo (mount PWD into the container)
  - Bash
    docker run --rm -v "$PWD":/ansible-labs -w /ansible-labs \
      ansible-labs:local \
      ansible-playbook -i inventory.ini <your_playbook>.yml

Connectivity checks (before running changes)
- Windows hosts (e.g., lab1 uses WinRM)
  - Bash
    ansible -i inventory.ini lab1 -m win_ping -k
- SSH hosts (e.g., ppgte)
  - Bash
    ansible -i inventory.ini ppgte -m ping

Running the BIOS update role
- Create a minimal playbook that targets the desired group and applies the role:
  - YAML
    - hosts: lab1
      gather_facts: true
      roles:
        - biosupdate
- Execute it (locally):
  - Bash
    ansible-playbook -i inventory.ini biosupdate.yml
- Execute it (in Docker):
  - Bash
    docker run --rm -v "$PWD":/ansible-labs -w /ansible-labs \
      ansible-labs:local \
      ansible-playbook -i inventory.ini biosupdate.yml

Linting and tests
- No ansible-lint configuration or Molecule scenarios were found in this repository; there is currently no automated linting or test harness configured here.

Notes from README.md
- Example pattern provided:
  - Bash
    ansible-playbook site.yaml -e "local=ip_address" -k -t netbeans
  This refers to a site.yaml playbook (not present in this repo). Adapt to your own playbook file as needed.
