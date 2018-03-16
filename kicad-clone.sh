#!/bin/sh

set -e
set -x

KICAD_VERSION="$1"
[ -n "$KICAD_VERSION" ] || KICAD_VERSION=HEAD

clone_repository()
{
    REPOSITORY=$1
    SOURCE=$2
    if [ -d $REPOSITORY ]; then
        echo "Updating $REPOSITORY repository to $KICAD_VERSION..."
        cd $REPOSITORY
        git fetch origin
        git reset --hard origin/master
        git checkout $KICAD_VERSION
        cd ..
    else
        if [ "$SOURCE" == "launchpad" ]; then
            echo "Cloning $REPOSITORY repository from Launchpad..."
            git clone https://git.launchpad.net/$REPOSITORY
        else
            echo "Cloning $REPOSITORY repository from GitHub..."
            git clone https://github.com/KiCad/$REPOSITORY.git
        fi
        cd $REPOSITORY
        git checkout $KICAD_VERSION
        cd ..
    fi
}

clone_repository "kicad"            launchpad
clone_repository "kicad-i18n"       github
clone_repository "kicad-doc"        github
clone_repository "kicad-templates"  github
clone_repository "kicad-symbols"    github
clone_repository "kicad-footprints" github
clone_repository "kicad-packages3D" github

exit 0
