#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
if sudo apt-get upgrade | grep -q 'sudo apt-get autoremove'
then
  sudo apt-get autoremove -y
fi
