CURR_DIR = $(shell pwd)
.PHONY: vim git zsh emacs awesome xresources adb_logcat clean_adb_logcat xflux clean clean_vim     \
	clean_git clean_zsh clean_emacs clean_awesome clean_xresources clean_adb_logcat clean_xflux all

all:
	@echo "Usage:\n"                                                                               \
				"Installation of the configuration files\n"                                        \
				"  make [vim | git | zsh | emacs | awesome | xresources]\n"                        \
				"  make install     # Install all the previous software configuration\n"           \
				"\n Uninstallation\n"                                                              \
				"  make [clean_vim | make clean_git | clean_zsh | clean_emacs]\n"                  \
				"  make clean       # Remove all configuration files from your home folder\n"

# The principe of the installation is to create links in your home folder link to the configuration
# files in the repository and copy the configuration folder in your home folder form the repository.
# Then you could share same configurations files with all your computer. And change configuration
# files from any computer.
#
# The reference files for the folder is always the repository. If you want to change something,
# change it in the repository then do a mak update / update_<software_name>
install: vim git zsh emacs awesome xresources adb_logcat

vim: clean_vim
	@echo Install vim configuration
	@ln -s $(CURR_DIR)/vim_rc/vimrc                   ~/.vimrc
	@ln -s $(CURR_DIR)/vim_rc/vim                     ~/vim
	@mv    ~/vim                                      ~/.vim

git: clean_git
	@echo "Install git configuration"
	@ln -s $(CURR_DIR)/git_rc/gitconfig               ~/.gitconfig
	@echo "Configuration of git colors and pull:rebase"
	@git config --global ui.color true
	@git config pull.rebase true


zsh: clean_zsh
	@echo Install zsh configuration
	@ln -s $(CURR_DIR)/zsh_rc/zshrc                   ~/.zshrc
	@ln -s $(CURR_DIR)/zsh_rc/zsh                     ~/
	@mv    ~/zsh                                      ~/.zsh

emacs: clean_emacs
	@echo Install emacs configuration
	@ln -s $(CURR_DIR)/emacs_rc/emacs                 ~/.emacs
	@ln -s $(CURR_DIR)/emacs_rc/emacs.d               ~/.emacs.d

awesome: clean_awesome
	@echo Install awesome configuration
	@ln -s $(CURR_DIR)/awesome                        ~/.config/awesome

xresources: clean_xresources
	@echo Install xresources configuration
	ln -s $(CURR_DIR)/Xresources/Xresources           ~/.Xresources
	xrdb                                              ~/.Xresources

adb_logcat: clean_adb_logcat
	@echo Install adb_logcat.py script
	@ln -s $(CURR_DIR)/adb_logcat/coloredlogcat.pytxt ~/.adb_logcat.py

xflux: clean_xflux
	@echo Install xflux
	@ln -s $(CURR_DIR)/xflux/xflux ~/.xflux

clean: clean_vim clean_git clean_zsh clean_emacs clean_awesome clean_xresources clean_adb_logcat

clean_vim:
	@echo Remove vim configuration
	@rm -rf ~/.vimrc ~/.vim

clean_git:
	@echo Remove git configuration
	@rm -rf  ~/.gitconfig

clean_zsh:
	@echo Remove zsh configuration
	@rm -rf ~/.zshrc
	@rm -rf ~/.zsh

clean_emacs:
	@echo Remove emacs configuration
	@rm -rf ~/.emacs
	@rm -rf ~/.emacs.d

clean_awesome:
	@echo Remove emacs configuration
	@rm -rf ~/.config/awesome

clean_xresources:
	@echo Remove .Xresources configuration
	@rm -rf ~/.Xresources

clean_adb_logcat:
	@echo Remove .adb_logcat.py script
	@rm -rf ~/.adb_logcat.py

clean_xflux:
	@echo Remove .xflux
	@rm -rf ~/.adb_logcat.py
