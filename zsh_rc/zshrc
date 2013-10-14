# My .zshrc by Hubert Lefevre
# Some part by Matt Blissey http://matt.blissett.me.uk/linux/zsh/zshrc
# Git prompt by Sebastian Celis (sebastiancelis.com)
# Some from Alexis Polti

# Use hard limits, except for a smaller stack and no core dumps
unlimit
limit stack 8192
limit core 0
limit -s

# Color table
# Font color
fg_black=%{$'\e[0;30m'%}
fg_red=%{$'\e[0;31m'%}
fg_green=%{$'\e[0;32m'%}
fg_brown=%{$'\e[0;33m'%}
fg_blue=%{$'\e[0;34m'%}
fg_purple=%{$'\e[0;35m'%}
fg_cyan=%{$'\e[0;36m'%}
fg_lgray=%{$'\e[0;37m'%}
fg_dgray=%{$'\e[1;30m'%}
fg_lred=%{$'\e[1;31m'%}
fg_lgreen=%{$'\e[1;32m'%}
fg_yellow=%{$'\e[1;33m'%}
fg_lblue=%{$'\e[1;34m'%}
fg_pink=%{$'\e[1;35m'%}
fg_lcyan=%{$'\e[1;36m'%}
fg_white=%{$'\e[1;37m'%}
# Background Colors
bg_red=%{$'\e[0;41m'%}
bg_green=%{$'\e[0;42m'%}
bg_brown=%{$'\e[0;43m'%}
bg_blue=%{$'\e[0;44m'%}
bg_purple=%{$'\e[0;45m'%}
bg_cyan=%{$'\e[0;46m'%}
bg_gray=%{$'\e[0;47m'%}
# Attributes
at_normal=%{$'\e[0m'%}
at_bold=%{$'\e[1m'%}
at_italics=%{$'\e[3m'%}
at_underl=%{$'\e[4m'%}
at_blink=%{$'\e[5m'%}
at_outline=%{$'\e[6m'%}
at_reverse=%{$'\e[7m'%}
at_nondisp=%{$'\e[8m'%}
at_strike=%{$'\e[9m'%}
at_boldoff=%{$'\e[22m'%}
at_italicsoff=%{$'\e[23m'%}
at_underloff=%{$'\e[24m'%}
at_blinkoff=%{$'\e[25m'%}
at_reverseoff=%{$'\e[27m'%}
at_strikeoff=%{$'\e[29m'%}

# Completion
autoload -U compinit
compinit
# case insensitive completion
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

# for cd, don't try username completions (~polti)
zstyle ':completion:*:cd:*' tag-order local-directories path-directories

# Completion in rm, mv, cp
zstyle ':completion:*:rm:*' ignore-line yes
zstyle ':completion:*:mv:*' ignore-line yes
zstyle ':completion:*:cp:*' ignore-line yes
zstyle ':completion:*:descriptions' format '%U%B%d%b%u'
zstyle ':completion:*:warnings' format '%BSorry, no matches for: %d%b'

# Completion selection by menu for kill
zstyle ':completion:*:*:kill:*' menu yes select
zstyle ':completion:*:kill:*' force-list always
zstyle ':completion:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
# Menu select
zstyle ':completion:*' menu select

