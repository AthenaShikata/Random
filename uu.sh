#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
if sudo apt-get upgrade -y | grep -q 'sudo apt autoremove'
then
  sudo apt-get autoremove -y
fi
date