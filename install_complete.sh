# Terminal zsh and needed program associated
if hash zsh 2>/dev/null; then
    sudo apt-get install zsh
    echo "Enter /usr/bin/zsh for setting zsh as a default shell"
    chsh
fi

if hash acpi 2>/dev/null; then
    sudo apt-get install acpi
fi

# Windows Manager
if hash awesome 2>/dev/null; then
    sudo apt-get install awesome
fi

if hash gnome-wm 2>/dev/null; then
    sudo apt-get install gnome
fi

# Code editor
if hash emacs 2>/dev/null; then
    sudo apt-get install emacs
fi

if hash vim 2>/dev/null; then
    sudo apt-get install vim
fi

# Version revision
if hash git 2>/dev/null; then
    sudo apt-get install git
fi

if hash gitk 2>/dev/null; then
    sudo apt-get install gitk
fi

# Others
#if hash valgrind 2>/dev/null; then
#    sudo apt-get install valgrind
#fi

#if hash wireshark /dev/null; then
#    sudo apt-get install wireshark
#fi

if hash fluxgui 2>/dev/null; then
    sudo add-apt-repository ppa:kilian/f.lux
    sudo apt-get update
    sudo apt-get install fluxgui
fi

make install
