#! /usr/bin/env bash

RED="\033[0;31m"
ORANGE="\033[1;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
PURPLE="\033[0;35m"
LPURPLE="\033[1;35m"
CYAN="\033[0;36m"
WHITE="\033[0;37m"
BWHITE="\033[1;37m"
NC="\033[0m"

function install_package()
{
  package_name=$1

  if dpkg -S "${package_name}" &> /dev/null
  then
    echo -e "${ORANGE}${package_name}${BLUE}: already installed${NC}"
  else
    echo -e "${ORANGE}${package_name}${BLUE}: not installed${NC}"
  fi
}

PACKAGES="\
  awesome
  neovim
  urxvt
  zsh
  test-random
"

for package in ${PACKAGES}
do
  install_package "${package}"
done
