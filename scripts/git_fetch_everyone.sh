#!/bin/bash

##############################################
# Folders where are located git repositories #
##############################################
# Paths from ~/

GIT_DIRS=""
REPO_AS_SUB=""


########################
# End of configuration #
########################

DO_GC=0
DO_FETCH=1


usage()
{
    echo "usage: $(basename "${0}") [-g] [-c] [-h]
    -g    Force to run \`git gc\` on each handled repository.
    -c    Force just the check part of the script (no fetch).
    -h    Print this help.
    "

    exit 1
}

while getopts gch opt
do
    case "$opt" in
        g) DO_GC=1
           ;;

        c) DO_FETCH=0
           ;;

        *) echo "Unknown option $opt ${OPTARG}"
           usage
           ;;
     esac
done


handle_repo()
{
    repo_path=$(realpath "${1}/${2}")

    cd "$repo_path" > /dev/null || exit 1

    repo_name="$(basename "${repo_path}" 2> /dev/null)"

    echo -e "\e[0m$repo_name \e[31m$repo_path\e[34m"

    if [ $DO_FETCH -eq 1 ]
    then
        git fetch
    fi

    if [ $DO_GC -eq 1 ]
    then
        git gc
        git submodule foreach 'git gc'
    fi

    # Check for remote gone in repository.
    if git branch -vv | grep ": gone"
    then
        echo -e "\e[31mGone remote detected for repo: \e[33m$repo_path\e[31m "
    fi

    # Check for stash in repository
    if [[ -e $repo_path/.git/logs/refs/stash ]]
    then
        echo -e "\e[1;31mStash detected for repo: \e[0;33m$repo_path\e[31m "
    fi

    # Don't update master for submodules, or repo behaving like submodules.
    for path in $REPO_AS_SUB
    do
        if [[ $path == "$repo_path" ]]
        then
            echo -ne "\e[0m"
            return
        fi
    done

    if git merge-base --is-ancestor origin/master master 2&> /dev/null
    then
        if [ "$(git merge-base origin/master master)" != "$(git merge-base --independent master)" ]
        then
            CUR_BRANCH=$(git rev-parse --abbrev-ref HEAD)
            NB_CHANGES=$(git status --porcelain=v2 --ignore-submodules | wc -l)

            if [ "$CUR_BRANCH" == "master" ] && [ "$NB_CHANGES" -eq 0 ]
            then
                git rebase
                git submodule update
                echo -e "\e[1;31mMaster automatically updated"
            else
                echo -e "\e[1;31mNew commits on Master for repo: \e[0;33m$repo_path"
            fi
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
            echo -e "\e[32mGone remote detected for repo: \e[33m$repo_path/$submodule"
        fi
    done < <(git submodule foreach git branch -vv)

    # Check for stash in repository's submodules.
    git submodule foreach -q 'if [ -e $(git rev-parse --git-dir)/logs/refs/stash ]; then echo "\033[1;31mStash detected for submodule: \033[0;33m$toplevel/$path"; fi; exit 0'

    echo -ne "\e[0m"

    cd "$1" || exit 1
}


# $1 path to folder to handle
go_through_subfolders()
{
    cd "$1" || exit 1
    local list

    list=$(ls "$1")

    for d in $list
    do
        if [ -d "$1/$d" ]
        then
            handle_folder "$1" "$d"
        fi
    done
}

handle_folder()
{
    if [ -e "$1/$2/.git" ]
    then
        handle_repo "$1" "$2"
    else
        go_through_subfolders "$1/$2"
    fi
}

# Update data base
for folder in $GIT_DIRS
do
    handle_folder "$HOME/$folder"
done

exit 0
