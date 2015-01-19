CURR_DIR = $(shell pwd)

all:
	@echo "Usage:\n"                                                                               \
			"    Installation of the configuration files\n"                                        \
			"        make [vim | git | zsh | emacs | awesome | xresources | adb_logcat | xflux]\n" \
			"        make install     # Install all the previous software configuration\n"

# Specify where to install the symbolic links of the configuration files and folders
VIMRC_DIR      = $(HOME)
VIM_DIR        = $(HOME)
GITCONFIG_DIR  = $(HOME)
ZSHRC_DIR      = $(HOME)
ZSH_DIR        = $(HOME)
EMACS_DIR      = $(HOME)
EMACS_D_DIR    = $(HOME)
AWESOME_DIR    = $(HOME)/.config
XRESOURCES_DIR = $(HOME)

# Where to put the symbolic links of the scripts
SCRIPT_DIR     = ~/.script

# Where to save previous configuration files
BACKUP_FOLDER  = ~/rc_backup

#################################
# Create the directories needed #
#################################
DIR_LIST       = $(sort $(VIMRC_DIR) $(VIM_DIR) $(GITCONFIG_DIR) $(ZSHRC_DIR) $(ZSH_DIR) $(EMACS_DIR) \
                 $(EMACS_D_DIR) $(AWESOME_DIR) $(XRESOURCES_DIR) $(SCRIPT_DIR) $(BACKUP_FOLDER))

$(DIR_LIST):
	mkdir $@

###############
# Phony rules #
###############
install: vim git zsh emacs awesome xresources adb_logcat xflux

vim:        save_vim        $(VIMRC_DIR)/.vimrc           $(VIM_DIR)/.vim
git:        save_git        $(GITCONFIG_DIR)/.gitconfig
zsh:        save_zsh        $(ZSHRC_DIR)/.zshrc           $(ZSH_DIR)/.zsh
emacs:      save_emacs      $(EMACS_DIR)/.emacs           $(EMACS_D_DIR)/.emacs.d
awesome: 	save_awesome    $(AWESOME_DIR)/awesome
xresources: save_xresources $(XRESOURCES_DIR)/.Xresources
adb_logcat:                 $(SCRIPT_DIR)/adb_logcat.py
xflux:                      $(SCRIPT_DIR)/xflux

#########
# Rules #
#########
%/.vim: $(CURR_DIR)/vim_rc/vim %
	@echo Install vimrc configuration file
	@-ln -sn $< $@

%/.vimrc: $(CURR_DIR)/vim_rc/vimrc $@ %
	@echo Install vim folder
	@-ln -sn $< $@

%/.gitconfig: %
	@echo Install gitconfig file
	@-ln -sn $(CURR_DIR)/git_rc/gitconfig $@

%/.zsh: $(CURR_DIR)/zsh_rc/zsh %
	@echo Install zsh configuration file
	@-ln -sn $< $@

%/.zshrc: $(CURR_DIR)/zsh_rc/zshrc %
	@echo Install zshrc configuration folder
	@-ln -sn $< $@


%/.emacs: $(CURR_DIR)/emacs_rc/emacs %
	@echo Install emacs configuration file
	@-ln -sn $< $@

%/.emacs: $(CURR_DIR)/emacs_rc/emacs.d %
	@echo Install emacs.d folder
	@-ln -sn $< $@

%/awesome: $(CURR_DIR)/awesome %
	@echo Install awesome configuration
	@-ln -sn $< $@

%/xresources: $(CURR_DIR)/Xresources/Xresources %
	@echo Install xresources configuration
	@-ln -sn $< $@
	@xrdb $@

%/adb_logcat.py: $(CURR_DIR)/adb_logcat/coloredlogcat.pytxt %
	@echo Install adb_logcat.py script
	@-ln -sn $< $@

%/xflux: $(CURR_DIR)/xflux/xflux %
	@echo Install xflux
	@-ln -sn $< $@

#
# Save the previous the configurations
#
.PHONY: save save_vim save_git save_zsh save_emacs save_awesome save_xresources save_adb_logcat save_xflux

