# Managing Windows and macOS physicals machines hosts with Ansible

This repository contains Ansible playbooks, roles and tasks to manage on-premises Windows 10/11, Linux and macOS machines on computer labs. 

Created to support mantaining daily techinical routines like: 
- Install apps;
- Users management;
- Scheduled tasks management;
- Change power plan on Windows 10;
- Windows updates: drivers, definitions updates etc.
- and much more.

Example:

```shell
$ ansible-playbook site.yaml -e "local=ip_address" -k -t netbeans
```
```
ansible-playbok --------  Using a playbook file;
site.yaml --------------  Playbook file;
-e "local=ip_address" --  Especify local variable;
-k ---------------------  Ask admin user password;
-t ---------------------  Call a especific tag.
``` 

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

