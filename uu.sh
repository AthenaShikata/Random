#!/bin/bash
sudo apt-get update
sudo apt-get upgrade
if sudo apt-get upgrade -y | grep -q 'sudo apt autoremove'
then
  sudo apt-get autoremove -y
fi
