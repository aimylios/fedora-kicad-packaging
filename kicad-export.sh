#!/bin/sh

set -e
set -x

KICAD_VERSION="$1"
[ -n "$KICAD_VERSION" ] || KICAD_VERSION=HEAD

export_tarball()
{
    REPOSITORY=$1
    cd $REPOSITORY
    echo "Creating $REPOSITORY-$KICAD_VERSION.tar.gz ..."
    git archive --format=tar.gz --prefix=$REPOSITORY-$KICAD_VERSION/ $KICAD_VERSION > ../$REPOSITORY-$KICAD_VERSION.tar.gz
    cd ..
}

export_tarball "kicad"
export_tarball "kicad-i18n"
export_tarball "kicad-doc"
export_tarball "kicad-templates"
export_tarball "kicad-symbols"
export_tarball "kicad-footprints"
export_tarball "kicad-packages3D"

exit 0