# Set the variables to YES if the selected file/folder is actually a symbolic link
test_file       = $(shell                    \
                    if [ -e $(1) ];          \
                        then if [ -L $(1) ]; \
                            then echo NO;    \
                            else echo YES;   \
                        fi;                  \
                    else                     \
                        echo NO;             \
                    fi)

VIM_TEST        = $(call test_file, $(VIM_DIR)/.vim)
VIMRC_TEST      = $(call test_file, $(VIMRC_DIR)/.vimrc)
GITCONFIG_TEST  = $(call test_file, $(GITCONFIG_DIR)/.gitconfig)
ZSH_TEST        = $(call test_file, $(ZSH_DIR)/.zsh)
ZSHRC_TEST      = $(call test_file, $(ZSHRC_DIR)/.zshrc)
EMACS_TEST      = $(call test_file, $(EMACS_DIR)/.emacs)
EMACSD_TEST     = $(call test_file, $(EMACS_D_DIR)/.emacs.d)
AWESOME_TEST    = $(call test_file, $(AWESOME_DIR)/awesome)
XRESOURCES_TEST = $(call test_file, $(XRESOURCES_DIR)/.Xresource)

# Main save rule
save: save_vim save_git save_zsh save_emacs save_awesome save_xresources save_adb_logcat

testsave:
	@echo "vim:        $(VIM_TEST)"
	@echo "vimrc:      $(VIMRC_TEST)"
	@echo "gitconfig:  $(GITCONFIG_TEST)"
	@echo "zsh:        $(ZSH_TEST)"
	@echo "zshrc:      $(ZSHRC_TEST)"
	@echo "emacs:      $(EMACS_TEST)"
	@echo "emacsd:     $(EMACSD_TEST)"
	@echo "awesome:    $(AWESOME_TEST)"
	@echo "xresources: $(XRESOURCES_TEST)"

# VIM
ifeq ($(VIM_TEST), YES)
save_vim: save_vimrc $(BACKUP_FOLDER)
	@echo Backup .vimrc file in $(BACKUP_FOLDER)
	@mv ~/.vimrc $(BACKUP_FOLDER)/vimrc
else
save_vim: save_vimrc
endif

ifeq ($(VIMRC_TEST), YES)
save_vimrc: $(BACKUP_FOLDER)
	@echo Backup .vim folder in ~/rc_backup
	@mv ~/.vimrc ~/rc_backup/vimrc
else
save_vimrc:
endif

# GIT
ifeq ($(GITCONFIG_TEST), YES)
save_git: $(BACKUP_FOLDER)
	@echo Backup .gitconfig file in ~/rc_backup
	@mv ~/.gitconfig ~/rc_backup/gitconfig
else
save_git:
endif

# ZSH
ifeq ($(ZSH_TEST), YES)
save_zsh: save_zshrc $(BACKUP_FOLDER)
	@echo Backup .zsh folder in ~/rc_backup
	@mv ~/.zsh ~/rc_backup/zsh
else
save_zsh: save_zshrc
endif

ifeq ($(ZSHRC_TEST), YES)
save_zshrc: $(BACKUP_FOLDER)
	@echo Backup .zshrc file in ~/rc_backup
	@mv ~/.zshrc ~/rc_backup/zshrc
else
save_zshrc:
endif

# EMACS
ifeq ($(EMACS_TEST), YES)
save_emacs: save_emacsd $(BACKUP_FOLDER)
	@echo Backup .emacs file in ~/rc_backup
	@mv ~/.emacs ~/rc_backup/emacs
else
save_emacs: save_emacsd
endif

ifeq ($(EMACSD_TEST), YES)
save_emacsd: $(BACKUP_FOLDER)
	@echo Backup .emacsd folder in ~/rc_backup
	@mv ~/.emacs ~/rc_backup/emacsd
else
save_emacsd:
endif

# Awesome WM
ifeq ($(AWESOME_TEST), YES)
save_awesome: $(BACKUP_FOLDER)
	@echo Backup .awesome folder in ~/rc_backup
	@mv ~/.config/awesome ~/rc_backup/awesome
else
save_awesome:
endif

# Xresource
ifeq ($(XRESOURCES_TEST), YES)
save_xresources: $(BACKUP_FOLDER)
	@echo Backup .Xressources file in ~/rc_backup
	@mv ~/.emacs ~/rc_backup/emacs
else
save_xresources:
endif
