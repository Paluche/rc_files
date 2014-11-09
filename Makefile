CURR_DIR = $(shell pwd)
.PHONY: all install vim git zsh emacs update udpate_vim update_zsh update_emacs clean clean_vim \
                clean_git clean_zsh clean_emacs

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
install: vim git zsh emacs awesome xresources

vim: clean_vim
	@echo Install vim
	@ln -s $(CURR_DIR)/vim_rc/vimrc          ~/.vimrc
	@ln -s $(CURR_DIR)/vim_rc/vim            ~/vim
	@mv ~/vim ~/.vim

git: clean_git
	@echo Install git
	@ln -s $(CURR_DIR)/git_rc/gitconfig      ~/.gitconfig

zsh: clean_zsh
	@echo Install zsh
	@ln -s $(CURR_DIR)/zsh_rc/zshrc          ~/.zshrc
	@ln -s $(CURR_DIR)/zsh_rc/zsh            ~
	@mv ~/zsh ~/.zsh

emacs: clean_emacs
	@ln -s $(CURR_DIR)/emacs_rc/emacs        ~/.emacs
	@ln -s $(CURR_DIR)/emacs_rc/emacs.d      ~/.emacs.d

awesome:
	ln -s $(CURR_DIR)/awesome               ~/.config/awesome

xresources:
	ln -s $(CURR_DIR)/Xresources/Xresources ~/.Xresources
	xrdb ~/.Xresources

clean: clean_vim clean_git clean_zsh clean_emacs

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
