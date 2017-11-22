#!/bin/bash

##############################################
# Folders where are located git repositories #
##############################################
# Paths from ~/

GIT_DIRS=""


########################
# End of configuration #
########################

if [ "$1" == "--gc" ]
then
    DO_GC=1
else
    DO_GC=0
fi

# For every folder listed in GIT_DIRS

fetch_git()
{
    cd $1 > /dev/null

    path="$(pwd)"

    echo -e $path

    echo -ne "\e[34m"

    git fetch

    if [ $DO_GC -eq 1 ]
    then
        git gc
        git submodule foreach 'git gc'
    fi

    # Check for remote gone in repository.
    git branch -vv | grep ": gone"
    if [ $? -eq 0 ]
    then
        echo -e "\e[31mGone remote detected for repo: \e[33m$path"
    fi

    # Check for stash in repository
    if [[ -e $path/.git/logs/refs/stash ]]
    then
        echo -e "\e[1;31mStash detected for repo: \e[0;33m$path"
    fi

    git merge-base --is-ancestor origin/master master

    if [ ! $? -eq 0 ]
    then
        echo -e "\e[1;31mNew commits on Master for repo: \e[0;33m$path\e[34m"

        CUR_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        NB_CHANGES=$(git status --porcelain=v2 --ignore-submodules | wc -l)

        if [ "$CUR_BRANCH" == "master" ] && [ $NB_CHANGES -eq 0 ]
        then
            git rebase
            git submodule update
            echo -e "\e[1;31mMaster automatically updated\e[0;33m"
        fi
    fi

    # Check for remote gone in repository's submodules.
    submodule="unknown"

    while read -r line
    do
        if [[ $line =~ "Entering" ]]
        then
            ar=($line)
            submodule=${ar[1]}
            submodule=${submodule:1:-1}
        elif [[ $line =~ ": gone" ]]
        then
            echo -e "\e[32mGone remote detected for repo: \e[33m$path/$submodule"
        fi
    done < <(git submodule foreach git branch -vv)

    # Check for stash in repository's submodules.
    git submodule foreach -q 'if [ -e $(git rev-parse --git-dir)/logs/refs/stash ]; then echo "\033[1;31mStash detected for submodule: \033[0;33m$toplevel/$path"; fi; exit 0'

    echo -ne "\e[0m"

    cd - > /dev/null
}


# $1 path to folder to handle
go_through_subfolders()
{
    $run cd $1
    local list=`ls $1`
    for d in $list
    do
        if [ -d $1/$d ]
        then
            handle_folder $1/$d
        fi
    done
}

handle_folder()
{
    if [ -e $1/.git ]
    then
        fetch_git $1
    else
        go_through_subfolders $1
    fi
}

for folder in $GIT_DIRS; do
    handle_folder ~/$folder
done
