#!/bin/sh

set -e
set -x

if [ -d kicad ]; then
    cd kicad
    git fetch origin
    git reset --hard origin/master
    git checkout tags/5.0.0-rc1
    cd ..
else 
    git clone https://git.launchpad.net/kicad
    cd kicad
    git checkout tags/5.0.0-rc1
    cd ..
fi

if [ -d kicad-i18n ]; then
    cd kicad-i18n
    git fetch origin
    git reset --hard origin/master
    cd ..
else
    git clone https://github.com/KiCad/kicad-i18n.git
fi

if [ -d kicad-doc ]; then
    cd kicad-doc
    git fetch origin
    git reset --hard origin/master
    cd ..
else
    git clone https://github.com/KiCad/kicad-doc.git
fi

if [ -d kicad-templates ]; then
    cd kicad-templates
    git fetch origin
    git reset --hard origin/master
    cd ..
else
    git clone https://github.com/KiCad/kicad-templates.git
fi

if [ -d kicad-symbols ]; then
    cd kicad-symbols
    git fetch origin
    git reset --hard origin/master
    cd ..
else
    git clone https://github.com/KiCad/kicad-symbols.git
fi

if [ -d kicad-footprints ]; then
    cd kicad-footprints
    git fetch origin
    git reset --hard origin/master
    cd ..
else
    git clone https://github.com/KiCad/kicad-footprints.git
fi

if [ -d kicad-packages3D ]; then
    cd kicad-packages3D
    git fetch origin
    git reset --hard origin/master
    cd ..
else
    git clone https://github.com/KiCad/kicad-packages3D.git
fi
