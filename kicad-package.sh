#!/bin/sh

set -e
set -x

KICAD_VERSION="5.0.2"

./kicad-clone.sh $KICAD_VERSION
./kicad-export.sh $KICAD_VERSION

rm -rf rpmbuild
mkdir -p rpmbuild/{SPECS,SOURCES}

mv ./kicad*.tar.gz ./rpmbuild/SOURCES/
cp ./kicad*.patch ./rpmbuild/SOURCES/
cp ./kicad.spec ./rpmbuild/SPECS/

rpmbuild --define "_topdir ./rpmbuild" -bs ./rpmbuild/SPECS/kicad.spec

exit 0
