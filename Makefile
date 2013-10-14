
.PHONY: all install vim git zsh emacs

all:
	@echo "Usage: \n" 				  																										\
				"Installation\n"                                                          \
				"make vim         # Install vim configuration in your home folder\n" 			\
				"make git         # Install git configuration in your home folder\n" 			\
				"make zsh         # Install zsh configuration in your home folder\n" 			\
				"make emacs       # Install emacs configuration in your home folder\n" 		\
				"make install     # Install all the configuration in your home folder\n" 	\
				"\n Uninstallation\n"                                                      \
				"make clean_vim   # Remove vim configuration in your home folder\n" 			\
				"make clean_git   # Remove git configuration in your home folder\n" 			\
				"make clean_zsh   # Remove zsh configuration in your home folder\n" 			\
				"make clean_emacs # Remove emacs configuration in your home folder\n"  		\
				"make clean       # Remove all configuration files from your home folder\n"

# The principe of the installation is to create links in your home folder link to the configuration
# files and folders in the repository. Then you could share same configurations files with all your
# computer. And change configuration files from any computer.

install: vim git zsh emacs

vim:
	ln vim_rc/vimrc ~/.vimrc
	cp vim_rc/vim ~/.vim

git:
	ln git_rc/gitconfig ~/.gitconfig

zsh:
	ln zsh_rc/zshrc ~/.zshrc
	cp zsh_rc/zsh ~/.zsh

emacs:
	ln emacs_rc/emacs ~/.emacs
	cp emacs_rc/emacs.d  ~/.emacs.d

clean: clean_vim clean_git clean_zsh clean_emacs

clean_vim:
	rm -rf ~/.vimrc
	rm -rf ~/.vim

clean_git:
	rm -rf  ~/.gitconfig

clean_zsh:
	rm -rf ~/.zshrc
	rm -rf ~/.zsh

clean_emacs:
	rm -rf ~/.emacs
	rm -rf ~/.emacs.d
