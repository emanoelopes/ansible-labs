# Managing Windows and macOS hosts with Ansible

This repository contains Ansible playbooks, roles and tasks to manage on-premises Windows 10/11  and macOS computer labs. 

Created to support mantaining daily techinical routines like: 
- Install apps;
- Users management;
- Scheduled tasks management;
- Change Power plan on Windows 10;
- Windows updates: Drivers, Definitions Updates, etc.
- and much more.

Example:

ansible-playbook playbooks/last.yaml -e "local=ip_address" -k -t netbeans

ansible-playbok --------  Using a playbook file;
playbooks/last.yaml ----  Playbook file location;
-e "local=ip_address" --  Especify local variable;
-k ---------------------  Ask admin user password;
-t ---------------------  Call a especific tag.


# License

gpl-3.0

# Author Information

Created in 2022 by [Emanoel Lopes](http://emanoel.pro.br).
