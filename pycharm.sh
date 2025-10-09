#!/bin/bash
while true; do
ansible lab2 -m win_chocolatey -a 'name=vscode,pycharm-community state=latest' -k 
done
