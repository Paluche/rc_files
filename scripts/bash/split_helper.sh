SPLIT=<PATH>/split_git.sh
SOURCE=
DEST=

mkdir $DEST.bare
cd $DEST.bare
git init --bare
cd -

bash $SPLIT -s=$SOURCE -d=$DEST.bare -f=python -t=sdlfksdlmfksmdlfkmsdlkf

git clone $DEST.bare $DEST
