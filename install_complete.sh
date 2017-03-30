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

curr_dir= pwd

echo -e "${red}WARNING
This script will override any configuration files of the following programs:
    VIM, emacs, awesome WM, Xresources.

    Enter yes to proceed${NC}"
read yesOrNo

if [ "$yesOrNo" = "yes" ] || [ "${yesOrNo}" = "Yes" ]; then
    echo ""
else
    exit
fi

if command -v zsh >/dev/null; then
    echo -e "${orange}ZSH ${blue}already installed${NC}"
else
    echo -e "${red}Installing ${orange}ZSH${NC}"
    sudo apt-get -y install zsh
    echo -e "${lpurple}Setting ZSH as the default shell${NC}"
    chsh -s /bin/zsh

    echo -e "${orange}ZSH installed${NC}"
fi

# Make
if [ -L $HOME/.zshrc ]; then
    echo -e "${orange}ZSH ${blue}configuration files already up to date${NC}"
else
    echo -e "${purple}Installing ZSH configuration files${NC}"
    ln -sf $curr_dir/zsh_rc/zshrc $HOME/.zshrc
fi

if command -v tree >/dev/null; then
    echo -e "${orange}Tree ${blue}already installed${NC}"
else
    echo -e "${red}Installing ${orange}tree${NC}";
    sudo apt-get -y install tree;
    echo -e "${orange}tree ${green}installed${NC}";
fi

if command -v acpi >/dev/null; then
    echo -e "${orange}ACPI ${blue}already installed${NC}"
else
    echo -e "${red}Installing ACPI${NC}"
    sudo apt-get -y install acpi
    echo -e "${orange}ACPI installed${NC}"
fi


# Windows Manager
if command -v awesome >/dev/null; then
    echo -e "${orange}Awesome WM ${blue}already installed${NC}"
else
    echo -e "${red}Installing awesome WM${NC}"
    sudo apt-get -y install awesome
    echo -e "${orange}Awesome WM installed${NC}"
fi

#if command -v gnome-wm >/dev/null; then
#    echo -e "${orange}Gnome WM ${blue}already installed${NC}"
#else
#    echo -e "${red}Installing gnome WM${NC}"
#    sudo apt-get -y install gnome
#    echo -e "${orange}Gnome WM installed${NC}"
#fi

# Code editors
if command -v emacs >/dev/null; then
    echo -e "${orange}Emacs ${blue}already installed${NC}"
else
    echo -e "${red}Installing emacs WM${NC}"
    sudo apt-get -y install emacs
    echo -e "${orange}Emacs installed${NC}"
fi

if command -v vim >/dev/null; then
    echo -e "${orange}VIM ${blue}already installed${NC}"
else
    echo -e "${red}Installing VIM${NC}"
    sudo apt-get -y install vim
    echo -e "${orange}VIM installed${NC}"
fi

# Version revision
if command -v git >/dev/null; then
    echo -e "${orange}GIT ${blue}already installed${NC}"
else
    echo -e "${red}Installing GIT${NC}"
    sudo apt-get -y install git
    echo -e "${orange}GIT installed${NC}"
fi

if command -v gitk >/dev/null; then
    echo -e "${orange}GITK ${blue}already installed${NC}"
else
    echo -e "${red}Installing GITK${NC}"
    sudo apt-get -y install gitk
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
    sudo apt-get -y install silversearcher-ag
    echo -e "${green}AG installed${NC}"
fi

if command -v urxvt >/dev/null; then
    echo -e "${orange}URxvt ${blue}already installed${NC}"
else
    echo -e "${red}Installing URxvt${NC}"
    sudo apt-get -y install rxvt-unicode-256color
    echo -e "${green}URxvt installed${NC}"
fi

echo "Copying fonts..."
FONT_DIRECTORY=~/.local/share/fonts

if [ ! -d "$FONT_DIRECTORY" ]; then
    mkdir $FONT_DIRECTORY
fi
cp ./fonts/* $FONT_DIRECTORY

# Reset font cache on Linux
echo "Resetting font cache, this may take a moment..."
fc-cache -f $FONT_DIRECTORY

bundle=./vim_rc/vim/bundle
# VIM plugins
git clone https://github.com/vim-scripts/DoxygenToolkit.vim     $bundle/DoxygenToolkit.vim
git clone https://github.com/tomtom/tlib_vim                    $bundle/tlib_vim
git clone https://github.com/tomtom/tskeleton_vim               $bundle/tskeleton_vim
git clone https://github.com/honza/vim-snippets                 $bundle/vim-snippets
git clone https://github.com/scrooloose/syntastic               $bundle/syntastic
git clone https://github.com/scrooloose/nerdtree                $bundle/nerdtree
git clone https://github.com/scrooloose/nerdcommenter           $bundle/nerdcommenter
git clone https://github.com/tpope/vim-surround                 $bundle/vim-surround
git clone https://github.com/tpope/vim-pathogen                 $bundle/vim-pathogen
git clone https://github.com/tpope/vim-fugitive                 $bundle/vim-fugitive
git clone https://github.com/vim-airline/vim-airline            $bundle/vim-airline
git clone https://github.com/vim-airline/vim-airline-themes     $bundle/vim-airline-themes
git clone https://github.com/airblade/vim-gitgutter             $bundle/vim-gitgutter
# Cool selected themes:
#   wonbat, iterm, solarized, simple, serene, kolor, ditinguished, behelit, cool
git clone https://github.com/altercation/vim-colors-solarized   $bundle/vim-colors-solarized
git clone https://github.com/gregsexton/gitv                    $bundle/gitv
git clone https://github.com/kien/rainbow_parentheses.vim       $bundle/rainbow_parentheses
git clone https://github.com/vim-scripts/taglist.vim            $bundle/taglist
git clone https://github.com/Xuyuanp/nerdtree-git-plugin        $bundle/nerdtree-git-plugin
