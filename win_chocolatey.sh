#!/bin/bash
echo "Package name: "
read package_name;
echo "Target: " 
read target;
echo "Would you like to install: $package_name on $target (y/n)"
read choice;
if [ "$choice" == "y" ];
install()
{
  ansible $target -m win_chocolatey -a "name=$package_name state=present -k
}  
if [ "$choice" == "y" ];
then
  echo "$package_name will be instaled at $target"
fi