# Aliases
alias ssh='ssh -X'              # Automatix graphic interface with ssh
alias m='more'
alias more=less
alias l="ls -AFhl -g"
alias ls='ls --color=auto'
alias ll='ls --color=auto -lh'
alias lll='ls --color=auto -lh | less'
alias grep='grep --colour'
alias ms='ls --color=auto'
alias la='ls -a --color=auto'
alias sl='ls --color=auto'
alias rm='nocorrect rm -r'   # no spelling correction on rm and ask for confirmation
alias mv='nocorrect mv -i'      # no spelling correction on mv
alias make='nocorrect make'     # no spelling correction on make
alias locate='nocorrect locate' # no spelling correction on locate
alias mkdir='nocorrect mkdir'   # no spelling correction on mkdir
alias cp='cp -r -i'
alias fuck='clear'
alias lo='libreoffice'
# git
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gca='git commit -a'
alias gph='git push'
alias gpl='git pull'
alias gd='git diff'
alias gap='git add -p'
# Editors on shell
alias pico='nano -mw'
alias nano='nano -mw'
# Auto launch
alias -s html='firefox'
alias -s c='vim'
alias -s h='vim'
alias -s o='vim'
alias -s md='vim'
alias -s cpp='vim'
alias -s vim='vim'
alias -s mk='vim'
alias -s mkv='vlc'
alias -s sv='emacs'
alias -s v='emacs'
alias -s txt='emacs'
alias -s pdf='evince'
alias -s odt='lowriter'
alias -s odp='loimpress'
alias -s ods='localc'
alias -s xls='localc'
alias -s py='python'
# Auto background
alias f='firefox &'
alias xchat='xchat &'
alias playonlinux='playonlinux &'
# Other
alias today='cat /usr/share/calendar/* | grep `date +"%m/%d"`'
alias enst='ssh -X hlefevre@ssh.enst.fr'
alias a406='ssh -X hlefevre@a406-04.enst.fr'
alias apt-get='sudo apt-get'
alias aptitude='sudo aptitude'
alias j='jobs'
# color
alias diff='colordiff'
# Global aliases (expand whatever their position)
# e.g. find . E L
alias -g G='| grep'
alias -g L='| less'
alias -g H='| head'
alias -g S='| sort'
alias -g T='| tail'
# lock screen using xscreensaver
alias lock='xscreensaver-command -lock'


unsetopt beep                      # keep quiet
unsetopt hist_beep
unsetopt list_beep

# Set Options
setopt correct
setopt autocd                      # Typing cd everytime is boring
setopt auto_pushd pushd_minus      # don't use cd, use pushd
setopt pushd_silent pushd_to_home
setopt pushd_ignore_dups
setopt prompt_subst                # allow function for prompt
setopt rm_star_wait                # Don't do anything stupid Like delete all
setopt chase_links                 # converts links to real path
setopt noclobber                   # don't allow > to clobber files
setopt complete_aliases
setopt extended_glob
setopt no_flow_control
setopt list_types
setopt mark_dirs
setopt path_dirs
setopt auto_remove_slash
setopt prompt_percent
setopt prompt_subst
setopt rm_star_wait                # rm * waits 10 seconds
setopt multios                     # allow multiple redirection echo 'a'>b>c
setopt bang_hist                   # allow ! for accessing history
setopt nohup                       # don't hup running jobs on logout.
unsetopt share_history             # Share history between multiple shells
setopt hist_ignore_dups            # If I type cd and then cd again, only save the last one
setopt hist_ignore_all_dups        # Even if there are commands inbetween commands that are the same, still only save the last one
setopt hist_ignore_space           # If a line starts with a space, don't save it.
setopt hist_no_store
setopt EXTENDED_HISTORY            # Save the time and how long a command ran
setopt hist_save_no_dups
setopt hist_expire_dups_first
setopt hist_find_no_dups

# Bind Key
# Emacs key
bindkey -e
# Input control
bindkey '^[[1;5D' backward-word    # Ctrl + LEFT
bindkey '^[[1;5C' forward-word     # Ctrl + RIGHT
bindkey '\e[1~' beginning-of-line  # Debut
bindkey '\e[4~' end-of-line        # fin

