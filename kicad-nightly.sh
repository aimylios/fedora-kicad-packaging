#!/bin/bash

set -e
set -x

get_current_revision()
{
    local REPOSITORY=$1
    cd $REPOSITORY
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
    cd ..
}

export_tarball()
{
    local REPOSITORY=$1
    local VERSION=$2
    local NAME=${REPOSITORY,,}
    if [ ! -f ./rpmbuild/SOURCES/$NAME-$VERSION.tar.gz ]; then
        rm -rf ./rpmbuild/SOURCES/$NAME-r*.tar.gz
        cd $REPOSITORY
        echo "Creating $NAME-$VERSION.tar.gz ..."
        git archive --format=tar.gz --prefix=$NAME-$VERSION/ HEAD > ../rpmbuild/SOURCES/$NAME-$VERSION.tar.gz
        cd ..
    fi
}

build_package()
{
    local REPOSITORY=$1
    local VERSION=$2
    local NAME=${REPOSITORY,,}
    sed s/REVISION_NUMBER/$VERSION/g $NAME.spec.template > ./rpmbuild/SPECS/$NAME.spec
    if [ ! -f ./rpmbuild/SRPMS/$NAME-$VERSION-nightly.fc27.src.rpm ]; then
        rm -rf ./rpmbuild/SRPMS/$NAME-r*.src.rpm
        ./kicad-build.sh -n $NAME -c "aimylios/kicad-nightly"
    fi
}

./kicad-clone.sh

[ -d rpmbuild ] || mkdir rpmbuild
cd rpmbuild
[ -d SPECS ] || mkdir SPECS
[ -d SOURCES ] || mkdir SOURCES
[ -d SRPMS ] || mkdir SRPMS
cd ..

KICAD_REV=$(get_current_revision kicad)
export_tarball "kicad"      $KICAD_REV
export_tarball "kicad-i18n" $KICAD_REV
export_tarball "kicad-doc"  $KICAD_REV
build_package  "kicad"      $KICAD_REV

TEMPLATES_REV=$(get_current_revision kicad-templates)
export_tarball "kicad-templates" $TEMPLATES_REV
build_package  "kicad-templates" $TEMPLATES_REV

SYMBOLS_REV=$(get_current_revision kicad-symbols)
export_tarball "kicad-symbols" $SYMBOLS_REV
build_package  "kicad-symbols" $SYMBOLS_REV

FOOTPRINTS_REV=$(get_current_revision kicad-footprints)
export_tarball "kicad-footprints" $FOOTPRINTS_REV
build_package  "kicad-footprints" $FOOTPRINTS_REV

PACKAGES3D_REV=$(get_current_revision kicad-packages3D)
export_tarball "kicad-packages3D" $PACKAGES3D_REV
build_package  "kicad-packages3D" $PACKAGES3D_REV

exit 0
