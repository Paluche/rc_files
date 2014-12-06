#!/bin/bash

red='\033[0;31m'
orange='\033[1;31m'
green='\033[0;32m'
yellow='\033[0;33m'
blue='\033[0;34m'
purple='\033[0;35m'
lpurple='\033[1;35m'
cyan='\033[0;36m'
white='\033[0;37m'
bwhite='\033[1;37m'
NC='\033[0m' # No Color

echo -e "
${red}red
${orange}orange
${green}green
${yellow}yellow
${blue}blue
${purple}purple
${lpurple}lpurple
${cyan}cyan
${white}white
${bwhite}bwhite"

if command -v tree >/dev/null; then
    echo -e "${orange}Tree ${blue}already installed${NC}"
else
    echo -e "${red}Installing ${orange}tree${NC}";
    sudo apt-get install tree;
    echo -e "${orange}tree ${green}installed${NC}";
fi

if command -v zsh >/dev/null; then
    echo -e "${orange}ZSH ${blue}already installed${NC}"
else
    echo -e "${red}Installing ${orange}ZSH${NC}"
    sudo apt-get install zsh
    echo -e "${purple}Setting ZSH as the default shell${NC}"
    chsh -s /bin/zsh
    echo -e "${orange}ZSH installed${NC}"
fi

if command -v acpi >/dev/null; then
    echo -e "${orange}ACPI ${blue}already installed${NC}"
else
    echo -e "${red}Installing ACPI${NC}"
    sudo apt-get install acpi
    echo -e "${orange}ACPI installed${NC}"
fi


# Windows Manager
if command -v awesome >/dev/null; then
    echo -e "${orange}Awesome WM ${blue}already installed${NC}"
else
    echo -e "${red}Installing awesome WM${NC}"
    sudo apt-get install awesome
    echo -e "${orange}Awesome WM installed${NC}"
fi

if command -v gnome-wm >/dev/null; then
    echo -e "${orange}Gnome WM ${blue}already installed${NC}"
else
    echo -e "${red}Installing gnome WM${NC}"
    sudo apt-get install gnome
    echo -e "${orange}Gnome WM installed${NC}"
fi

# Code editors
if command -v emacs >/dev/null; then
    echo -e "${orange}Emacs ${blue}already installed${NC}"
else
    echo -e "${red}Installing emacs WM${NC}"
    sudo apt-get install emacs
    echo -e "${orange}Emacs installed${NC}"
fi

if command -v vim >/dev/null; then
    echo -e "${orange}VIM ${blue}already installed${NC}"
else
    echo -e "${red}Installing VIM${NC}"
    sudo apt-get install vim
    echo -e "${orange}VIM installed${NC}"
fi

# Version revision
if command -v git >/dev/null; then
    echo -e "${orange}GIT ${blue}already installed${NC}"
else
    echo -e "${red}Installing GIT${NC}"
    sudo apt-get install git
    echo -e "${orange}GIT installed${NC}"
fi

if command -v gitk >/dev/null; then
    echo -e "${orange}GITK ${blue}already installed${NC}"
else
    echo -e "${red}Installing GITK${NC}"
    sudo apt-get install gitk
    echo -e "${orange}GITK installed${NC}"
fi

# Others
#if command -v valgrind >/dev/null; then
#    echo -e "${orange}Valgrind ${blue}already installed${NC}"
#else
#    echo -e "${red}Installing valgrind${NC}"
#    sudo apt-get install valgrind
#    echo -e "${green}Valgrind installed${NC}"
#fi
#
#if command -v wireshark /dev/null; then
#    echo -e "${orange}Wireshark ${blue}already installed${NC}"
#else
#    echo -e "${red}Installing wireshark${NC}"
#    sudo apt-get install wireshark
#    echo -e "${green}Wireshark installed${NC}"
#fi

if command -v ag >/dev/null; then
    echo -e "${orange}AG ${blue}already installed${NC}"
else
    echo -e "${red}Installing AG${NC}"
    apt-get install silversearcher-ag
    echo -e "${green}AG installed${NC}"
fi