# Autoload zsh functions.
fpath=(~/.zsh/functions $fpath)
autoload -U ~/.zsh/functions/*(:t)

# Enable auto-execution of functions.
typeset -ga preexec_functions
typeset -ga precmd_functions
typeset -ga chpwd_functions

# Append git functions needed for prompt.
preexec_functions+='preexec_update_git_vars'
precmd_functions+='precmd_update_git_vars'
chpwd_functions+='chpwd_update_git_vars'

# prompt
autoload -U promptinit
promptinit
export PROMPT='${fg_green}%n${fg_blue}@${fg_lred}%m ${fg_lgray}[%T]%{${fg_cyan}%}%B%b${fg_yellow}$(prompt_git_info)%{${fg[default]}%}
${fg_lblue}-> ${at_normal}'
export RPROMPT="${fg_lgreen}%~/ ${at_normal}"

# Historic
export HISTSIZE=2000
export HISTFILE="$HOME/.history"
export SAVEHIST=$HISTSIZE
#Say how long a command took, if it took more than 10 seconds
#export REPORTTIME=10

# Watch other user login/out
watch=notme
export LOGCHECK=60

# Lines for compiling and correct usr of openocd
export PATH=$PATH:/opt/tools_arm/bin/
export PATH=$PATH:/opt/openocd/bin/
export PATH=$PATH:/opt/msp430/msp430mcu-20120406/bin/
export PATH=$PATH:/opt/soclib/utils/bin/
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

alias openocd="sudo /opt/openocd/bin/openocd"

# SSH Completion
users=(hlefevre paluche hubert)
hosts=(191.168.1.100 198.168.1.101 ssh.enst.fr bar-telecom.kicks-ass.net a406-01.enst.fr a406-10.enst.fr paluche-laptop)

zstyle ':completion:*' users $users
zstyle ':completion:*:hosts' hosts $hosts

# Format titles for screen and rxvt
precmd () {print -Pn "\e]2;%n@%m%#  %~ %l  %w :: %T\a"}
preexec () {print -Pn "\e]2;%n@%m%#  <$1>  %~ %l  %w :: %T\a"}

# Misc settings
#export EDITOR="nano -mw"
export LM_LICENSE_FILE=@flexlm.comelec.enst.fr

# functions
# extract the files
extract()
{
    if [[ -z "$1" ]]; then
        print -P "usage: \e[1;36mextract\e[1;0m < filename >"
        print -P "       Extract the file specified based on the extension"
    elif [[ -f $1 ]]; then
        case ${(L)1} in
            *.tar.bz2)  tar -jxvf $1;;
            *.tar.gz)   tar -zxvf $1;;
            *.bz2)      bunzip2 $1   ;;
            *.gz)       gunzip $1   ;;
            *.jar)      unzip $1       ;;
            *.rar)      unrar x $1   ;;
            *.tar)      tar -xvf $1   ;;
            *.tbz2)     tar -jxvf $1;;
            *.tgz)      tar -zxvf $1;;
            *.zip)      unzip $1      ;;
            *.Z)        uncompress $1;;
            *)          echo "Unable to extract '$1' :: Unknown extension"
        esac
    else
        echo "File ('$1') does not exist!"
    fi
}

# Alexis Polti functions
# ls handling
if [[ -x `which gls` ]]; then
    alias rls=`which ls`
    alias ls='gls -h --color=auto '
# Unfortunatly GNU ls support -G.
elif [[ $(uname) != 'Linux' && -n `ls -G` && $? == 0 ]]; then
    alias ls='ls -G'
elif [[ -n `ls --color` && $? == 0 ]]; then
  # Check if ls can handle the --color option. If it can it's probably gnu.
    alias ls='ls --color=auto'
fi

if [ `uname` = "Linux" ]; then
    export LS_COLORS="di=34;4:ln=35;4:ex=31:*.rpm=32:*.gz=32:*.tar=32:*.tgz=32"
fi

# (if running screen, show window #)
if [ x$WINDOW != x ]; then
    PROMPT='$WINDOW:'$PROMPT
fi

# Nice function but I don't like it
# on slow disk access, show moving dots
#expand-or-complete-with-dots() {
#  echo -n "\e[31m......\e[0m"
#  zle expand-or-complete
#  zle redisplay
#}
#zle -N expand-or-complete-with-dots
#bindkey "^I" expand-or-complete-with-dots
#

if [ `hostname` = "paluche-laptop" ]; then
  alias gohubert='cd /media/paluche/OS/Users/Hubert'
elif [ `hostname` = "dell-hlefevre" ]; then
  #TODO Add here specific
fi

