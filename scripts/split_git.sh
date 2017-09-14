#!/bin/sh

display_usage() {
    echo ""
    echo "Usage:"
    echo "$0 [-s|--source=REPO_SOURCE] [-d|--destination=REPO_DESTINATION] \
[--branch-regex=BRANCH_REGEX] [--tag-regex=TAG_REGEX] \
[-f|--filter=FILTER_FOLDER] [-r|--rm-folders=RM_FOLDERS]"
    echo ""

    exit 0
}

run=

current_dir=`pwd`

for i in "$@"
do
case $i in
    -s=*|--source=*)
    REPO_SOURCE="${i#*=}"
    shift # past argument=value
    ;;
    --branch-regex=*)
    BRANCH_REGEX="${i#*=}"
    shift # past argument=value
    ;;
    --tag-regex=*)
    TAG_REGEX="${i#*=}"
    shift # past argument=value
    ;;
    -f=*|--filter=*)
    FILTER_FOLDER="${i#*=}"
    shift # past argument=value
    ;;
    -d=*|--destination=*)
    REPO_DESTINATION="${i#*=}"
    shift # past argument=value
    ;;
    -r=*|--rm-folders=*)
    RM_FOLDERS="${i#*=}"
    shift # past argument=value
    ;;
    -n|--dry-run)
    run=echo
    ;;
    -h=*|--help=*)
    display_usage
    ;;
    *)
    echo "Unknown argument $i"
    ;;
esac
done

if [ -z "$REPO_SOURCE" ]; then
    echo "Missing REPO_SOURCE argument.";
    display_usage
else
    echo "REPO_SOURCE          = ${REPO_SOURCE}"
fi
if [ -z "$REPO_DESTINATION" ]; then
    echo "Missing REPO_DESTINATION argument."
    display_usage
else
    echo "REPO_DESTINATION   = ${REPO_DESTINATION}"
fi
if [ -z "$FILTER_FOLDER" ]; then
    echo "Missing FILTER_FOLDER argument."
    display_usage
else
    echo "FILTER_FOLDER        = ${FILTER_FOLDER}"
fi

# Create temp folder
tmp_dir=`mktemp -d`

echo "###### Cloning in : ${tmp_dir}"
cd $tmp_dir

# Clone source repo
git clone $REPO_SOURCE netatmo

cd ./netatmo

# List all remote branches and filter using regex
if [ -z "$BRANCH_REGEX" ]; then
    echo "Keeping all branches.";
    BRANCHES=`git branch --list --remote | tr -d '[[ ]]' | sed "s/^origin\///"`
else
    echo "Filter branches with regex ${BRANCH_REGEX}"
    BRANCHES=`git branch --list --remote | egrep $BRANCH_REGEX | tr -d '[[ ]]' | sed "s/^origin\///"`
fi

# Track all branches locally
for branch in $BRANCHES; do
    $run git branch -t $branch origin/$branch
done

# Remove old origin
git remote rm origin

if [ -z "$TAG_REGEX" ]; then
    echo "Keeping all tags.";
else
    # Filter tags using inverted regex
    echo "Filter tags with regex ${TAG_REGEX}"
    TAGS=`git tag | egrep -v $TAG_REGEX`

    # For each rejected tags, delete it
    for tag in $TAGS; do
        $run git tag -d $tag
    done
fi

# Actually filter the repo
$run git filter-branch --tag-name-filter cat --prune-empty --subdirectory-filter $FILTER_FOLDER -- --all

$run git reset --hard

# Remove backup
ORIGINALS=`git for-each-ref --format="%(refname)" refs/original/`
for original in $ORIGINALS; do
    $run git update-ref -d $original
done

if [ -z "$RM_FOLDERS" ]; then
    echo "Keeping all folders.";
else
    # Filter tags using inverted regex
    echo "Filter folders : ${RM_FOLDERS}"
    $run git filter-branch --force --index-filter "git rm -r --cached --ignore-unmatch ${RM_FOLDERS}" --prune-empty --tag-name-filter cat -- --all
fi

$run git reset --hard

# Remove backup
ORIGINALS=`git for-each-ref --format="%(refname)" refs/original/`
for original in $ORIGINALS; do
    $run git update-ref -d $original
done

# Clean up the mess
$run git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
$run git reflog expire --expire=now --all
$run git gc --aggressive --prune=now

# Add new origin
$run git remote add origin $REPO_DESTINATION

# push master branch
$run git push -u origin master

# push all local branches
for branch in $BRANCHES; do
    $run git push -u origin $branch
done

# Push tags
$run git push --tags

cd $current_dir

# remove temp repository
# rm -rf $tmp_dir
